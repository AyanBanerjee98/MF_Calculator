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


def create_growth_chart_with_investment(df, amount_column, invested_column, title):
    """Create interactive growth chart with invested amount tracking"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Main growth line
    fig.add_trace(
        go.Scatter(
            x=df['Year'],
            y=df[amount_column],
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8),
            hovertemplate='<b>Year:</b> %{x}<br><b>Portfolio Value:</b> ₹%{y:,.0f}<extra></extra>'
        ),
        secondary_y=False,
    )

    # Invested amount line (only for SIP)
    if invested_column in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['Year'],
                y=df[invested_column],
                mode='lines+markers',
                name='Total Invested',
                line=dict(color='#ff7f0e', width=3, dash='dot'),
                marker=dict(size=6),
                hovertemplate='<b>Year:</b> %{x}<br><b>Total Invested:</b> ₹%{y:,.0f}<extra></extra>'
            ),
            secondary_y=False,
        )

    # Inflation adjusted line if available
    if 'Real Value (Inflation Adjusted)' in df.columns and df['Real Value (Inflation Adjusted)'].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df['Year'],
                y=df['Real Value (Inflation Adjusted)'],
                mode='lines+markers',
                name='Inflation Adjusted Value',
                line=dict(color='#2ca02c', width=2, dash='dash'),
                marker=dict(size=6),
                hovertemplate='<b>Year:</b> %{x}<br><b>Real Value:</b> ₹%{y:,.0f}<extra></extra>'
            ),
            secondary_y=False,
        )

    fig.update_layout(
        title=title,
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="Amount (₹)", secondary_y=False)

    return fig

def create_pie_chart(invested, gains, title):
    """Create interactive pie chart for investment breakdown"""
    labels = ['Principal/Invested Amount', 'Gains/Returns']
    values = [invested, gains]
    colors = ['#ff9999', '#66b3ff']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,  # Increased hole size for a donut-style chart
        marker=dict(colors=colors, line=dict(color='white', width=2)),  # Add border for better contrast
        textinfo='label+percent',
        texttemplate='<b>%{label}</b><br>₹%{value:,.0f}<br>(%{percent})',
        hovertemplate='<b>%{label}</b><br>Amount: ₹%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color='#333'),
            x=0.5,  # Center the title
        ),
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,  # Adjusted position for better spacing
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        )
    )

    return fig

def create_swp_pie_chart(remaining, withdrawn, title):
    """Create pie chart for SWP showing remaining vs withdrawn"""
    labels = ['Remaining Balance', 'Total Withdrawn']
    values = [remaining, withdrawn]
    colors = ['#90EE90', '#FFB6C1']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,  # Increased hole size for a donut-style chart
        marker=dict(colors=colors, line=dict(color='white', width=2)),  # Add border for better contrast
        textinfo='label+percent',
        texttemplate='<b>%{label}</b><br>₹%{value:,.0f}<br>(%{percent})',
        hovertemplate='<b>%{label}</b><br>Amount: ₹%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color='#333'),
            x=0.5,  # Center the title
        ),
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,  # Adjusted position for better spacing
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        )
    )

    return fig

def format_currency(amount):
    """Format currency in Indian format"""
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount:,.0f}"
    
# Inflation adjustment option
st.sidebar.markdown("### Optional Settings")
use_inflation = st.sidebar.checkbox("Apply Inflation Adjustment")
inflation_rate = 0
if use_inflation:
    inflation_rate = st.sidebar.slider("Inflation Rate (%)", 0.0, 15.0, 6.0, 0.1)

st.sidebar.markdown("---")

# One Time Investment Calculator
if calculator_type == "One Time Investment":
    # Sidebar inputs
    st.sidebar.markdown("### 💵 Input Parameters")
    principal = st.sidebar.number_input("Initial Investment (₹)", min_value=1000, value=100000, step=1000)
    rate = st.sidebar.slider("Expected Annual Return (%)", 1.0, 30.0, 12.0, 0.1)
    years = st.sidebar.slider("Investment Period (Years)", 1, 30, 10)

    calculate_button = st.sidebar.button("Calculate", type="primary", use_container_width=True)

    # Main content area
    st.header("💵 One Time Investment Calculator")

    if calculate_button:
        st.session_state.oti_calculated = True
        st.session_state.oti_results = calc.one_time_investment(principal, rate, years, inflation_rate)
        st.session_state.oti_principal = principal

    if hasattr(st.session_state, 'oti_calculated') and st.session_state.oti_calculated:
        results = st.session_state.oti_results
        principal = st.session_state.oti_principal

        # Summary metrics
        final_amount = results.iloc[-1]['Final Amount']
        total_gains = final_amount - principal
        cagr = calc.calculate_cagr(principal, final_amount, years)

        col2a, col2b, col2c = st.columns(3)
        with col2a:
            st.metric("Final Amount", format_currency(final_amount))
        with col2b:
            st.metric("Total Gains", format_currency(total_gains))
        with col2c:
            st.metric("CAGR", f"{cagr:.2f}%")

        # Create two columns for charts
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            # Growth chart
            fig_growth = create_growth_chart_with_investment(results, 'Final Amount', None, 'Investment Growth Over Time')
            st.plotly_chart(fig_growth, use_container_width=True)

        with chart_col2:
            # Pie chart
            fig_pie = create_pie_chart(principal, total_gains, 'Investment Breakdown')
            st.plotly_chart(fig_pie, use_container_width=True)

        # Results table
        st.subheader("Detailed Breakdown")
        display_cols = ['Period', 'Year', 'Final Amount', 'Interest Percent']
        if inflation_rate > 0:
            display_cols.append('Real Value (Inflation Adjusted)')
        st.dataframe(results[display_cols], use_container_width=True)
    else:
        st.info("👈 Please enter your investment parameters in the sidebar and click 'Calculate' to see results.")

# SIP Calculator
elif calculator_type == "SIP Calculator":
    # Sidebar inputs
    st.sidebar.markdown("### 📈 Input Parameters")
    monthly_investment = st.sidebar.number_input("Monthly SIP Amount (₹)", min_value=500, value=10000, step=500)
    rate = st.sidebar.slider("Expected Annual Return (%)", 1.0, 30.0, 12.0, 0.1)
    years = st.sidebar.slider("Investment Period (Years)", 1, 30, 10)

    calculate_button = st.sidebar.button("Calculate", type="primary", use_container_width=True)

    # Main content area
    st.header("📈 SIP (Systematic Investment Plan) Calculator")

    if calculate_button:
        st.session_state.sip_calculated = True
        st.session_state.sip_results = calc.sip_calculator(monthly_investment, rate, years, inflation_rate)

    if hasattr(st.session_state, 'sip_calculated') and st.session_state.sip_calculated:
        results = st.session_state.sip_results

        # Summary metrics
        total_invested = results.iloc[-1]['Total Invested']
        final_amount = results.iloc[-1]['Final Amount']
        total_gains = results.iloc[-1]['Gains']

        col2a, col2b, col2c = st.columns(3)
        with col2a:
            st.metric("Total Invested", format_currency(total_invested))
        with col2b:
            st.metric("Final Amount", format_currency(final_amount))
        with col2c:
            st.metric("Total Gains", format_currency(total_gains))

        # Create two columns for charts
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            # Growth chart with invested amount
            fig_growth = create_growth_chart_with_investment(results, 'Final Amount', 'Total Invested', 'SIP Growth: Portfolio vs Invested Amount')
            st.plotly_chart(fig_growth, use_container_width=True)

        with chart_col2:
            # Pie chart
            fig_pie = create_pie_chart(total_invested, total_gains, 'SIP Investment Breakdown')
            st.plotly_chart(fig_pie, use_container_width=True)

        # Results table
        st.subheader("Detailed Breakdown")
        display_cols = ['Period', 'Year', 'Total Invested', 'Final Amount', 'Gains', 'Gains Percent']
        if inflation_rate > 0:
            display_cols.append('Real Value (Inflation Adjusted)')
        st.dataframe(results[display_cols], use_container_width=True)
    else:
        st.info("👈 Please enter your SIP parameters in the sidebar and click 'Calculate' to see results.")

# SWP Calculator
elif calculator_type == "SWP Calculator":
    # Sidebar inputs
    st.sidebar.markdown("### 💸 Input Parameters")
    initial_amount = st.sidebar.number_input("Initial Investment (₹)", min_value=100000, value=1000000, step=10000)
    withdrawal_amount = st.sidebar.number_input("Monthly Withdrawal (₹)", min_value=1000, value=10000, step=1000)
    rate = st.sidebar.slider("Expected Annual Return (%)", 1.0, 30.0, 10.0, 0.1)
    years = st.sidebar.slider("Withdrawal Period (Years)", 1, 30, 15)

    calculate_button = st.sidebar.button("Calculate", type="primary", use_container_width=True)

    # Main content area
    st.header("💸 SWP (Systematic Withdrawal Plan) Calculator")

    if calculate_button:
        st.session_state.swp_calculated = True
        st.session_state.swp_results = calc.swp_calculator(initial_amount, withdrawal_amount, rate, years, inflation_rate)
        st.session_state.swp_initial = initial_amount

    if hasattr(st.session_state, 'swp_calculated') and st.session_state.swp_calculated:
        results = st.session_state.swp_results
        initial_amount = st.session_state.swp_initial

        # Summary metrics
        if len(results) > 0:
            final_balance = results.iloc[-1]['Remaining Balance']
            total_withdrawn = results.iloc[-1]['Total Withdrawn']
            years_lasted = len(results)

            col2a, col2b, col2c = st.columns(3)
            with col2a:
                st.metric("Remaining Balance", format_currency(final_balance))
            with col2b:
                st.metric("Total Withdrawn", format_currency(total_withdrawn))
            with col2c:
                st.metric("Years Lasted", f"{years_lasted} years")

            # Create two columns for charts
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                # Balance chart
                fig_growth = create_growth_chart_with_investment(results, 'Remaining Balance', None, 'SWP: Remaining Balance Over Time')
                st.plotly_chart(fig_growth, use_container_width=True)

            with chart_col2:
                # Pie chart for remaining vs withdrawn
                fig_pie = create_swp_pie_chart(final_balance, total_withdrawn, 'SWP Distribution')
                st.plotly_chart(fig_pie, use_container_width=True)

            # Results table
            st.subheader("Detailed Breakdown")
            display_cols = ['Period', 'Year', 'Remaining Balance', 'Annual Withdrawn', 'Total Withdrawn']
            if inflation_rate > 0:
                display_cols.append('Real Balance (Inflation Adjusted)')
            st.dataframe(results[display_cols], use_container_width=True)
    else:
        st.info("👈 Please enter your SWP parameters in the sidebar and click 'Calculate' to see results.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666;'>
        <p>💡 <strong>Disclaimer:</strong> This calculator provides estimates based on assumed rates of return. 
        Actual returns may vary. Please consult with a financial advisor for investment decisions.</p>
    </div>
    """, 
    unsafe_allow_html=True
)
