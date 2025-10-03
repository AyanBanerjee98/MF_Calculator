import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from calculations import MutualFundCalculator
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Mutual Fund Calculator",
    page_icon="💰",
    layout="wide"
)

# Initialize calculator
calc = MutualFundCalculator()

# Main title
st.title("🏦 Mutual Fund Investment Calculator")
st.markdown("---")

# Sidebar for calculator selection
st.sidebar.title("Select Calculator")
calculator_type = st.sidebar.selectbox(
    "Choose Calculator Type:",
    ["One Time Investment", "SIP Calculator", "SWP Calculator"]
)

st.sidebar.markdown("---")

# Optional Settings
with st.sidebar.expander("Optional: Adjust Inflation & CAGR"):
    enable_inflation = st.checkbox("Enable Inflation Adjustment", value=False)
    inflation_rate = st.number_input("Inflation rate (% per year)", min_value=0.0, max_value=20.0, value=6.0, step=0.25, disabled=not enable_inflation)

with st.sidebar.expander("Optional: Step-up Investment/Withdrawal", expanded=False):
    enable_increase = st.checkbox("Enable step-up / periodic increase", value=False)
    increase_frequency = st.selectbox("Increase frequency", ["Yearly", "Every 3 years", "Every 5 years"], index=0, disabled=not enable_increase)

    # Different controls for SIP/SWP vs One-time
    if calculator_type == "SIP Calculator":
        increase_percentage = st.number_input("Increase SIP by (%) when frequency triggers", min_value=0.0, max_value=200.0, value=10.0, step=1.0, disabled=not enable_increase)
        increase_amount = None
    elif calculator_type == "SWP Calculator":
        increase_percentage = st.number_input("Increase Withdrawal by (%) when frequency triggers", min_value=0.0, max_value=200.0, value=10.0, step=1.0, disabled=not enable_increase)
        increase_amount = None
    else:  # One-time
        increase_percentage = None
        increase_amount = st.number_input("Additional one-time contribution (₹) when frequency triggers", min_value=0, max_value=1_00_00_000, value=50000, step=1_000, disabled=not enable_increase)

# Helper functions
def pretty_num(n):
    """Format number as currency"""
    return f"₹{int(n):,}"

def create_growth_chart(df, y_cols, title):
    """Create interactive growth chart"""
    fig = go.Figure()
    for col in y_cols:
        if col in df.columns and df[col].notna().any():
            fig.add_trace(go.Scatter(
                x=df['Year'], 
                y=df[col], 
                mode='lines+markers', 
                name=col,
                line=dict(width=3)
            ))

    fig.update_layout(
        title=title,
        xaxis_title='Year',
        yaxis_title='Amount (₹)',
        template='plotly_white',
        legend=dict(orientation='h', yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500
    )
    return fig

def investment_summary_block(df, calculator_type):
    """Display investment summary for the final year"""
    summary_row = df.iloc[-1]
    year = int(summary_row['Year'])

    st.subheader(f"📊 Investment Summary for {year}")

    col1, col2, col3, col4 = st.columns(4)

    if calculator_type == "One Time Investment":
        final_amount = summary_row.get('Final Amount', 0)
        total_principal = summary_row.get('Total Principal', 0)
        interest_earned = summary_row.get('Interest Earned', 0)
        interest_percent = summary_row.get('Interest Percent', 0)

        with col1:
            st.metric("Final Amount", pretty_num(final_amount))
        with col2:
            st.metric("Total Principal", pretty_num(total_principal))
        with col3:
            st.metric("Interest Earned", pretty_num(interest_earned))
        with col4:
            st.metric("Interest %", f"{interest_percent:.1f}%")

    elif calculator_type == "SIP Calculator":
        final_amount = summary_row.get('Final Amount', 0)
        total_invested = summary_row.get('Total Invested', 0)
        gains = summary_row.get('Gains', 0)
        gains_percent = summary_row.get('Gains Percent', 0)

        with col1:
            st.metric("Final Amount", pretty_num(final_amount))
        with col2:
            st.metric("Total Invested", pretty_num(total_invested))
        with col3:
            st.metric("Total Gains", pretty_num(gains))
        with col4:
            st.metric("Gains %", f"{gains_percent:.1f}%")

    else:  # SWP Calculator
        remaining_balance = summary_row.get('Remaining Balance', 0)
        total_withdrawn = summary_row.get('Total Withdrawn', 0)
        monthly_withdrawal = summary_row.get('Monthly Withdrawal', 0)

        with col1:
            st.metric("Remaining Balance", pretty_num(remaining_balance))
        with col2:
            st.metric("Total Withdrawn", pretty_num(total_withdrawn))
        with col3:
            st.metric("Monthly Withdrawal", pretty_num(monthly_withdrawal))
        with col4:
            st.metric("Years Completed", f"{len(df)}")

    # Real value if inflation is considered and enabled
    if enable_inflation:
        if 'Real Value (Inflation Adjusted)' in summary_row and pd.notnull(summary_row['Real Value (Inflation Adjusted)']):
            st.info(f"💡 **Real Value (Inflation Adjusted):** {pretty_num(summary_row['Real Value (Inflation Adjusted)'])}")
        elif 'Real Balance (Inflation Adjusted)' in summary_row and pd.notnull(summary_row['Real Balance (Inflation Adjusted)']):
            st.info(f"💡 **Real Balance (Inflation Adjusted):** {pretty_num(summary_row['Real Balance (Inflation Adjusted)'])}")

    st.markdown("---")


# Main calculator sections
if calculator_type == "One Time Investment":
    st.subheader("💰 One Time Investment Calculator")

    col1, col2, col3 = st.columns(3)
    with col1:
        principal = st.number_input("Initial Investment (₹)", min_value=0, value=100000, step=5000)
    with col2:
        rate = st.number_input("Expected Return Rate (% p.a.)", min_value=0.0, max_value=30.0, value=12.0, step=0.25)
    with col3:
        years = st.number_input("Investment Duration (years)", min_value=1, max_value=60, value=15, step=1)

    if st.button("Calculate", type="primary", use_container_width=True):
        # Calculate with new parameters
        df = calc.one_time_investment(
            principal=int(principal), 
            rate=float(rate), 
            years=int(years),
            inflation_rate=float(inflation_rate),
            enable_increase=bool(enable_increase),
            increase_frequency=increase_frequency,
            increase_amount=float(increase_amount) if increase_amount is not None else 0.0
        )

        # 1. Display summary
        investment_summary_block(df, calculator_type)

        # 2. Display growth chart
        chart_cols = ["Final Amount", "Total Principal"]
        if enable_inflation and inflation_rate > 0:
            chart_cols.append("Real Value (Inflation Adjusted)")

        st.plotly_chart(
            create_growth_chart(
                df, 
                chart_cols, 
                "One-time Investment Growth Over Time"
            ), 
            use_container_width=True
        )

        # 3. Display data table
        st.subheader("📈 Year-wise Growth Details")
        # Remove the index column for cleaner display
        df_display = df.copy()
        if not enable_inflation:
            df_display = df_display.drop(columns=["Real Value (Inflation Adjusted)"], errors="ignore")
        st.dataframe(df_display, use_container_width=True, hide_index=True)


elif calculator_type == "SIP Calculator":
    st.subheader("📈 SIP (Systematic Investment Plan) Calculator")

    col1, col2, col3 = st.columns(3)
    with col1:
        monthly_investment = st.number_input("Monthly SIP (₹)", min_value=0, value=10000, step=500)
    with col2:
        rate = st.number_input("Expected Return Rate (% p.a.)", min_value=0.0, max_value=30.0, value=12.0, step=0.25)
    with col3:
        years = st.number_input("Investment Duration (years)", min_value=1, max_value=60, value=15, step=1)

    if st.button("Calculate", type="primary", use_container_width=True):
        # Calculate with new parameters
        df = calc.sip_calculator(
            monthly_investment=int(monthly_investment), 
            rate=float(rate), 
            years=int(years),
            inflation_rate=float(inflation_rate),
            enable_increase=bool(enable_increase),
            increase_frequency=increase_frequency,
            increase_percentage=float(increase_percentage) if increase_percentage is not None else 0.0
        )

        # 1. Display summary
        investment_summary_block(df, calculator_type)

        # 2. Display growth chart
        chart_cols = ["Final Amount", "Total Invested"]
        if enable_inflation and inflation_rate > 0:
            chart_cols.append("Real Value (Inflation Adjusted)")

        st.plotly_chart(
            create_growth_chart(
                df, 
                chart_cols, 
                "SIP Growth Over Time"
            ), 
            use_container_width=True
        )

        # 3. Display data table
        st.subheader("📈 Year-wise SIP Growth Details")
        # Remove the index column for cleaner display
        df_display = df.copy()
        st.dataframe(df_display, use_container_width=True, hide_index=True)


elif calculator_type == "SWP Calculator":
    st.subheader("💸 SWP (Systematic Withdrawal Plan) Calculator")

    col1, col2, col3 = st.columns(3)
    with col1:
        initial_amount = st.number_input("Initial Corpus (₹)", min_value=0, value=1000000, step=10000)
    with col2:
        withdrawal_amount = st.number_input("Monthly Withdrawal (₹)", min_value=0, value=10000, step=500)
    with col3:
        rate = st.number_input("Expected Return Rate (% p.a.)", min_value=0.0, max_value=30.0, value=12.0, step=0.25)
    with col1:
        years = st.number_input("Duration (years)", min_value=1, max_value=60, value=10, step=1)

    if st.button("Calculate", type="primary", use_container_width=True):
        # Calculate with new parameters
        df = calc.swp_calculator(
            initial_amount=int(initial_amount), 
            withdrawal_amount=int(withdrawal_amount),
            rate=float(rate), 
            years=int(years), 
            inflation_rate=float(inflation_rate),
            enable_increase=bool(enable_increase),
            increase_frequency=increase_frequency,
            increase_percentage=float(increase_percentage) if increase_percentage is not None else 0.0
        )

        # 1. Display summary
        investment_summary_block(df, calculator_type)

        # 2. Display growth chart
        chart_cols = ["Remaining Balance", "Total Withdrawn"]
        if enable_inflation and inflation_rate > 0:
            chart_cols.append("Real Balance (Inflation Adjusted)")

        st.plotly_chart(
            create_growth_chart(
                df, 
                chart_cols, 
                "SWP Balance Over Time"
            ), 
            use_container_width=True
        )

        # 3. Display data table
        st.subheader("📈 Year-wise SWP Details")
        # Remove the index column for cleaner display
        df_display = df.copy()
        st.dataframe(df_display, use_container_width=True, hide_index=True)


# Footer
st.markdown("---")
st.markdown("""
📝 **Note:** 
- Step-up increases for SIP/SWP apply at the start of the triggered year and compound thereafter
- One-time additional contributions are added at the start of triggered years
- All calculations assume monthly compounding for SIP/SWP
- Inflation adjustment shows the real purchasing power of your investments
- For "Every 3 years" frequency: increases happen in years 3, 6, 9, etc.
- For "Every 5 years" frequency: increases happen in years 5, 10, 15, etc.
""")