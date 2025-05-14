import uuid
import pandas as pd
from src.strategies.base import StrategyInterface
from src.strategies.default import DefaultStrategy
from src.strategies.mean_reversion import MeanReversionStrategy
from src.strategies.momentum import MomentumStrategy

import json
from pathlib import Path

from src.__init__ import DATA_PATH

def run_backtest(combined_data: pd.DataFrame, fee: float, balances: dict[str, float], strategy: StrategyInterface) -> pd.DataFrame:
    """Run a backtest with multiple trading pairs.

    Args:
        submission_dir: Path to the strategy directory
        combined_data: DataFrame containing market data for multiple pairs
        fee: Trading fee (in basis points, e.g., 2 = 0.02%)
        balances: Dictionary of {pair: amount} containing initial balances
        strategy: StrategyInterface instance to use for trading decisions
    """
    # Record initial balances for display
    initial_balances = balances.copy()

    # Initialize prices with first data point for each pair
    combined_data.sort_values("timestamp", inplace=True)
    first_prices = {k: df.iloc[0]['close'] for k, df in combined_data.groupby("symbol")}

    # Calculate true initial portfolio value including all assets
    initial_portfolio_value = initial_balances["fiat"]
    if "token_1/fiat" in first_prices and initial_balances["token_1"] > 0:
        initial_portfolio_value += initial_balances["token_1"] * first_prices["token_1/fiat"]
    if "token_2/fiat" in first_prices and initial_balances["token_2"] > 0:
        initial_portfolio_value += initial_balances["token_2"] * first_prices["token_2/fiat"]

    # Combine all dataframes and sort by timestamp
    result = pd.DataFrame(
        columns=["id", "timestamp", "pair", "side", "qty"],
    )

    # Process data timestamp by timestamp
    for timestamp, group in combined_data.groupby('timestamp'):
        # Update prices for each pair in this timestamp
        market_data = {
            "fee": fee,
        }
        for _, row in group.iterrows():
            pair = row['symbol']
            data_dict = row.to_dict()
            # Add fee information to market data so strategies can access it
            market_data[pair] = data_dict
        
        # Get strategy decision based on all available market data and current balances
        orders = strategy.on_data(market_data, balances)

        # Handle list of orders
        for order in orders:
            order["timestamp"] = timestamp
            order["id"] = str(uuid.uuid4())
            result = pd.concat([result, pd.DataFrame([order])], ignore_index=True)

    return result

if __name__ == "__main__":
    hp = f"{DATA_PATH}/hyperparameters.json"
    # hp = "/kaggle/input/crypto-trading-hackathon-2025/hyperparameters.json"

    cd = f"{DATA_PATH}/test.csv"
    # cd = f"{DATA_PATH}/dataset01/dataset01.csv"
    # cd = "/kaggle/input/crypto-trading-hackathon-2025/test.csv"

    with open(hp) as f:
        HYPERPARAMETERS = json.load(f)
        
    FEE = HYPERPARAMETERS.get("fee", 3.0)
    BALANCE_FIAT = HYPERPARAMETERS.get("fiat_balance", 10000.0)
    BALANCE_TOKEN1 = HYPERPARAMETERS.get("token1_balance", 0.0)
    BALANCE_TOKEN2 = HYPERPARAMETERS.get("token2_balance", 0.0)
    OUTPUT = "submission.csv"

    combined_data = pd.read_csv(cd)

    # Run the backtest on the provided test data with a fee of 0.02% and initial balances of 10,000 fiat, and 0 token_1 and token_2
    result = run_backtest(combined_data, FEE, {
        "fiat": BALANCE_FIAT,
        "token_1": BALANCE_TOKEN1,
        "token_2": BALANCE_TOKEN2,
    },
        DefaultStrategy(),
        # MeanReversionStrategy(window=30, threshold=1.5),
        # MomentumStrategy(lookback=20),
    )

    # Output the backtest result to a CSV file for submission
    result.to_csv(OUTPUT, index=False)