import pandas as pd
import numpy as np

class MutualFundCalculator:
    def __init__(self):
        pass

    def one_time_investment(self, principal, rate, years, inflation_rate=0, 
                           enable_increase=False, increase_frequency="yearly", 
                           increase_amount=0):
        """
        Calculate one-time investment with compound interest and optional periodic increases
        """
        results = []
        current_amount = principal
        total_principal = principal

        # Convert increase_frequency to match expected values from app.py
        freq_map = {
            "Yearly": "yearly",
            "Every 3 years": "every_3_years", 
            "Every 5 years": "every_5_years",
            "yearly": "yearly",
            "every_3_years": "every_3_years",
            "every_5_years": "every_5_years"
        }
        freq = freq_map.get(increase_frequency, increase_frequency.lower())

        for year in range(1, years + 1):
            # Check if we need to add additional investment this year
            additional_investment = 0
            if enable_increase and increase_amount > 0:
                if freq == "yearly":
                    additional_investment = increase_amount
                elif freq == "every_3_years" and year % 3 == 0:
                    additional_investment = increase_amount
                elif freq == "every_5_years" and year % 5 == 0:
                    additional_investment = increase_amount

            # Add additional investment at the beginning of the year
            current_amount += additional_investment
            total_principal += additional_investment

            # Apply compound interest
            current_amount = current_amount * (1 + rate/100)

            # Calculate real return after inflation adjustment
            if inflation_rate > 0:
                real_value = current_amount / ((1 + inflation_rate/100) ** year)
            else:
                real_value = current_amount

            interest_earned = current_amount - total_principal
            interest_percent = (interest_earned / total_principal) * 100 if total_principal > 0 else 0

            results.append({
                'Period': year,
                'Year': 2025 + year,
                'Total Principal': int(total_principal),
                'Additional Investment': int(additional_investment),
                'Final Amount': int(current_amount),
                'Interest Earned': int(interest_earned),
                'Interest Percent': round(interest_percent, 2),
                'Real Value (Inflation Adjusted)': int(real_value) if inflation_rate > 0 else None
            })

        return pd.DataFrame(results)

    def sip_calculator(self, monthly_investment, rate, years, inflation_rate=0,
                      enable_increase=False, increase_frequency="yearly", 
                      increase_percentage=0):
        """
        Calculate SIP (Systematic Investment Plan) returns with optional periodic increases
        """
        results = []
        monthly_rate = rate / (12 * 100)  # Monthly interest rate
        total_invested = 0
        current_value = 0
        current_monthly_sip = monthly_investment

        # Convert increase_frequency to match expected values from app.py
        freq_map = {
            "Yearly": "yearly",
            "Every 3 years": "every_3_years", 
            "Every 5 years": "every_5_years",
            "yearly": "yearly",
            "every_3_years": "every_3_years",
            "every_5_years": "every_5_years"
        }
        freq = freq_map.get(increase_frequency, increase_frequency.lower())

        for year in range(1, years + 1):
            # Check if we need to increase SIP this year
            if enable_increase and increase_percentage > 0:
                if freq == "yearly":
                    if year > 1:  # Don't increase in the first year
                        current_monthly_sip = current_monthly_sip * (1 + increase_percentage/100)
                elif freq == "every_3_years" and year > 1 and (year - 1) % 3 == 0:
                    current_monthly_sip = current_monthly_sip * (1 + increase_percentage/100)
                elif freq == "every_5_years" and year > 1 and (year - 1) % 5 == 0:
                    current_monthly_sip = current_monthly_sip * (1 + increase_percentage/100)

            year_invested = 0
            for month in range(12):
                total_invested += current_monthly_sip
                year_invested += current_monthly_sip
                current_value = (current_value + current_monthly_sip) * (1 + monthly_rate)

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
                'Monthly SIP': int(current_monthly_sip),
                'Annual Investment': int(year_invested),
                'Total Invested': int(total_invested),
                'Final Amount': int(current_value),
                'Gains': int(gains),
                'Gains Percent': round(gains_percent, 2),
                'Real Value (Inflation Adjusted)': int(real_value) if inflation_rate > 0 else None
            })

        return pd.DataFrame(results)

    def swp_calculator(self, initial_amount, withdrawal_amount, rate, years, inflation_rate=0,
                      enable_increase=False, increase_frequency="yearly", 
                      increase_percentage=0):
        """
        Calculate SWP (Systematic Withdrawal Plan) with optional periodic withdrawal increases
        """
        results = []
        monthly_rate = rate / (12 * 100)
        current_balance = initial_amount
        total_withdrawn = 0
        current_monthly_withdrawal = withdrawal_amount

        # Convert increase_frequency to match expected values from app.py
        freq_map = {
            "Yearly": "yearly",
            "Every 3 years": "every_3_years", 
            "Every 5 years": "every_5_years",
            "yearly": "yearly",
            "every_3_years": "every_3_years",
            "every_5_years": "every_5_years"
        }
        freq = freq_map.get(increase_frequency, increase_frequency.lower())

        for year in range(1, years + 1):
            # Check if we need to increase withdrawal this year
            if enable_increase and increase_percentage > 0:
                if freq == "yearly":
                    if year > 1:  # Don't increase in the first year
                        current_monthly_withdrawal = current_monthly_withdrawal * (1 + increase_percentage/100)
                elif freq == "every_3_years" and year > 1 and (year - 1) % 3 == 0:
                    current_monthly_withdrawal = current_monthly_withdrawal * (1 + increase_percentage/100)
                elif freq == "every_5_years" and year > 1 and (year - 1) % 5 == 0:
                    current_monthly_withdrawal = current_monthly_withdrawal * (1 + increase_percentage/100)

            year_withdrawn = 0
            for month in range(12):
                if current_balance > 0:
                    # Apply monthly growth
                    current_balance = current_balance * (1 + monthly_rate)

                    # Make withdrawal
                    withdrawal = min(current_monthly_withdrawal, current_balance)
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
                'Monthly Withdrawal': int(current_monthly_withdrawal),
                'Annual Withdrawn': int(year_withdrawn),
                'Remaining Balance': int(current_balance),
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