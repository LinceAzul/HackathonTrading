import numpy as np
from src.strategies.base import StrategyInterface

class MeanReversionStrategy(StrategyInterface):
    def __init__(self, window=30, threshold=1.5):
        self.window = window
        self.threshold = threshold
        self.history = []

    def on_data(self, market_data, balances):
        orders = []
        pair = "token_1/fiat"
        price = market_data[pair]["close"]
        self.history.append(price)
        if len(self.history) > self.window:
            self.history = self.history[-self.window:]
            mu = np.mean(self.history)
            sigma = np.std(self.history)
            qty = 0.01
            fee = market_data.get("fee", 0)
            # Buy low
            if price < mu - self.threshold * sigma:
                req = qty * price * (1 + fee)
                if balances.get("fiat", 0) >= req:
                    orders.append({"pair": pair, "side": "buy", "qty": qty})
            # Sell high
            elif price > mu + self.threshold * sigma:
                avail = balances.get("token_1", 0)
                qty_sell = min(qty, avail)
                if qty_sell > 0:
                    orders.append({"pair": pair, "side": "sell", "qty": qty_sell})
        return orders