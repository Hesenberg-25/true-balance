import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math


def show_interest_calculator() -> None:
    st.header("🧮 Interest & Financial Calculator")

    tab_si, tab_ci, tab_loan, tab_tax, tab_sip = st.tabs([
        "📐 Simple Interest",
        "📈 Compound Interest",
        "🏦 Loan Amortization",
        "💼 Income Tax",
        "💹 SIP Calculator",
    ])

    with tab_si:
        _simple_interest()

    with tab_ci:
        _compound_interest()

    with tab_loan:
        _loan_amortization()

    with tab_tax:
        _income_tax()

    with tab_sip:
        _sip_calculator()


def _simple_interest() -> None:
    st.subheader("Simple Interest Calculator")
    st.markdown("**Formula:** SI = (P × R × T) / 100")

    col1, col2, col3 = st.columns(3)
    with col1:
        principal = st.number_input("Principal Amount (₹)", min_value=0.0, value=10000.0, step=1000.0, key="si_p")
    with col2:
        rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=8.0, step=0.5, key="si_r")
    with col3:
        years = st.number_input("Time Period (Years)", min_value=0.0, value=5.0, step=0.5, key="si_t")

    if st.button("Calculate Simple Interest", type="primary", key="si_calc"):
        if principal <= 0 or rate <= 0 or years <= 0:
            st.error("All values must be greater than 0.")
        else:
            si = (principal * rate * years) / 100
            total = principal + si
            col1, col2, col3 = st.columns(3)
            col1.metric("Principal", f"₹{principal:,.2f}")
            col2.metric("Interest Earned", f"₹{si:,.2f}")
            col3.metric("Total Amount", f"₹{total:,.2f}")

            fig = go.Figure(go.Pie(
                labels=["Principal", "Interest"],
                values=[principal, si],
                hole=0.5,
                marker_colors=["#4CAF50", "#2196F3"],
            ))
            fig.update_layout(title="Principal vs Interest Breakdown")
            st.plotly_chart(fig, use_container_width=True)


def _compound_interest() -> None:
    st.subheader("Compound Interest Calculator")
    st.markdown("**Formula:** A = P × (1 + r/n)^(n×t)")

    frequency_map = {"Yearly": 1, "Half-yearly": 2, "Quarterly": 4, "Monthly": 12}

    col1, col2 = st.columns(2)
    with col1:
        principal = st.number_input("Principal Amount (₹)", min_value=0.0, value=10000.0, step=1000.0, key="ci_p")
        rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=8.0, step=0.5, key="ci_r")
    with col2:
        years = st.number_input("Time Period (Years)", min_value=0.0, value=5.0, step=0.5, key="ci_t")
        frequency = st.selectbox("Compounding Frequency", list(frequency_map.keys()), key="ci_f")

    if st.button("Calculate Compound Interest", type="primary", key="ci_calc"):
        if principal <= 0 or rate <= 0 or years <= 0:
            st.error("All values must be greater than 0.")
        else:
            n = frequency_map[frequency]
            r = rate / 100
            total = principal * math.pow(1 + r / n, n * years)
            ci = total - principal

            col1, col2, col3 = st.columns(3)
            col1.metric("Principal", f"₹{principal:,.2f}")
            col2.metric("Interest Earned", f"₹{ci:,.2f}")
            col3.metric("Total Amount", f"₹{total:,.2f}")

            year_labels = list(range(1, int(years) + 1))
            growth = [principal * math.pow(1 + r / n, n * y) for y in year_labels]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=year_labels, y=growth, mode="lines+markers", name="Total Value",
                                     line=dict(color="#4CAF50", width=2)))
            fig.add_hline(y=principal, line_dash="dash", line_color="gray", annotation_text="Principal")
            fig.update_layout(
                title="Compound Growth Over Time",
                xaxis_title="Year",
                yaxis_title="Amount (₹)",
            )
            st.plotly_chart(fig, use_container_width=True)


def _loan_amortization() -> None:
    st.subheader("Loan Amortization Schedule")
    st.markdown("Calculate your EMI and see a month-by-month repayment breakdown.")

    col1, col2, col3 = st.columns(3)
    with col1:
        loan_amount = st.number_input("Loan Amount (₹)", min_value=0.0, value=500000.0, step=10000.0, key="loan_p")
    with col2:
        annual_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=10.0, step=0.5, key="loan_r")
    with col3:
        tenure = st.number_input("Tenure (Months)", min_value=1, value=60, step=6, key="loan_t")

    if st.button("Calculate EMI & Schedule", type="primary", key="loan_calc"):
        if loan_amount <= 0 or annual_rate <= 0 or tenure <= 0:
            st.error("All values must be greater than 0.")
        else:
            monthly_rate = annual_rate / (12 * 100)
            if monthly_rate == 0:
                emi = loan_amount / tenure
            else:
                emi = loan_amount * monthly_rate * math.pow(1 + monthly_rate, tenure) / (
                    math.pow(1 + monthly_rate, tenure) - 1
                )
            total_payment = emi * tenure
            total_interest = total_payment - loan_amount

            col1, col2, col3 = st.columns(3)
            col1.metric("Monthly EMI", f"₹{emi:,.2f}")
            col2.metric("Total Interest", f"₹{total_interest:,.2f}")
            col3.metric("Total Payment", f"₹{total_payment:,.2f}")

            schedule = []
            balance = loan_amount
            for month in range(1, int(tenure) + 1):
                interest_payment = balance * monthly_rate
                principal_payment = emi - interest_payment
                balance = max(balance - principal_payment, 0)
                schedule.append({
                    "Month": month,
                    "EMI (₹)": round(emi, 2),
                    "Principal (₹)": round(principal_payment, 2),
                    "Interest (₹)": round(interest_payment, 2),
                    "Balance (₹)": round(balance, 2),
                })

            schedule_df = pd.DataFrame(schedule)

            fig = go.Figure()
            fig.add_trace(go.Bar(name="Principal", x=schedule_df["Month"], y=schedule_df["Principal (₹)"],
                                 marker_color="#4CAF50"))
            fig.add_trace(go.Bar(name="Interest", x=schedule_df["Month"], y=schedule_df["Interest (₹)"],
                                 marker_color="#F44336"))
            fig.update_layout(
                barmode="stack",
                title="Monthly Principal vs Interest",
                xaxis_title="Month",
                yaxis_title="Amount (₹)",
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📋 Full Amortization Schedule"):
                st.dataframe(
                    schedule_df.style.format({
                        "EMI (₹)": "₹{:,.2f}",
                        "Principal (₹)": "₹{:,.2f}",
                        "Interest (₹)": "₹{:,.2f}",
                        "Balance (₹)": "₹{:,.2f}",
                    }),
                    use_container_width=True,
                    hide_index=True,
                )


def _income_tax() -> None:
    st.subheader("Income Tax Calculator (India)")
    st.markdown("Uses the **new tax regime** with a standard deduction of ₹75,000.")

    annual_salary = st.number_input(
        "Annual Salary (₹)", min_value=0.0, value=800000.0, step=50000.0, key="tax_sal"
    )

    if st.button("Calculate Tax", type="primary", key="tax_calc"):
        standard_deduction = 75000
        taxable_income = max(annual_salary - standard_deduction, 0)

        slabs = [
            (300000, 0.00),
            (300000, 0.05),
            (300000, 0.10),
            (300000, 0.15),
            (300000, 0.20),
            (float("inf"), 0.30),
        ]

        total_tax = 0.0
        slab_breakdown = []
        remaining = taxable_income
        slab_limits = [300000, 600000, 900000, 1200000, 1500000, float("inf")]
        slab_labels = ["0–3L (0%)", "3–6L (5%)", "6–9L (10%)", "9–12L (15%)", "12–15L (20%)", "Above 15L (30%)"]

        for i, (limit, rate_frac) in enumerate(slabs):
            if remaining <= 0:
                break
            taxable_in_slab = min(remaining, limit)
            tax_in_slab = taxable_in_slab * rate_frac
            total_tax += tax_in_slab
            slab_breakdown.append({
                "Slab": slab_labels[i],
                "Income in Slab (₹)": taxable_in_slab,
                "Tax Rate": f"{int(rate_frac * 100)}%",
                "Tax (₹)": tax_in_slab,
            })
            remaining -= taxable_in_slab

        net_income = annual_salary - total_tax
        effective_rate = (total_tax / annual_salary * 100) if annual_salary > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Gross Salary", f"₹{annual_salary:,.2f}")
        col2.metric("Taxable Income", f"₹{taxable_income:,.2f}")
        col3.metric("Total Tax", f"₹{total_tax:,.2f}")
        col4.metric("Net Income", f"₹{net_income:,.2f}")
        st.caption(f"Effective Tax Rate: {effective_rate:.2f}%")

        breakdown_df = pd.DataFrame(slab_breakdown)
        st.dataframe(
            breakdown_df.style.format({"Income in Slab (₹)": "₹{:,.2f}", "Tax (₹)": "₹{:,.2f}"}),
            use_container_width=True,
            hide_index=True,
        )

        fig = go.Figure(go.Pie(
            labels=["Net Income", "Tax"],
            values=[net_income, total_tax],
            hole=0.5,
            marker_colors=["#4CAF50", "#F44336"],
        ))
        fig.update_layout(title="Net Income vs Tax")
        st.plotly_chart(fig, use_container_width=True)


def _sip_calculator() -> None:
    st.subheader("SIP (Systematic Investment Plan) Calculator")
    st.markdown("Calculate the future value of your monthly SIP investments.")

    col1, col2, col3 = st.columns(3)
    with col1:
        monthly_investment = st.number_input(
            "Monthly Investment (₹)", min_value=0.0, value=5000.0, step=500.0, key="sip_m"
        )
    with col2:
        annual_rate = st.number_input(
            "Expected Annual Return (%)", min_value=0.0, value=12.0, step=0.5, key="sip_r"
        )
    with col3:
        duration_years = st.number_input("Duration (Years)", min_value=1, value=10, step=1, key="sip_y")

    if st.button("Calculate SIP Returns", type="primary", key="sip_calc"):
        if monthly_investment <= 0 or annual_rate <= 0 or duration_years <= 0:
            st.error("All values must be greater than 0.")
        else:
            monthly_rate = annual_rate / (12 * 100)
            n = int(duration_years * 12)
            future_value = monthly_investment * ((math.pow(1 + monthly_rate, n) - 1) / monthly_rate) * (
                1 + monthly_rate
            )
            total_invested = monthly_investment * n
            wealth_gained = future_value - total_invested

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Invested", f"₹{total_invested:,.2f}")
            col2.metric("Wealth Gained", f"₹{wealth_gained:,.2f}")
            col3.metric("Future Value", f"₹{future_value:,.2f}")

            years_list = list(range(1, int(duration_years) + 1))
            invested_vals = []
            fv_vals = []
            for y in years_list:
                n_y = y * 12
                fv_y = monthly_investment * ((math.pow(1 + monthly_rate, n_y) - 1) / monthly_rate) * (
                    1 + monthly_rate
                )
                invested_vals.append(monthly_investment * n_y)
                fv_vals.append(fv_y)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years_list, y=fv_vals, name="Portfolio Value",
                                     fill="tozeroy", line=dict(color="#4CAF50")))
            fig.add_trace(go.Scatter(x=years_list, y=invested_vals, name="Amount Invested",
                                     fill="tozeroy", line=dict(color="#2196F3", dash="dash")))
            fig.update_layout(
                title="SIP Growth Over Time",
                xaxis_title="Year",
                yaxis_title="Amount (₹)",
            )
            st.plotly_chart(fig, use_container_width=True)

            fig2 = go.Figure(go.Pie(
                labels=["Amount Invested", "Wealth Gained"],
                values=[total_invested, wealth_gained],
                hole=0.5,
                marker_colors=["#2196F3", "#4CAF50"],
            ))
            fig2.update_layout(title="Investment vs Returns Breakdown")
            st.plotly_chart(fig2, use_container_width=True)
