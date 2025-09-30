
import pandas as pd
import numpy as np

class MutualFundCalculator:
    def __init__(self):
        pass

    def one_time_investment(self, principal, rate, years, inflation_rate=0):
        """
        Calculate one-time investment with compound interest
        """
        results = []
        current_amount = principal

        for year in range(1, years + 1):
            # Apply compound interest
            current_amount = current_amount * (1 + rate/100)

            # Calculate real return after inflation adjustment
            if inflation_rate > 0:
                real_value = current_amount / ((1 + inflation_rate/100) ** year)
            else:
                real_value = current_amount

            interest_earned = current_amount - principal
            interest_percent = (interest_earned / principal) * 100

            results.append({
                'Period': year,
                'Year': 2025 + year,
                'Final Amount': int(current_amount),
                'Interest Percent': int(interest_percent),
                'Real Value (Inflation Adjusted)': int(real_value) if inflation_rate > 0 else None
            })

        return pd.DataFrame(results)

    def sip_calculator(self, monthly_investment, rate, years, inflation_rate=0):
        """
        Calculate SIP (Systematic Investment Plan) returns
        """
        results = []
        monthly_rate = rate / (12 * 100)  # Monthly interest rate
        total_invested = 0
        current_value = 0

        for year in range(1, years + 1):
            for month in range(12):
                total_invested += monthly_investment
                current_value = (current_value + monthly_investment) * (1 + monthly_rate)

            # Calculate real value after inflation adjustment
            if inflation_rate > 0:
                real_value = current_value / ((1 + inflation_rate/100) ** year)
            else:
                real_value = current_value

            gains = current_value - total_invested
            gains_percent = (gains / total_invested) * 100 if total_invested > 0 else 0

            results.append({
                'Period': year,
                'Year': 2025 + year,
                'Total Invested': int(total_invested),
                'Final Amount': int(current_value),
                'Gains': int(gains),
                'Gains Percent': int(gains_percent),
                'Real Value (Inflation Adjusted)': int(real_value) if inflation_rate > 0 else None
            })

        return pd.DataFrame(results)

    def swp_calculator(self, initial_amount, withdrawal_amount, rate, years, inflation_rate=0):
        """
        Calculate SWP (Systematic Withdrawal Plan)
        """
        results = []
        monthly_rate = rate / (12 * 100)
        current_balance = initial_amount
        total_withdrawn = 0

        for year in range(1, years + 1):
            year_withdrawn = 0
            for month in range(12):
                if current_balance > 0:
                    # Apply monthly growth
                    current_balance = current_balance * (1 + monthly_rate)
                    # Make withdrawal
                    withdrawal = min(withdrawal_amount, current_balance)
                    current_balance -= withdrawal
                    total_withdrawn += withdrawal
                    year_withdrawn += withdrawal

            # Calculate real value after inflation adjustment
            if inflation_rate > 0:
                real_balance = current_balance / ((1 + inflation_rate/100) ** year)
                real_withdrawn = total_withdrawn / ((1 + inflation_rate/100) ** year)
            else:
                real_balance = current_balance
                real_withdrawn = total_withdrawn

            results.append({
                'Period': year,
                'Year': 2025 + year,
                'Remaining Balance': int(current_balance),
                'Annual Withdrawn': int(year_withdrawn),
                'Total Withdrawn': int(total_withdrawn),
                'Real Balance (Inflation Adjusted)': int(real_balance) if inflation_rate > 0 else None
            })

            if current_balance <= 0:
                break

        return pd.DataFrame(results)

    def calculate_cagr(self, initial_value, final_value, years):
        """Calculate Compound Annual Growth Rate"""
        if initial_value <= 0 or final_value <= 0 or years <= 0:
            return 0
        return ((final_value / initial_value) ** (1/years) - 1) * 100
