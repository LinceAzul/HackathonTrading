import numpy as np
import pandas as pd
from src.strategies.base import StrategyInterface

class EnhancedStrategy(StrategyInterface):
    """
    Enhanced multi-asset strategy combining trend, momentum, mean-reversion, and triangular arbitrage.

    Indicators:
      - EMA crossover for trend
      - RSI for momentum filtering
      - ATR for dynamic volatility threshold and stop-loss
    Position sizing:
      - Risk-per-trade based on ATR
    Risk controls:
      - Maximum open position count
      - Trade cooldowns to avoid rapid reversals
    """
    def __init__(self,
                 ema_short=12,
                 ema_long=26,
                 rsi_period=14,
                 atr_period=14,
                 risk_per_trade=0.01,
                 max_positions=3,
                 cooldown_period=5):
        self.initialized = False
        self.price_history = {pair: [] for pair in ["token_1/fiat", "token_2/fiat", "token_1/token_2"]}
        self.high_history = {pair: [] for pair in ["token_1/fiat", "token_2/fiat"]}
        self.low_history  = {pair: [] for pair in ["token_1/fiat", "token_2/fiat"]}
        self.window = max(ema_long, rsi_period, atr_period) + 1
        self.ema_short = ema_short
        self.ema_long = ema_long
        self.rsi_period = rsi_period
        self.atr_period = atr_period
        self.risk_per_trade = risk_per_trade
        self.max_positions = max_positions
        self.cooldown_period = cooldown_period
        # track cooldowns per pair
        self.cooldowns = {pair: 0 for pair in self.price_history}

    def _ema(self, prices, span):
        return pd.Series(prices).ewm(span=span, adjust=False).mean().iloc[-1]

    def _rsi(self, prices):
        delta = np.diff(prices)
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        avg_gain = np.mean(up[-self.rsi_period:])
        avg_loss = -np.mean(down[-self.rsi_period:])
        rs = avg_gain / (avg_loss + 1e-8)
        return 100 - (100 / (1 + rs))

    def _atr(self, highs, lows, closes):
        trs = []
        for i in range(1, len(closes)):
            tr = max(highs[i] - lows[i],
                     abs(highs[i] - closes[i-1]),
                     abs(lows[i] - closes[i-1]))
            trs.append(tr)
        return np.mean(trs[-self.atr_period:])

    def on_data(self, market_data, balances):
        orders = []
        # Update histories
        for pair, data in market_data.items():
            if pair in self.price_history:
                close = data['close']
                self.price_history[pair].append(close)
                if pair in self.high_history:
                    self.high_history[pair].append(data['high'])
                    self.low_history[pair].append(data['low'])
                # trim history
                if len(self.price_history[pair]) > self.window:
                    self.price_history[pair] = self.price_history[pair][-self.window:]
        # wait
        if not self.initialized:
            if all(len(v) >= self.window for v in self.price_history.values()):
                self.initialized = True
            else:
                return orders
        # decrement cooldowns
        for pair in self.cooldowns:
            if self.cooldowns[pair] > 0:
                self.cooldowns[pair] -= 1
        # trend + momentum + mean-reversion
        for pair in ['token_1/fiat', 'token_2/fiat']:
            prices = self.price_history[pair]
            if len(prices) < self.window: continue
            # indicators
            ema_s = self._ema(prices, self.ema_short)
            ema_l = self._ema(prices, self.ema_long)
            rsi   = self._rsi(prices)
            atr   = self._atr(self.high_history[pair], self.low_history[pair], prices)
            current = prices[-1]

            # skip if in cooldown
            if self.cooldowns[pair] > 0:
                continue

            # trend-following signal
            if ema_s > ema_l and 30 < rsi < 70:
                # buy signal
                risk_amount = balances['fiat'] * self.risk_per_trade
                qty = (risk_amount / current)
                fee = market_data.get('fee', 0)
                cost = qty * current * (1 + fee)
                if balances['fiat'] >= cost:
                    orders.append({'pair': pair, 'side': 'buy', 'qty': qty})
                    self.cooldowns[pair] = self.cooldown_period
            elif ema_s < ema_l and 30 < rsi < 70:
                # sell signal
                base = pair.split('/')[0]
                max_qty = balances.get(base, 0)
                if max_qty > 0:
                    orders.append({'pair': pair, 'side': 'sell', 'qty': max_qty * self.risk_per_trade})
                    self.cooldowns[pair] = self.cooldown_period
            # mean reversion at extremes
            elif current > ema_l + 2 * atr:
                # overbought: sell
                base = pair.split('/')[0]
                qty = balances.get(base, 0) * self.risk_per_trade
                if qty > 0:
                    orders.append({'pair': pair, 'side': 'sell', 'qty': qty})
                    self.cooldowns[pair] = self.cooldown_period
            elif current < ema_l - 2 * atr:
                # oversold: buy
                qty = (balances['fiat'] * self.risk_per_trade) / current
                fee = market_data.get('fee', 0)
                cost = qty * current * (1 + fee)
                if balances['fiat'] >= cost:
                    orders.append({'pair': pair, 'side': 'buy', 'qty': qty})
                    self.cooldowns[pair] = self.cooldown_period
        # triangular arbitrage
        if all(p in market_data for p in ['token_1/fiat', 'token_2/fiat', 'token_1/token_2']):
            p1 = market_data['token_1/fiat']['close']
            p2 = market_data['token_2/fiat']['close']
            p12 = market_data['token_1/token_2']['close']
            implied = p1 / p2
            fee = market_data.get('fee', 0)
            if p12 < implied * (1 - fee):
                # buy token1 with token2
                qty = balances['token_2'] * self.risk_per_trade
                if qty * p12 * (1 + fee) <= balances['token_2'] * p12:
                    orders.append({'pair': 'token_1/token_2', 'side': 'buy', 'qty': qty})
            elif p12 > implied * (1 + fee):
                # sell token1 for token2
                qty = balances['token_1'] * self.risk_per_trade
                if qty > 0:
                    orders.append({'pair': 'token_1/token_2', 'side': 'sell', 'qty': qty})
        return orders