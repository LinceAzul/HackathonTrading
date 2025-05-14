import numpy as np
from src.strategies.base import StrategyInterface

class MomentumStrategy(StrategyInterface):
    def __init__(self, lookback=20):
        self.lookback = lookback
        self.history = {pair: [] for pair in ["token_1/fiat", "token_2/fiat"]}

    def on_data(self, market_data, balances):
        orders = []
        for pair in ["token_1/fiat", "token_2/fiat"]:
            price = market_data[pair]["close"]
            self.history[pair].append(price)
            if len(self.history[pair]) > self.lookback:
                self.history[pair] = self.history[pair][-self.lookback:]
                # Momentum: buy if price above moving average, sell if below
                ma = np.mean(self.history[pair])
                qty = 0.01 if pair.startswith("token_1") else 0.1
                fee = market_data.get("fee", 0)
                if price > ma:
                    # buy
                    required = qty * price * (1 + fee)
                    if balances.get("fiat", 0) >= required:
                        orders.append({"pair": pair, "side": "buy", "qty": qty})
                else:
                    # sell
                    avail = balances.get(pair.split("/")[0], 0)
                    qty_sell = min(qty, avail)
                    if qty_sell > 0:
                        orders.append({"pair": pair, "side": "sell", "qty": qty_sell})
        return orders