# Algorithmic Trading Bot – Portfolio Project

## Introduction

This project implements an algorithmic trading bot in Python designed for financial portfolio competitions. Algorithmic trading uses computer programs to execute buy and sell orders of financial assets based on predefined rules, using technical, fundamental, or quantitative analysis.

Automating trading offers significant advantages:

* **Removal of emotional factors**: Decisions are strictly based on programmed parameters
* **Execution speed**: Ability to process data and execute orders in milliseconds
* **Backtesting**: Ability to test strategies on historical data before using real money
* **24/7 operation**: The bot can monitor markets and trade without interruptions

The main goal of this project is to create strategies that maximize financial returns while maintaining proper risk control, applying solid principles of money management and systematic analysis.

## Portfolio Evaluation Metrics

A high-performing portfolio in trading competitions is not only judged by profits, but by the balance between return and risk. Below are the most relevant metrics:

### Main Metrics

| Metric                         | Definition                            | Relevance in Competition                                                                                                                            |
| ------------------------------ | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ROI (Return on Investment)** | % of profit/loss over initial capital | Main metric: shows how much the portfolio gained (e.g., 15% means a 15% return on the invested amount)                                              |
| **Profit Factor**              | Gross profit / Gross loss             | Overall efficiency: >1 is profitable, >2 is excellent. For example, a factor of 1.5 means that for every \$1 lost, \$1.5 is earned                  |
| **Win Rate**                   | % of winning trades                   | Consistency in success (e.g., 60% means 6 out of 10 trades were winners)                                                                            |
| **Maximum Drawdown**           | Largest percentage drop from a peak   | Measures risk: lower drawdown indicates more stability. Example: If you start with \$1000, rise to \$1200, then drop to \$900, the drawdown is -25% |
| **Sharpe Ratio**               | Excess return divided by volatility   | Risk-adjusted performance; >1 is good, >2 is excellent                                                                                              |

### Additional Metrics

* **Net Absolute Profit**: Total profit after deducting costs (commissions, etc.)
* **Risk-Reward Ratio**: Average magnitude of gains vs losses per trade. For instance, if your strategy only wins 20% of the time, each winning trade must return \~5x more than a losing one to be profitable.
* **Consistency**: A stable, upward-sloping equity curve, with gains achieved consistently rather than relying on one lucky trade.
* **Risk of Ruin**: Probability of losing all capital, tied to risk management through proper position sizing and use of stop-losses.

In practice, competition rankings are usually based on final profit (ROI), but if two teams achieve similar returns, metrics like drawdown or Sharpe ratio may determine the winner. A winning strategy is one that grows capital sustainably and safely over the competition period.

## Project Structure

The file and folder organization follows software development best practices, allowing for modularity, maintenance, and collaboration:

```
pyproject.toml            # Project dependencies
|
README.md                 # This documentation file
|
src/
│
├── data/                     # Financial data
│   ├── raw/                  # Raw data
│   └── processed/            # Preprocessed data
│
├── strategies/               # Trading strategy modules
│   ├── __init__.py
│   ├── mean_reversion.py     # Mean reversion strategy
│   └── trend_following.py    # Trend following strategy
│
├── utils/                    # Common utilities
│   ├── __init__.py
│   ├── data_fetcher.py       # API data fetching
│   └── indicators.py         # Technical indicator calculations
│
├── backtesting/              # Scripts for historical data testing
│   ├── __init__.py
│   ├── backtest_engine.py    # Backtesting engine
│   └── performance.py        # Performance metrics calculation
│
└── tests/                    # Automated tests
    ├── __init__.py
```

### Component Details

* **config/**: Stores strategy parameters and API credentials. Real API keys should never be uploaded for security.
* **data/**: Contains market data for backtesting or analysis. Raw and processed data are kept separate for organization.
* **strategies/**: Holds the core trading logic. Each strategy is in its own module for easy testing and reuse.
* **risk\_management/**: Defines rules for position sizing and loss limits—critical for portfolio survival.
* **utils/**: Helper functions used across different parts of the project.
* **backtesting/**: Tools to simulate strategies on historical data before using them in live trading.
* **logs/**: Logs of trades, errors, and system events for debugging and analysis.
* **tests/**: Automated tests to verify critical components work correctly.

## Virtual Environment Setup

A virtual environment isolates the project’s dependencies, helping with reproducibility and avoiding conflicts with other Python projects.

### On Windows

1. Make sure Python is installed (preferably Python 3.8+)
2. Open Command Prompt or PowerShell
3. Navigate to the project folder:

   ```
   cd path\to\trading-bot
   ```
4. Create a virtual environment:

   ```
   python -m venv venv
   ```
5. Activate the virtual environment:

   ```
   venv\Scripts\activate
   ```
6. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

### On macOS/Linux

1. Make sure Python is installed (preferably Python 3.8+)
2. Open the Terminal
3. Navigate to the project folder:

   ```
   cd path/to/trading-bot
   ```
4. Create a virtual environment:

   ```
   python3 -m venv venv
   ```
5. Activate the virtual environment:

   ```
   source venv/bin/activate
   ```
6. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

## Basic Usage

To run the trading bot:

1. Set up your API keys in the file `config/api_config.py` (create this file based on `api_config_example.py`)
2. Run:

   ```
   python main.py
   ```

## Strategy Development

To create a new strategy:

1. Create a new file in the `strategies/` folder
2. Implement your trading logic
3. Perform backtesting in the `backtesting/` folder
4. Integrate the strategy into the main script

## Contributing

To contribute to the project:

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push the branch (`git push origin feature/new-feature`)
5. Open a Pull Request