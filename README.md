# Algorithmic Trading Bot

A backtesting system I built to test whether different trading strategies would have been profitable on historical stock data. The idea was simple - instead of risking real money to see if a strategy works, you simulate it on past data first.

## What it does

You give it a stock, a date range, and a strategy. It fetches real price data, runs the strategy through every trading day, simulates buys and sells with realistic costs (commissions, slippage), and tells you how you would have done.

I tested 7 different strategy configurations across NVDA and SPY. The most interesting result was that Bollinger Bands mean reversion returned +22.3% on NVDA over 6 months with a 93.3% win rate, while Moving Average Crossover lost -19.8% on the exact same dataset. Same stock, same time period, completely different outcomes depending on strategy - which is exactly why backtesting matters.

## Strategies implemented

**Moving Average Crossover** - Buys when the short-term average crosses above the long-term average (momentum). Struggled on NVDA because the stock was choppy rather than trending.

**RSI Mean Reversion** - Buys when RSI drops below 40 (oversold) and sells when it rises above 60 (overbought). Returned +14.3% on NVDA with 88.9% win rate.

**Bollinger Bands** - Buys when price drops to the lower 20% of its normal range, sells when it reaches the upper 20%. Best performer across both assets tested.

## Results

| Strategy | Asset | Return | Win Rate | Sharpe |
|----------|-------|--------|----------|--------|
| Bollinger Bands 10/2 | NVDA | +22.34% | 93.3% | 2.56 |
| Bollinger Bands 20/2 | NVDA | +18.03% | 100% | 2.34 |
| RSI Mean Reversion | NVDA | +14.26% | 88.9% | 1.72 |
| Bollinger Bands 20/3 | SPY | +4.03% | 100% | 2.27 |
| MA Crossover 5/20 | NVDA | -19.80% | 20% | -4.48 |

## How it's built

data/providers/     - Data source integrations (Yahoo Finance, Questrade-ready)
database/           - SQLite storage for market data
strategies/         - Trading strategy implementations
backtesting/        - Core simulation and metrics engine
utils/              - Technical indicator calculations


The data layer uses an abstract interface so I can swap Yahoo Finance for a real broker (Questrade) without touching the rest of the code. Currently have Yahoo Finance implemented for backtesting and historical data.

## Metrics tracked

For every backtest the engine calculates total return, Sharpe ratio, maximum drawdown, win rate, profit factor, average win/loss size, and a full trade-by-trade breakdown with equity curve.

## Tech stack

Python, pandas, NumPy, SQLAlchemy, SQLite, yfinance, matplotlib

## Setup
```bash
git clone https://github.com/ayaannaveed05/algo-trading-bot.git
cd algo-trading-bot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Running a backtest
```bash
# Run all strategies and compare
python test_all_strategies.py

# Test individual strategies
python test_bollinger.py
python test_rsi_strategy.py
```