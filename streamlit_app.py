import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import date

from expense_tracker import show_expense_tracker, load_expenses, MONTHS, CATEGORIES
from budget_tracker import show_budget_tracker, load_budgets
from interest_calculator import show_interest_calculator

st.set_page_config(
    page_title="True Balance — Financial Tracker",
    page_icon="💴",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def show_dashboard() -> None:
    st.header("Dashboard")
    st.markdown("Welcome to **True Balance** — your Personal Financial Companion.")

    expenses_df = load_expenses()
    budgets_df = load_budgets()

    if not expenses_df.empty:
        expenses_df["Amount"] = pd.to_numeric(expenses_df["Amount"], errors="coerce")

    if not budgets_df.empty:
        budgets_df["Budget"] = pd.to_numeric(budgets_df["Budget"], errors="coerce")

    total_expenses = expenses_df["Amount"].sum() if not expenses_df.empty else 0
    total_budget = budgets_df["Budget"].sum() if not budgets_df.empty else 0
    num_entries = len(expenses_df) if not expenses_df.empty else 0
    remaining = total_budget - total_expenses

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Expenses", f"₹{total_expenses:,.2f}")
    col2.metric("Total Budget", f"₹{total_budget:,.2f}")
    col3.metric("Remaining Budget", f"₹{remaining:,.2f}", delta=f"₹{remaining:,.2f}")
    col4.metric("Expense Entries", num_entries)

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Expenses by Category")
        if not expenses_df.empty:
            cat_totals = expenses_df.groupby("Category")["Amount"].sum().reset_index()
            fig = px.pie(
                cat_totals,
                values="Amount",
                names="Category",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data yet. Start by adding some expenses!")

    with col_right:
        st.subheader("Monthly Spending Trend")
        if not expenses_df.empty:
            month_order = {m: i for i, m in enumerate(MONTHS)}
            month_totals = expenses_df.groupby("Month")["Amount"].sum().reset_index()
            month_totals["order"] = month_totals["Month"].map(month_order)
            month_totals = month_totals.sort_values("order")
            fig = px.bar(
                month_totals,
                x="Month",
                y="Amount",
                color="Amount",
                color_continuous_scale="Blues",
                text_auto=".2s",
            )
            fig.update_layout(margin=dict(t=20, b=20), xaxis_title="Month", yaxis_title="₹")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly data yet.")

    if not expenses_df.empty and not budgets_df.empty:
        st.subheader("Budget vs Actual")
        actual_by_month = expenses_df.groupby("Month")["Amount"].sum().reset_index()
        actual_by_month.columns = ["Month", "Actual"]
        comparison = budgets_df.merge(actual_by_month, on="Month", how="left").fillna(0)
        month_order = {m: i for i, m in enumerate(MONTHS)}
        comparison["order"] = comparison["Month"].map(month_order)
        comparison = comparison.sort_values("order")
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Budget", x=comparison["Month"], y=comparison["Budget"],
                             marker_color="steelblue"))
        fig.add_trace(go.Bar(name="Actual", x=comparison["Month"], y=comparison["Actual"],
                             marker_color="coral"))
        fig.update_layout(barmode="group", xaxis_title="Month", yaxis_title="Amount (₹)",
                          margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    if not expenses_df.empty:
        st.subheader("Recent Transactions")
        recent = expenses_df.tail(10).iloc[::-1].copy()
        recent["Amount"] = recent["Amount"].apply(lambda x: f"₹{x:,.2f}")
        st.dataframe(recent, use_container_width=True, hide_index=True)


def main() -> None:
    with st.sidebar:
        st.title("True Balance")
        st.markdown("**Your Personal Financial Tracker**")
        st.divider()

        page = st.radio(
            "Navigate",
            ["Dashboard", "Expense Tracker", "Budget Tracker", "Interest Calculator"],
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("### Quick Add Expense")
        with st.form("sidebar_quick_add", clear_on_submit=True):
            quick_category = st.selectbox("Category", CATEGORIES, key="quick_cat")
            quick_amount = st.number_input("Amount (₹)", min_value=0.01, step=10.0, key="quick_amt")
            quick_month = st.selectbox("Month", MONTHS, index=date.today().month - 1, key="quick_month")
            add_btn = st.form_submit_button("Add", use_container_width=True)
            if add_btn:
                if quick_amount > 0:
                    from expense_tracker import save_expense
                    save_expense(str(date.today()), quick_month, quick_category, quick_amount)
                    st.success(f"Added ₹{quick_amount:,.2f}")
                    st.rerun()
                else:
                    st.error("Amount must be > 0")

        st.divider()

    if page == "Dashboard":
        show_dashboard()
    elif page == "Expense Tracker":
        show_expense_tracker()
    elif page == "Budget Tracker":
        show_budget_tracker()
    elif page == "Interest Calculator":
        show_interest_calculator()


if __name__ == "__main__":
    main()
