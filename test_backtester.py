"""Test backtesting engine with multiple strategies"""

from utils.analysis import DataAnalyzer
from strategies.moving_average import MovingAverageCrossover
from strategies.rsi_strategy import RSIMeanReversion
from backtesting.engine import Backtester
from datetime import datetime, timedelta

# Load 1 month of hourly data
analyzer = DataAnalyzer()
symbol = 'SPY'
end = datetime.now()
start = end - timedelta(days=30)

print("="*70)
print("LOADING DATA")
print("="*70)
df = analyzer.get_df(symbol, start, end, interval='1h')
print(f"✓ Loaded {len(df)} hourly bars from {df.index[0]} to {df.index[-1]}\n")

# Create strategies to test
strategies = [
    MovingAverageCrossover(short_period=5, long_period=20),   # Fast MA
    MovingAverageCrossover(short_period=10, long_period=50),  # Medium MA
    MovingAverageCrossover(short_period=20, long_period=100), # Slow MA
    RSIMeanReversion(rsi_period=14, oversold=30, overbought=70),  # Conservative RSI
    RSIMeanReversion(rsi_period=14, oversold=40, overbought=60),  # Aggressive RSI
]

# Initialize backtester
backtester = Backtester(
    initial_capital=10000,  # Start with $10k
    commission=0.001,       # 0.1% commission per trade
    slippage=0.0005        # 0.05% slippage
)

# Compare all strategies
print("="*70)
print("RUNNING BACKTESTS")
print("="*70)
comparison = backtester.compare_strategies(strategies, df)

# Display results
print("\n" + "="*70)
print("STRATEGY COMPARISON")
print("="*70)
print(comparison.to_string(index=False))

# Find best strategy
print("\n" + "="*70)
print("BEST PERFORMERS")
print("="*70)

# Sort by total return
best_return = comparison.loc[comparison['total_return'].idxmax()]
print(f"\nHighest Return:")
print(f"  Strategy: {best_return['strategy']}")
print(f"  Return: {best_return['total_return']:.2f}%")
print(f"  Sharpe: {best_return['sharpe_ratio']:.2f}")
print(f"  Max DD: {best_return['max_drawdown']:.2f}%")

# Sort by Sharpe ratio (risk-adjusted return)
best_sharpe = comparison.loc[comparison['sharpe_ratio'].idxmax()]
print(f"\nBest Risk-Adjusted (Sharpe):")
print(f"  Strategy: {best_sharpe['strategy']}")
print(f"  Return: {best_sharpe['total_return']:.2f}%")
print(f"  Sharpe: {best_sharpe['sharpe_ratio']:.2f}")
print(f"  Win Rate: {best_sharpe['win_rate']:.1f}%")

# Detailed view of best strategy
print("\n" + "="*70)
print(f"DETAILED RESULTS: {best_return['strategy']}")
print("="*70)

# Re-run best strategy to get trade details
best_strategy = [s for s in strategies if s.name == best_return['strategy']][0]
detailed_results = backtester.run_backtest(best_strategy, df.copy())

# Show all trades
trades = detailed_results['trades']
if trades:
    print(f"\nAll Trades ({len(trades)} total):\n")
    for i, trade in enumerate(trades, 1):
        print(f"Trade {i}:")
        print(f"  Entry:  {trade['entry_time']} @ ${trade['entry_price']:.2f}")
        print(f"  Exit:   {trade['exit_time']} @ ${trade['exit_price']:.2f}")
        print(f"  Return: {trade['return_pct']:+.2f}%")
        print(f"  P&L:    ${trade['pnl']:+.2f}\n")
else:
    print("\nNo trades executed")

# Show equity curve summary
equity = detailed_results['equity_curve']
print("\nPortfolio Value Over Time:")
print(f"  Starting: ${equity['portfolio_value'].iloc[0]:,.2f}")
print(f"  Ending:   ${equity['portfolio_value'].iloc[-1]:,.2f}")
print(f"  Peak:     ${equity['portfolio_value'].max():,.2f}")
print(f"  Trough:   ${equity['portfolio_value'].min():,.2f}")