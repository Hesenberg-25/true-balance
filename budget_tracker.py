import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

BUDGET_FILE = "Budget.csv"
EXPENSES_FILE = "Expenses.csv"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_budgets() -> pd.DataFrame:
    if os.path.exists(BUDGET_FILE):
        df = pd.read_csv(BUDGET_FILE)
        if not df.empty:
            return df
    return pd.DataFrame(columns=["Month", "Budget"])


def load_expenses() -> pd.DataFrame:
    if os.path.exists(EXPENSES_FILE):
        df = pd.read_csv(EXPENSES_FILE)
        if not df.empty:
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
            return df
    return pd.DataFrame(columns=["Date", "Month", "Category", "Amount"])


def save_budget(month: str, budget: float) -> None:
    df = load_budgets()
    df["Budget"] = pd.to_numeric(df["Budget"], errors="coerce")
    if month in df["Month"].values:
        df.loc[df["Month"] == month, "Budget"] = budget
    else:
        new_row = pd.DataFrame([{"Month": month, "Budget": budget}])
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(BUDGET_FILE, index=False)


def show_budget_tracker() -> None:
    st.header("💰 Budget Tracker")

    tab_set, tab_compare, tab_overview = st.tabs(["🎯 Set Budget", "📊 Budget vs Actual", "🗂️ Overview"])

    with tab_set:
        _set_budget_form()

    with tab_compare:
        _compare_budget_vs_actual()

    with tab_overview:
        _budget_overview()


def _set_budget_form() -> None:
    st.subheader("Set Monthly Budget")
    budgets = load_budgets()

    with st.form("set_budget_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            month = st.selectbox("Month", MONTHS)
        with col2:
            existing = 0.0
            if not budgets.empty and month in budgets["Month"].values:
                val = budgets.loc[budgets["Month"] == month, "Budget"].values[0]
                existing = float(val) if pd.notna(val) else 0.0
            budget_amount = st.number_input(
                "Budget Amount (₹)",
                min_value=0.01,
                value=existing if existing > 0 else 1000.0,
                step=100.0,
                format="%.2f",
            )

        submitted = st.form_submit_button("Save Budget", use_container_width=True, type="primary")
        if submitted:
            if budget_amount <= 0:
                st.error("Budget must be greater than 0.")
            else:
                save_budget(month, budget_amount)
                st.success(f"✅ Budget for {month} set to ₹{budget_amount:,.2f}")
                st.rerun()

    if not budgets.empty:
        st.subheader("Current Budgets")
        budgets["Budget"] = pd.to_numeric(budgets["Budget"], errors="coerce")
        st.dataframe(
            budgets.style.format({"Budget": "₹{:,.2f}"}),
            use_container_width=True,
            hide_index=True,
        )


def _compare_budget_vs_actual() -> None:
    st.subheader("Budget vs Actual Spending")
    budgets = load_budgets()
    expenses = load_expenses()

    if budgets.empty:
        st.info("No budgets set yet. Go to 'Set Budget' to add budgets.")
        return

    budgets["Budget"] = pd.to_numeric(budgets["Budget"], errors="coerce")

    if not expenses.empty:
        actual_by_month = expenses.groupby("Month")["Amount"].sum().reset_index()
        actual_by_month.columns = ["Month", "Actual"]
    else:
        actual_by_month = pd.DataFrame(columns=["Month", "Actual"])

    comparison = budgets.merge(actual_by_month, on="Month", how="left").fillna(0)
    comparison["Utilization (%)"] = (comparison["Actual"] / comparison["Budget"] * 100).round(1)
    comparison["Status"] = comparison["Utilization (%)"].apply(_status_label)

    month_order = {m: i for i, m in enumerate(MONTHS)}
    comparison["order"] = comparison["Month"].map(month_order)
    comparison = comparison.sort_values("order").drop(columns="order")

    for _, row in comparison.iterrows():
        util = row["Utilization (%)"]
        budget = row["Budget"]
        actual = row["Actual"]
        month = row["Month"]

        with st.expander(f"**{month}** — Budget: ₹{budget:,.0f} | Spent: ₹{actual:,.0f} | {util:.1f}%"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Budget", f"₹{budget:,.2f}")
            col2.metric("Actual", f"₹{actual:,.2f}")
            remaining = budget - actual
            col3.metric("Remaining", f"₹{remaining:,.2f}", delta=f"{remaining:,.2f}")

            color = "green" if util <= 80 else ("orange" if util <= 100 else "red")
            st.progress(min(util / 100, 1.0), text=f"{util:.1f}% used")
            if util > 100:
                st.error(f"⚠️ Over budget by ₹{abs(remaining):,.2f}!")
            elif util > 80:
                st.warning(f"⚠️ {100 - util:.1f}% of budget remaining for {month}.")
            else:
                st.success(f"✅ On track! ₹{remaining:,.2f} remaining.")

    st.subheader("Comparison Chart")
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Budget", x=comparison["Month"], y=comparison["Budget"], marker_color="steelblue"))
    fig.add_trace(go.Bar(name="Actual", x=comparison["Month"], y=comparison["Actual"], marker_color="coral"))
    fig.update_layout(
        barmode="group",
        title="Budget vs Actual by Month",
        xaxis_title="Month",
        yaxis_title="Amount (₹)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)


def _budget_overview() -> None:
    st.subheader("Budget Overview")
    budgets = load_budgets()
    expenses = load_expenses()

    if budgets.empty:
        st.info("No budgets set. Add budgets to see the overview.")
        return

    budgets["Budget"] = pd.to_numeric(budgets["Budget"], errors="coerce")

    if not expenses.empty:
        actual_by_month = expenses.groupby("Month")["Amount"].sum().reset_index()
        actual_by_month.columns = ["Month", "Actual"]
    else:
        actual_by_month = pd.DataFrame(columns=["Month", "Actual"])

    comparison = budgets.merge(actual_by_month, on="Month", how="left").fillna(0)
    comparison["Remaining"] = comparison["Budget"] - comparison["Actual"]
    comparison["Utilization (%)"] = (comparison["Actual"] / comparison["Budget"] * 100).round(1)
    comparison["Status"] = comparison["Utilization (%)"].apply(_status_label)

    total_budget = comparison["Budget"].sum()
    total_actual = comparison["Actual"].sum()
    total_remaining = comparison["Remaining"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Budget", f"₹{total_budget:,.2f}")
    col2.metric("Total Spent", f"₹{total_actual:,.2f}")
    col3.metric("Total Remaining", f"₹{total_remaining:,.2f}")

    st.dataframe(
        comparison[["Month", "Budget", "Actual", "Remaining", "Utilization (%)", "Status"]].style.format(
            {"Budget": "₹{:,.2f}", "Actual": "₹{:,.2f}", "Remaining": "₹{:,.2f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )

    fig = px.bar(
        comparison,
        x="Month",
        y="Utilization (%)",
        title="Budget Utilization by Month (%)",
        color="Utilization (%)",
        color_continuous_scale=["green", "yellow", "red"],
        range_color=[0, 120],
        text_auto=".1f",
    )
    fig.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="100% Budget")
    fig.add_hline(y=80, line_dash="dot", line_color="orange", annotation_text="80% Warning")
    st.plotly_chart(fig, use_container_width=True)


def _status_label(util: float) -> str:
    if util > 100:
        return "🔴 Over Budget"
    elif util > 80:
        return "🟡 Warning"
    else:
        return "🟢 On Track"
