"""Generate charts for strategy performance"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from utils.analysis import DataAnalyzer
from strategies.bollinger_bands import BollingerBands
from strategies.moving_average import MovingAverageCrossover
from backtesting.engine import Backtester
from datetime import datetime, timedelta
import pandas as pd

# Load data
analyzer = DataAnalyzer()
end = datetime.now()
start = end - timedelta(days=180)

symbol = 'NVDA'
df = analyzer.get_df(symbol, start, end, interval='1d')

# Run backtests
backtester = Backtester(initial_capital=10000, commission=0.001, slippage=0.001)

strategies = [
    BollingerBands(period=10, std_dev=2),
    BollingerBands(period=20, std_dev=2),
    MovingAverageCrossover(short_period=5, long_period=20),
]

# Create figure with subplots
fig, axes = plt.subplots(3, 1, figsize=(14, 16))
fig.suptitle(f'Strategy Performance Comparison - {symbol} (6 Months)', 
             fontsize=16, fontweight='bold', y=0.98)

# Color scheme
colors = ['#2196F3', '#4CAF50', '#F44336']
labels = ['Bollinger Bands 10/2', 'Bollinger Bands 20/2', 'MA Crossover 5/20']

# ============================================================
# CHART 1: Equity Curves
# ============================================================
ax1 = axes[0]
ax1.set_title('Portfolio Value Over Time ($10,000 Starting Capital)', 
              fontsize=12, fontweight='bold')

for i, strategy in enumerate(strategies):
    result = backtester.run_backtest(strategy, df.copy())
    equity = result['equity_curve']
    
    # Plot equity curve
    ax1.plot(
        equity['timestamp'],
        equity['portfolio_value'],
        color=colors[i],
        label=f"{labels[i]} ({result['metrics']['total_return']:+.1f}%)",
        linewidth=2
    )

# Add starting capital reference line
ax1.axhline(y=10000, color='gray', linestyle='--', alpha=0.5, label='Starting Capital')
ax1.set_ylabel('Portfolio Value ($)')
ax1.legend(loc='upper left', fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# ============================================================
# CHART 2: NVDA Price with Bollinger Bands
# ============================================================
ax2 = axes[1]
ax2.set_title('NVDA Price with Bollinger Bands (Best Strategy)', 
              fontsize=12, fontweight='bold')

# Calculate Bollinger Bands
period = 10
df_bb = df.copy()
df_bb['bb_middle'] = df_bb['close'].rolling(window=period).mean()
rolling_std = df_bb['close'].rolling(window=period).std()
df_bb['bb_upper'] = df_bb['bb_middle'] + (rolling_std * 2)
df_bb['bb_lower'] = df_bb['bb_middle'] - (rolling_std * 2)
df_bb['percent_b'] = (df_bb['close'] - df_bb['bb_lower']) / (df_bb['bb_upper'] - df_bb['bb_lower'])

# Plot price and bands
ax2.plot(df_bb.index, df_bb['close'], color='black', linewidth=1.5, label='NVDA Price', zorder=5)
ax2.plot(df_bb.index, df_bb['bb_upper'], color='#F44336', linewidth=1, linestyle='--', alpha=0.7, label='Upper Band')
ax2.plot(df_bb.index, df_bb['bb_middle'], color='gray', linewidth=1, linestyle='--', alpha=0.7, label='Middle Band')
ax2.plot(df_bb.index, df_bb['bb_lower'], color='#2196F3', linewidth=1, linestyle='--', alpha=0.7, label='Lower Band')

# Shade band area
ax2.fill_between(df_bb.index, df_bb['bb_upper'], df_bb['bb_lower'], alpha=0.1, color='gray')

# Plot buy/sell signals
best_strategy = BollingerBands(period=10, std_dev=2)
df_signals = best_strategy.generate_signals(df.copy())

# Mark buy signals (green triangles pointing up)
buy_signals = df_signals[df_signals['signal'] == 1]
ax2.scatter(buy_signals.index, buy_signals['close'], 
           color='#4CAF50', marker='^', s=100, zorder=10, label='Buy Signal')

# Mark sell signals (red triangles pointing down)
sell_signals = df_signals[df_signals['signal'] == -1]
ax2.scatter(sell_signals.index, sell_signals['close'], 
           color='#F44336', marker='v', s=100, zorder=10, label='Sell Signal')

ax2.set_ylabel('Price ($)')
ax2.legend(loc='upper left', fontsize=9)
ax2.grid(True, alpha=0.3)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.0f}'))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# ============================================================
# CHART 3: Strategy Comparison Bar Chart
# ============================================================
ax3 = axes[2]
ax3.set_title('Strategy Returns Comparison', fontsize=12, fontweight='bold')

# All strategies data
strategy_names = [
    'BB 10/2\n(NVDA)', 'BB 20/2\n(NVDA)', 'RSI 40/60\n(NVDA)',
    'BB 20/3\n(SPY)', 'BB 20/2\n(SPY)', 'MA 5/20\n(NVDA)'
]
returns = [22.34, 18.03, 14.26, 4.03, 3.49, -19.80]
bar_colors = ['#4CAF50' if r > 0 else '#F44336' for r in returns]

bars = ax3.bar(strategy_names, returns, color=bar_colors, edgecolor='white', linewidth=0.5)

# Add value labels on bars
for bar, ret in zip(bars, returns):
    height = bar.get_height()
    ax3.text(
        bar.get_x() + bar.get_width() / 2.,
        height + (0.5 if height >= 0 else -1.5),
        f'{ret:+.1f}%',
        ha='center', va='bottom' if height >= 0 else 'top',
        fontweight='bold', fontsize=10
    )

ax3.axhline(y=0, color='black', linewidth=0.8)
ax3.set_ylabel('Total Return (%)')
ax3.grid(True, alpha=0.3, axis='y')

# Adjust layout
plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save chart
output_file = 'strategy_performance.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✓ Chart saved to {output_file}")

plt.show()
print("✓ Charts generated successfully")