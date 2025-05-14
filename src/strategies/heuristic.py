from src.strategies.base import StrategyInterface
import numpy as np

MOVING_AVG_WINDOW = 25
MOMENTUM_WINDOW = 5
VOLATILITY_MULTIPLIER = 2.5
ARBITRAGE_MARGIN = 0.004  # 0.4%

class HeuristicStrategy:
    def __init__(self):
        self.price_history = {
            "token_1/fiat": [],
            "token_2/fiat": [],
            "token_1/token_2": []
        }
        self.window = MOVING_AVG_WINDOW
        self.momentum_window = MOMENTUM_WINDOW
        self.initialized = False

    def _calculate_indicators(self, prices):
        ma = np.mean(prices)
        std = np.std(prices)
        momentum = prices[-1] - prices[-self.momentum_window]
        rsi = 100 - (100 / (1 + np.mean(np.diff(prices)[-self.momentum_window:]) / (np.std(prices[-self.momentum_window:]) + 1e-5)))
        return ma, std, momentum, rsi

    def on_data(self, market_data, balances):
        orders = []

        # Update history
        for pair, data in market_data.items():
            if pair in self.price_history:
                self.price_history[pair].append(data["close"])
                if len(self.price_history[pair]) > self.window:
                    self.price_history[pair] = self.price_history[pair][-self.window:]

        if not all(len(v) >= self.window for v in self.price_history.values()):
            return []

        if not self.initialized:
            self.initialized = True
            return []

        fee = market_data.get("fee", 0.001)

        # --- Heuristic Trading for token_1/fiat ---
        pair = "token_1/fiat"
        if pair in market_data:
            price = self.price_history[pair][-1]
            ma, std, momentum, rsi = self._calculate_indicators(self.price_history[pair])
            # Buy signal
            if price < ma - VOLATILITY_MULTIPLIER * std and momentum > 0 and rsi < 40:
                qty = 0.02
                if balances.get("fiat", 0) >= qty * price * (1 + fee):
                    orders.append({"pair": pair, "side": "buy", "qty": qty})
            # Sell signal
            elif price > ma + VOLATILITY_MULTIPLIER * std and momentum < 0 and rsi > 60:
                qty = min(0.02, balances.get("token_1", 0))
                if qty > 0:
                    orders.append({"pair": pair, "side": "sell", "qty": qty})

        # --- Heuristic Trading for token_2/fiat ---
        pair = "token_2/fiat"
        if pair in market_data:
            price = self.price_history[pair][-1]
            ma, std, momentum, rsi = self._calculate_indicators(self.price_history[pair])
            if price < ma - VOLATILITY_MULTIPLIER * std and momentum > 0 and rsi < 40:
                qty = 0.05
                if balances.get("fiat", 0) >= qty * price * (1 + fee):
                    orders.append({"pair": pair, "side": "buy", "qty": qty})
            elif price > ma + VOLATILITY_MULTIPLIER * std and momentum < 0 and rsi > 60:
                qty = min(0.05, balances.get("token_2", 0))
                if qty > 0:
                    orders.append({"pair": pair, "side": "sell", "qty": qty})

        # --- Arbitrage Heuristic ---
        if all(p in market_data for p in ["token_1/fiat", "token_2/fiat", "token_1/token_2"]):
            t1_fiat = market_data["token_1/fiat"]["close"]
            t2_fiat = market_data["token_2/fiat"]["close"]
            t1_t2 = market_data["token_1/token_2"]["close"]
            implied_price = t1_fiat / t2_fiat
            margin = ARBITRAGE_MARGIN

            if t1_t2 < implied_price * (1 - margin):
                qty = 0.02
                cost = qty * t1_t2 * (1 + fee)
                if balances.get("token_2", 0) >= cost:
                    orders.append({"pair": "token_1/token_2", "side": "buy", "qty": qty})

            elif t1_t2 > implied_price * (1 + margin):
                qty = min(0.02, balances.get("token_1", 0))
                if qty > 0:
                    orders.append({"pair": "token_1/token_2", "side": "sell", "qty": qty})

        return orders
