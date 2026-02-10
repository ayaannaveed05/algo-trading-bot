from utils.analysis import DataAnalyzer
from strategies.moving_average import MovingAverageCrossover
from datetime import datetime, timedelta
import pandas as pd

# Initialize
analyzer = DataAnalyzer()
strategy = MovingAverageCrossover(short_period=10, long_period=50)

# Get data
symbol = 'SPY'
end = datetime.now()
start = end - timedelta(days=7)

print(f"Loading {symbol} data...")
df = analyzer.get_df(symbol, start, end, interval='1m')
print(f"✓ Loaded {len(df)} bars\n")

# Generate signals
print(f"Generating signals for {strategy.name}...")
df = strategy.generate_signals(df)
print(f"✓ Signals generated\n")

# Analyze signals
buy_signals = (df['position'] == 2).sum()
sell_signals = (df['position'] == -2).sum()
currently_long = df['signal'].iloc[-1] == 1
currently_short = df['signal'].iloc[-1] == -1

print("="*60)
print("STRATEGY PERFORMANCE")
print("="*60)
print(f"Strategy:        {strategy.name}")
print(f"Period:          {df.index[0]} to {df.index[-1]}")
print(f"Total bars:      {len(df)}")
print(f"Buy signals:     {buy_signals}")
print(f"Sell signals:    {sell_signals}")
print(f"Current position: {'LONG (holding)' if currently_long else 'SHORT (not holding)' if currently_short else 'NEUTRAL'}")

# Show recent signals
print("\n" + "="*60)
print("RECENT CROSSOVERS (Last 10)")
print("="*60)

crossovers = df[df['position'].abs() == 2].tail(10)
if len(crossovers) > 0:
    for idx, row in crossovers.iterrows():
        signal_type = "BUY (↑)" if row['position'] == 2 else "SELL (↓)"
        print(f"{idx}: {signal_type:10s} | Price: ${row['close']:.2f} | SMA10: ${row['sma_10']:.2f} | SMA50: ${row['sma_50']:.2f}")
else:
    print("No crossovers in this period")

# Show current status
print("\n" + "="*60)
print("CURRENT STATUS")
print("="*60)
latest = df.iloc[-1]
print(f"Timestamp:       {df.index[-1]}")
print(f"Close price:     ${latest['close']:.2f}")
print(f"SMA(10):         ${latest['sma_10']:.2f}")
print(f"SMA(50):         ${latest['sma_50']:.2f}")
print(f"Signal:          {'BUY/LONG' if latest['signal'] == 1 else 'SELL/SHORT' if latest['signal'] == -1 else 'NEUTRAL'}")

# Simple P&L calculation (if we traded every signal)
print("\n" + "="*60)
print("HYPOTHETICAL P&L (if traded every crossover)")
print("="*60)

# Calculate returns from each crossover
if len(crossovers) > 1:
    total_return = 0
    trades = []
    
    crossover_list = crossovers.reset_index()
    for i in range(len(crossover_list) - 1):
        entry = crossover_list.iloc[i]
        exit = crossover_list.iloc[i + 1]
        
        if entry['position'] == 2:  # Entered long
            pnl = ((exit['close'] - entry['close']) / entry['close']) * 100
            trades.append({
                'entry_time': entry['timestamp'],
                'exit_time': exit['timestamp'],
                'entry_price': entry['close'],
                'exit_price': exit['close'],
                'return': pnl
            })
    
    if trades:
        for i, trade in enumerate(trades, 1):
            print(f"\nTrade {i}:")
            print(f"  Entry: {trade['entry_time']} @ ${trade['entry_price']:.2f}")
            print(f"  Exit:  {trade['exit_time']} @ ${trade['exit_price']:.2f}")
            print(f"  Return: {trade['return']:+.3f}%")
        
        total_return = sum(t['return'] for t in trades)
        win_rate = len([t for t in trades if t['return'] > 0]) / len(trades) * 100
        
        print("\n" + "-"*60)
        print(f"Total trades:    {len(trades)}")
        print(f"Total return:    {total_return:+.3f}%")
        print(f"Avg per trade:   {total_return/len(trades):+.3f}%")
        print(f"Win rate:        {win_rate:.1f}%")
else:
    print("Not enough crossovers to calculate P&L")