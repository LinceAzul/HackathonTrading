import numpy as np
import pandas as pd

def calculate_score(
    trades: pd.DataFrame,
    price_data: pd.DataFrame,
    initial_balances: dict[str, float],
    fee_bps: float,
    risk_free_rate: float = 0.0
) -> dict[str, float]:
    """
    Calculate risk‐adjusted performance score for a backtest.

    Args:
        trades: DataFrame with columns [id, timestamp, pair, side, qty]
        price_data: DataFrame with columns [timestamp, symbol, close]
        initial_balances: {'fiat': float, 'token1': float, ...}
        fee_bps: fee in basis points (e.g. 2 = 0.02%)
        risk_free_rate: annual risk‐free rate as decimal (default 0.0)

    Returns:
        Dict containing:
          initial_equity, final_equity, abs_pnl, pct_pnl,
          annualized_return, annualized_volatility, sharpe,
          max_drawdown, turnover, fees_paid, score
    """
    # --- Prepare data & lookups ---
    trades = trades.copy()
    trades['timestamp'] = pd.to_datetime(trades['timestamp'], utc=True)
    price_data = price_data.copy()
    price_data['timestamp'] = pd.to_datetime(price_data['timestamp'], utc=True)
    trades.sort_values('timestamp', inplace=True)
    price_data.sort_values('timestamp', inplace=True)
    price_lookup = price_data.set_index(['timestamp','symbol'])['close']

    # --- Initialize ---
    balances = initial_balances.copy()
    # compute initial equity
    t0 = price_data['timestamp'].iloc[0]
    init_eq = balances['fiat']
    for asset, amt in balances.items():
        if asset == 'fiat': continue
        pair = f"{asset}/fiat"
        price = price_lookup.get((t0, pair), 0.0)
        init_eq += amt * price

    turnover = 0.0
    fees_paid = 0.0

    # group trades by timestamp for fast lookup
    trades_by_time = trades.groupby('timestamp')
    equity_ts = []

    # --- Walk through each price timestamp, apply trades, record equity ---
    for t in sorted(price_data['timestamp'].unique()):
        # apply all trades at this timestamp
        if t in trades_by_time.groups:
            for _, order in trades_by_time.get_group(t).iterrows():
                pair = order['pair']
                asset = pair.split('/')[0]
                side = order['side']
                qty = order['qty']
                price = price_lookup.loc[(t, pair)]
                notional = qty * price
                turnover += abs(notional)
                fee_rate = fee_bps / 10_000.0

                if side == 'buy':
                    cost = notional * (1 + fee_rate)
                    balances['fiat'] -= cost
                    balances[asset] = balances.get(asset, 0.0) + qty
                    fees_paid += notional * fee_rate
                elif side == 'sell':
                    proceeds = notional * (1 - fee_rate)
                    balances['fiat'] += proceeds
                    balances[asset] = balances.get(asset, 0.0) - qty
                    fees_paid += notional * fee_rate

        # compute equity at this timestamp
        eq = balances['fiat']
        for asset, amt in balances.items():
            if asset == 'fiat': continue
            pair = f"{asset}/fiat"
            price = price_lookup.get((t, pair), 0.0)
            eq += amt * price
        equity_ts.append((t, eq))

    eq_df = pd.DataFrame(equity_ts, columns=['timestamp','equity']).set_index('timestamp')

    # --- Compute returns & annualization factors ---
    returns = eq_df['equity'].pct_change().dropna()
    total_seconds = (eq_df.index[-1] - eq_df.index[0]).total_seconds()
    seconds_per_year = 365 * 24 * 3600
    years = total_seconds / seconds_per_year

    if years <= 0 or returns.empty:
        raise ValueError("Not enough data to annualize.")

    # annualized return
    total_return = eq_df['equity'].iloc[-1] / eq_df['equity'].iloc[0]
    ann_return = total_return**(1/years) - 1

    # annualized volatility
    n_periods = returns.shape[0]
    ann_vol = returns.std(ddof=1) * np.sqrt(n_periods / years)

    # sharpe
    sharpe = (ann_return - risk_free_rate) / ann_vol if ann_vol > 0 else np.nan

    # max drawdown
    running_max = eq_df['equity'].cummax()
    drawdowns = (eq_df['equity'] - running_max) / running_max
    max_dd = drawdowns.min()

    # other stats
    final_eq = eq_df['equity'].iloc[-1]
    abs_pnl = final_eq - init_eq
    pct_pnl = abs_pnl / init_eq * 100

    # final score
    score = (
        0.7 * sharpe
        - 0.2 * abs(max_dd)
        - 0.1 * (turnover / 1_000_000.0)
    )

    return {
        'initial_equity': init_eq,
        'final_equity': final_eq,
        'abs_pnl': abs_pnl,
        'pct_pnl': pct_pnl,
        'annualized_return': ann_return,
        'annualized_volatility': ann_vol,
        'sharpe': sharpe,
        'max_drawdown': max_dd,
        'turnover': turnover,
        'fees_paid': fees_paid,
        'score': score
    }


# 1 -> 1118.6322
# 2 -> 45.2633