from src.strategies.base import StrategyInterface
import numpy as np
import pandas as pd

class AdvancedStrategy(StrategyInterface):
    """Improved multi-pair strategy using EMA crossover, MACD signal filtering, and risk-managed position sizing."""
    def __init__(self,
                 fast_period: int = 12,
                 slow_period: int = 26,
                 signal_period: int = 9,
                 capital_risk: float = 0.01):
        # EMA & MACD parameters
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

        # Capital risk per trade (fraction of fiat balance)
        self.capital_risk = capital_risk

        # Price history buffers
        self.price_history = {
            "token_1/fiat": [],
            "token_2/fiat": [],
            "token_1/token_2": []
        }

        # Flag to skip on first warm-up
        self.initialized = False

    def on_data(self, market_data: dict, balances: dict) -> list:
        orders = []
        fee = market_data.get("fee", 0.001)

        # Update price history for each known pair
        for pair, tick in market_data.items():
            if pair in self.price_history:
                self.price_history[pair].append(tick["close"])
                # limit history to max needed length
                max_len = self.slow_period + self.signal_period
                if len(self.price_history[pair]) > max_len:
                    self.price_history[pair] = self.price_history[pair][-max_len:]

        # Warm-up period until we have enough data
        for hist in self.price_history.values():
            if len(hist) < self.slow_period + self.signal_period:
                return orders

        # Skip first calculation
        if not self.initialized:
            self.initialized = True
            return orders

        # Helper to compute MACD and signal
        def compute_macd(prices):
            series = pd.Series(prices)
            ema_fast = series.ewm(span=self.fast_period, adjust=False).mean()
            ema_slow = series.ewm(span=self.slow_period, adjust=False).mean()
            macd = ema_fast - ema_slow
            signal = macd.ewm(span=self.signal_period, adjust=False).mean()
            return macd.iloc[-1], signal.iloc[-1]

        # ----- Trading logic for token_1/fiat and token_2/fiat -----
        for token_pair in ["token_1/fiat", "token_2/fiat"]:
            price = self.price_history[token_pair][-1]
            macd_val, sig_val = compute_macd(self.price_history[token_pair])

            # Entry when MACD crosses above signal
            if macd_val > sig_val * 1.02:
                # buy signal
                # risk-managed sizing: allocate fraction of fiat capital
                alloc = balances.get("fiat", 0) * self.capital_risk
                qty = alloc / price
                if qty * price * (1 + fee) <= balances.get("fiat", 0):
                    orders.append({"pair": token_pair, "side": "buy", "qty": round(qty, 8)})

            # Exit when MACD crosses below signal
            elif macd_val < sig_val * 0.98:
                # sell signal
                base = token_pair.split("/")[0]
                qty = balances.get(base, 0) * self.capital_risk
                if qty > 0:
                    orders.append({"pair": token_pair, "side": "sell", "qty": round(qty, 8)})

        # ----- Arbitrage via token_1/token_2 vs implied -----
        if all(p in market_data for p in ["token_1/fiat", "token_2/fiat", "token_1/token_2"]):
            t1 = market_data["token_1/fiat"]["close"]
            t2 = market_data["token_2/fiat"]["close"]
            arb_price = market_data["token_1/token_2"]["close"]
            implied = t1 / t2
            # buy if direct < implied * (1 - fee buffer)
            if arb_price < implied * (1 - fee * 2):
                qty = balances.get("token_2", 0) * self.capital_risk
                if qty > 0:
                    orders.append({"pair": "token_1/token_2", "side": "buy", "qty": round(qty, 8)})
            # sell if direct > implied * (1 + fee buffer)
            elif arb_price > implied * (1 + fee * 2):
                qty = balances.get("token_1", 0) * self.capital_risk
                if qty > 0:
                    orders.append({"pair": "token_1/token_2", "side": "sell", "qty": round(qty, 8)})

        return orders
