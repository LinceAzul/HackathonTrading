import numpy as np
import pandas as pd

class Trader:
    """Trader supporting multiple trading pairs and currencies."""

    def __init__(self, balances, fee):
        # Initialize balances for each currency
        self.balances = balances

        # Track market prices for each pair
        self.prices = {
            "token_1/fiat": None,
            "token_2/fiat": None,
            "token_1/token_2": None
        }

        # First and last prices for reporting
        self.first_prices = {
            "token_1/fiat": None,
            "token_2/fiat": None,
            "token_1/token_2": None
        }

        # Store the first update timestamp for each pair
        self.first_update = {
            "token_1/fiat": False,
            "token_2/fiat": False,
            "token_1/token_2": False
        }

        # Track portfolio value history
        self.equity_history = 0.0
        self.turnover = 0.0
        self.trade_count = 0
        self.total_fees_paid = 0.0  # Track total fees paid

        # Trading fee
        self.fee = fee

    def update_market(self, pair, price_data):
        """Update market prices for a specific trading pair"""
        # Store the updated price
        self.prices[pair] = price_data["close"]

        # Store first price for each pair (for reporting)
        if not self.first_update[pair]:
            self.first_prices[pair] = price_data["close"]
            self.first_update[pair] = True

        # Calculate total portfolio value (in fiat)
        equity = self.calculate_portfolio_value()
        self.equity_history.append(equity)

    def calculate_portfolio_value(self):
        """Calculate total portfolio value in fiat currency"""
        value = self.balances["fiat"]

        # Add token_1 value if we have price data
        if self.prices["token_1/fiat"] is not None:
            value += self.balances["token_1"] * self.prices["token_1/fiat"]

        # Add token_2 value if we have price data
        if self.prices["token_2/fiat"] is not None:
            value += self.balances["token_2"] * self.prices["token_2/fiat"]
        # If token_2/fiat price not available but token_1/fiat and token_1/token_2 are available
        elif self.prices["token_1/fiat"] is not None and self.prices["token_1/token_2"] is not None:
            token2_value_in_token1 = self.balances["token_2"] / self.prices["token_1/token_2"]
            value += token2_value_in_token1 * self.prices["token_1/fiat"]

        return value

    def execute(self, order):
        """Execute a trading order across any supported pair"""
        pair = order["pair"]  # e.g., "token_1/fiat"
        side = order["side"]  # "buy" or "sell"
        qty = float(order["qty"])

        # Split the pair into base and quote currencies
        base, quote = pair.split("/")

        # Get current price for the pair
        price = self.prices[pair]
        if price is None:
            return  # Can't trade without a price

        executed = False

        if side == "buy":
            # Calculate total cost including fee
            base_cost = qty * price
            fee_amount = base_cost * self.fee
            total_cost = base_cost + fee_amount

            # Check if we have enough of the quote currency
            if self.balances[quote] >= total_cost:
                # Deduct quote currency (e.g., fiat)
                self.balances[quote] -= total_cost

                # Add base currency (e.g., token_1)
                self.balances[base] += qty

                # Track turnover and fees
                self.turnover += total_cost
                self.total_fees_paid += fee_amount
                executed = True

        elif side == "sell":
            # Check if we have enough of the base currency
            if self.balances[base] >= qty:
                # Calculate proceeds after fee
                base_proceeds = qty * price
                fee_amount = base_proceeds * self.fee
                net_proceeds = base_proceeds - fee_amount

                # Add quote currency (e.g., fiat)
                self.balances[quote] += net_proceeds

                # Deduct base currency (e.g., token_1)
                self.balances[base] -= qty

                # Track turnover and fees
                self.turnover += base_proceeds
                self.total_fees_paid += fee_amount
                executed = True

        # Count successful trades
        if executed:
            self.trade_count += 1

    def calculate_score(self):
        equity_series = pd.Series(self.equity_history)
        returns = equity_series.pct_change().dropna()
        initial = equity_series.iloc[0]
        final = equity_series.iloc[-1]
        
        absolute_pnl = final - initial
        pct_pnl = (absolute_pnl / initial) * 100
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if not returns.empty else 0
        running_max = equity_series.cummax()
        max_dd = ((equity_series - running_max) / running_max).min()
        score = 0.7 * sharpe - 0.2 * abs(max_dd) - 0.1 * (self.turnover / 1_000_000)

        return {
            "Final Equity": final,
            "Absolute PnL": absolute_pnl,
            "Pct PnL": pct_pnl,
            "Sharpe": sharpe,
            "Max Drawdown": max_dd,
            "Turnover": self.turnover,
            "Fees Paid": self.total_fees_paid,
            "Trade Count": self.trade_count,
            "Score": score
        }