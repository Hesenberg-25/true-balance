import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import os

EXPENSES_FILE = "Expenses.csv"
CATEGORIES = ["Food", "Transport", "Household", "Education", "Health", "Utilities", "Other"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_expenses() -> pd.DataFrame:
    if os.path.exists(EXPENSES_FILE):
        df = pd.read_csv(EXPENSES_FILE)
        if df.empty:
            return _empty_df()
        return df
    return _empty_df()


def _empty_df() -> pd.DataFrame:
    return pd.DataFrame(columns=["Date", "Month", "Category", "Amount"])


def save_expense(expense_date: str, month: str, category: str, amount: float) -> None:
    df = load_expenses()
    new_row = pd.DataFrame([{"Date": expense_date, "Month": month, "Category": category, "Amount": amount}])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(EXPENSES_FILE, index=False)


def show_expense_tracker() -> None:
    st.header("📊 Expense Tracker")

    tab_add, tab_view, tab_charts = st.tabs(["➕ Add Expense", "📋 View Expenses", "📈 Charts & Analytics"])

    with tab_add:
        _add_expense_form()

    with tab_view:
        _view_expenses()

    with tab_charts:
        _show_charts()


def _add_expense_form() -> None:
    st.subheader("Add New Expense")
    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            expense_date = st.date_input("Date", value=date.today())
            category = st.selectbox("Category", CATEGORIES)
        with col2:
            month = st.selectbox("Month", MONTHS, index=date.today().month - 1)
            amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01, format="%.2f")

        submitted = st.form_submit_button("Add Expense", use_container_width=True, type="primary")
        if submitted:
            if amount <= 0:
                st.error("Amount must be greater than 0.")
            else:
                save_expense(str(expense_date), month, category, amount)
                st.success(f"✅ Expense of ₹{amount:,.2f} added under '{category}' for {month}.")
                st.rerun()


def _view_expenses() -> None:
    st.subheader("View Expenses")
    df = load_expenses()

    if df.empty:
        st.info("No expenses recorded yet. Add some expenses to get started!")
        return

    col1, col2 = st.columns(2)
    with col1:
        filter_month = st.selectbox("Filter by Month", ["All"] + MONTHS, key="view_month")
    with col2:
        filter_category = st.selectbox("Filter by Category", ["All"] + CATEGORIES, key="view_category")

    filtered = df.copy()
    if filter_month != "All":
        filtered = filtered[filtered["Month"] == filter_month]
    if filter_category != "All":
        filtered = filtered[filtered["Category"] == filter_category]

    if filtered.empty:
        st.warning("No expenses match the selected filters.")
        return

    filtered["Amount"] = pd.to_numeric(filtered["Amount"], errors="coerce")
    total = filtered["Amount"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Expenses", f"₹{total:,.2f}")
    col2.metric("Number of Entries", len(filtered))
    col3.metric("Average Expense", f"₹{total / len(filtered):,.2f}")

    st.dataframe(
        filtered.style.format({"Amount": "₹{:,.2f}"}),
        use_container_width=True,
        hide_index=True,
    )


def _show_charts() -> None:
    st.subheader("Charts & Analytics")
    df = load_expenses()

    if df.empty:
        st.info("No expenses recorded yet. Add some expenses to see charts!")
        return

    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    col1, col2 = st.columns(2)

    with col1:
        category_totals = df.groupby("Category")["Amount"].sum().reset_index()
        fig_pie = px.pie(
            category_totals,
            values="Amount",
            names="Category",
            title="Expenses by Category",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        month_order = {m: i for i, m in enumerate(MONTHS)}
        month_totals = df.groupby("Month")["Amount"].sum().reset_index()
        month_totals["order"] = month_totals["Month"].map(month_order)
        month_totals = month_totals.sort_values("order")
        fig_bar = px.bar(
            month_totals,
            x="Month",
            y="Amount",
            title="Monthly Expense Trend",
            color="Amount",
            color_continuous_scale="Blues",
            text_auto=".2s",
        )
        fig_bar.update_layout(xaxis_title="Month", yaxis_title="Amount (₹)")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Category vs Month Heatmap")
    pivot = df.pivot_table(values="Amount", index="Category", columns="Month", aggfunc="sum", fill_value=0)
    existing_months = [m for m in MONTHS if m in pivot.columns]
    pivot = pivot[existing_months]
    fig_heat = px.imshow(
        pivot,
        title="Spending Heatmap (Category × Month)",
        color_continuous_scale="YlOrRd",
        aspect="auto",
        text_auto=".0f",
    )
    fig_heat.update_layout(xaxis_title="Month", yaxis_title="Category")
    st.plotly_chart(fig_heat, use_container_width=True)
