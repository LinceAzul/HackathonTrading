import numpy as np
from src.strategies.base import StrategyInterface

SHORT_WINDOW = 40          # short moving average, slower → fewer false crosses
LONG_WINDOW  = 120         # keeps the ratio ≈1 : 3
VOL_THRESHOLD = 0.02       # requires 1.2% of CV → filters flat sessions
QTY_T1 = 0.10              # double the size per operation in token_1
QTY_T2 = 0.20  

class MomentumVolStrategy(StrategyInterface):
    """
    Strategy that uses momentum and volatility to make trading decisions.
    It calculates short and long moving averages, and uses the coefficient of
    variation to determine the volatility of the price series.
    It trades two tokens against fiat and each other, and uses a simple
    strategy to decide when to buy or sell.
    The strategy is designed to be used in a backtesting environment.
    """

    def __init__(self):
        """Initialize strategy state."""
        self.prices = {pair: [] for pair in
                       ["token_1/fiat", "token_2/fiat", "token_1/token_2"]}
        # Price history for each pair - this maintains state between calls
        self.in_position = {"token_1": False, "token_2": False}

    # ---------- Inside utilities ---------- #
    @staticmethod
    def _sma(arr, w):
        return float(np.mean(arr[-w:]))

    @staticmethod
    def _cv(arr):              
        mu, sigma = np.mean(arr), np.std(arr)
        return sigma / mu if mu != 0 else 0.0

    # ---------- Main method ---------- #
    def on_data(self, market_data, balances):
        orders = []

        # Update price history for each pair
        for pair, data in market_data.items():
            if pair in self.prices:
                self.prices[pair].append(data["close"])
                # mantenemos solo LONG_WINDOW velas
                if len(self.prices[pair]) > LONG_WINDOW:
                    self.prices[pair] = self.prices[pair][-LONG_WINDOW:]

        # Wait until we have enough data points
        if any(len(p) < LONG_WINDOW for p in self.prices.values()):
            return orders

        # ---------- token_1 / fiat ---------- #
        p1   = self.prices["token_1/fiat"]
        sma_s, sma_l = self._sma(p1, SHORT_WINDOW), self._sma(p1, LONG_WINDOW)
        cv1  = self._cv(p1)

        # Buy signal (entry)
        if (not self.in_position["token_1"]
            and sma_s > sma_l
            and p1[-2] <= self._sma(p1[:-1], SHORT_WINDOW)   # crossover
            and cv1 > VOL_THRESHOLD):

            qty = QTY_T1
            cost = qty * p1[-1] * (1 + market_data["fee"])
            if balances["fiat"] >= cost:
                print(f"BUY {qty} token_1 at {p1[-1]:.2f} (cv={cv1:.3f})")
                orders.append({"pair": "token_1/fiat", "side": "buy", "qty": qty})
                self.in_position["token_1"] = True

        # Sell signal (exit)
        elif (self.in_position["token_1"]
              and (p1[-1] < sma_l or cv1 <= VOL_THRESHOLD)):

            qty = min(QTY_T1, balances["token_1"])
            if qty > 0:
                print(f"SELL {qty} token_1 at {p1[-1]:.2f} (cv={cv1:.3f})")
                orders.append({"pair": "token_1/fiat", "side": "sell", "qty": qty})
            self.in_position["token_1"] = False

        # ---------- token_2 / fiat ---------- #
        p2   = self.prices["token_2/fiat"]
        sma_s2, sma_l2 = self._sma(p2, SHORT_WINDOW), self._sma(p2, LONG_WINDOW)
        cv2  = self._cv(p2)

        if (not self.in_position["token_2"]
            and sma_s2 > sma_l2
            and p2[-2] <= self._sma(p2[:-1], SHORT_WINDOW)
            and cv2 > VOL_THRESHOLD):

            qty = QTY_T2
            cost = qty * p2[-1] * (1 + market_data["fee"])
            if balances["fiat"] >= cost:
                print(f"BUY {qty} token_2 at {p2[-1]:.2f} (cv={cv2:.3f})")
                orders.append({"pair": "token_2/fiat", "side": "buy", "qty": qty})
                self.in_position["token_2"] = True

        elif (self.in_position["token_2"]
              and (p2[-1] < sma_l2 or cv2 <= VOL_THRESHOLD)):

            qty = min(QTY_T2, balances["token_2"])
            if qty > 0:
                print(f"SELL {qty} token_2 at {p2[-1]:.2f} (cv={cv2:.3f})")
                orders.append({"pair": "token_2/fiat", "side": "sell", "qty": qty})
            self.in_position["token_2"] = False

        return orders
