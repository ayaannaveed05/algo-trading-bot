"""Test Bollinger Bands strategy"""

from utils.analysis import DataAnalyzer
from strategies.bollinger_bands import BollingerBands
from backtesting.engine import Backtester
from datetime import datetime, timedelta

# Load NVDA data (we already have it in database)
analyzer = DataAnalyzer()
symbol = 'NVDA'
end = datetime.now()
start = end - timedelta(days=180)

print("="*70)
print(f"TESTING BOLLINGER BANDS ON {symbol}")
print("="*70)

df = analyzer.get_df(symbol, start, end, interval='1d')
print(f"✓ Loaded {len(df)} bars\n")

# Test multiple Bollinger Band configurations
strategies = [
    BollingerBands(period=10, std_dev=2),   # Fast, tight
    BollingerBands(period=20, std_dev=2),   # Standard
    BollingerBands(period=20, std_dev=3),   # Standard, wider
    BollingerBands(period=30, std_dev=2),   # Slow
]

# Run backtests
backtester = Backtester(initial_capital=10000, commission=0.001, slippage=0.001)

print("="*70)
print("RUNNING BACKTESTS")
print("="*70)

comparison = backtester.compare_strategies(strategies, df)

# Display results
print("\n" + "="*70)
print("BOLLINGER BANDS STRATEGY COMPARISON")
print("="*70)
print(comparison.to_string(index=False))

# Find best
active = comparison[comparison['total_trades'] > 0]

if len(active) > 0:
    best = active.loc[active['total_return'].idxmax()]
    
    print("\n" + "="*70)
    print("BEST CONFIGURATION")
    print("="*70)
    print(f"\nStrategy: {best['strategy']}")
    print(f"Return: {best['total_return']:+.2f}%")
    print(f"Trades: {int(best['total_trades'])}")
    print(f"Win Rate: {best['win_rate']:.1f}%")
    print(f"Sharpe: {best['sharpe_ratio']:.2f}")
    print(f"Max DD: {best['max_drawdown']:.2f}%")
    
    # Show trades
    best_strategy = [s for s in strategies if s.name == best['strategy']][0]
    results = backtester.run_backtest(best_strategy, df.copy())
    
    print(f"\nTrade History ({len(results['trades'])} trades):")
    for i, trade in enumerate(results['trades'][:10], 1):
        status = "✓" if trade['return_pct'] > 0 else "✗"
        print(f"{i:2d}. {trade['entry_time'].date()} → {trade['exit_time'].date()}: "
              f"{trade['return_pct']:+6.2f}% {status}")
    
    if len(results['trades']) > 10:
        print(f"... and {len(results['trades']) - 10} more")
else:
    print("\n⚠️  No trades generated")