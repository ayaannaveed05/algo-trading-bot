"""Master comparison of all strategies across multiple assets"""

from utils.analysis import DataAnalyzer
from strategies.moving_average import MovingAverageCrossover
from strategies.rsi_strategy import RSIMeanReversion
from strategies.bollinger_bands import BollingerBands
from backtesting.engine import Backtester
from datetime import datetime, timedelta
import pandas as pd

# Load data for multiple symbols
analyzer = DataAnalyzer()
end = datetime.now()
start = end - timedelta(days=180)

symbols = ['NVDA', 'SPY']

print("="*80)
print("COMPREHENSIVE STRATEGY COMPARISON")
print("="*80)

# All strategies to test
all_strategies = [
    # Moving Average Crossover
    MovingAverageCrossover(5, 20),
    MovingAverageCrossover(10, 30),
    
    # RSI Mean Reversion
    RSIMeanReversion(14, 30, 70),
    RSIMeanReversion(14, 40, 60),
    
    # Bollinger Bands
    BollingerBands(10, 2),
    BollingerBands(20, 2),
    BollingerBands(20, 3),
]

# Initialize backtester
backtester = Backtester(initial_capital=10000, commission=0.001, slippage=0.001)

# Store all results
all_results = []

# Test each symbol
for symbol in symbols:
    print(f"\n{'='*80}")
    print(f"TESTING ON {symbol}")
    print(f"{'='*80}")
    
    # Load data
    df = analyzer.get_df(symbol, start, end, interval='1d')
    print(f"✓ Loaded {len(df)} bars from {df.index[0].date()} to {df.index[-1].date()}\n")
    
    # Run all strategies
    comparison = backtester.compare_strategies(all_strategies, df)
    
    # Add symbol column
    comparison['symbol'] = symbol
    
    # Append to results
    all_results.append(comparison)
    
    # Show top 3 for this symbol
    active = comparison[comparison['total_trades'] > 0].copy()
    if len(active) > 0:
        active_sorted = active.sort_values('total_return', ascending=False)
        
        print(f"\nTOP 3 STRATEGIES FOR {symbol}:")
        print("-"*80)
        for i, (idx, row) in enumerate(active_sorted.head(3).iterrows(), 1):
            print(f"{i}. {row['strategy']}")
            print(f"   Return: {row['total_return']:+.2f}% | "
                  f"Trades: {int(row['total_trades'])} | "
                  f"Win Rate: {row['win_rate']:.1f}% | "
                  f"Sharpe: {row['sharpe_ratio']:.2f}")

# Combine all results
combined = pd.concat(all_results, ignore_index=True)

# Find overall best strategies
print(f"\n{'='*80}")
print("OVERALL BEST STRATEGIES (ACROSS ALL ASSETS)")
print(f"{'='*80}")

# Filter to strategies that actually traded
active_all = combined[combined['total_trades'] > 0].copy()

if len(active_all) > 0:
    # Sort by return
    best_performers = active_all.sort_values('total_return', ascending=False).head(5)
    
    print("\nTop 5 by Return:")
    for i, (idx, row) in enumerate(best_performers.iterrows(), 1):
        print(f"\n{i}. {row['strategy']} on {row['symbol']}")
        print(f"   Return: {row['total_return']:+.2f}%")
        print(f"   Trades: {int(row['total_trades'])}")
        print(f"   Win Rate: {row['win_rate']:.1f}%")
        print(f"   Sharpe: {row['sharpe_ratio']:.2f}")
        print(f"   Max DD: {row['max_drawdown']:.2f}%")

# Save results to CSV
output_file = 'strategy_comparison_results.csv'
combined.to_csv(output_file, index=False)
print(f"\n{'='*80}")
print(f"✓ Results saved to {output_file}")
print(f"{'='*80}")