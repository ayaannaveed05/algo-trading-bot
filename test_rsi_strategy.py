"""Test script for RSI Mean Reversion strategy"""

from utils.analysis import DataAnalyzer
from strategies.rsi_strategy import RSIMeanReversion
from datetime import datetime, timedelta

# Initialize analyzer and strategy
analyzer = DataAnalyzer()
strategy = RSIMeanReversion(rsi_period=14, oversold=40, overbought=60)

# Load data
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

# Count signals
buy_signals = (df['position'] == 2).sum()
sell_signals = (df['position'] == -2).sum()
currently_long = df['signal'].iloc[-1] == 1
currently_short = df['signal'].iloc[-1] == -1

# Display performance
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
print("RECENT RSI SIGNALS (Last 10)")
print("="*60)

signals = df[df['position'].abs() == 2].tail(10)
if len(signals) > 0:
    for idx, row in signals.iterrows():
        signal_type = "BUY (oversold)" if row['position'] == 2 else "SELL (overbought)"
        print(f"{idx}: {signal_type:20s} | Price: ${row['close']:.2f} | RSI: {row['rsi_14']:.1f}")
else:
    print("No signals in this period")

# Current status
print("\n" + "="*60)
print("CURRENT STATUS")
print("="*60)
latest = df.iloc[-1]
print(f"Timestamp:       {df.index[-1]}")
print(f"Close price:     ${latest['close']:.2f}")
print(f"RSI(14):         {latest['rsi_14']:.1f}")
print(f"Signal:          {'BUY (oversold)' if latest['signal'] == 1 else 'SELL (overbought)' if latest['signal'] == -1 else 'NEUTRAL'}")

# Calculate P&L
print("\n" + "="*60)
print("HYPOTHETICAL P&L")
print("="*60)

if len(signals) > 1:
    trades = []
    signal_list = signals.reset_index()
    
    # Calculate returns for each trade
    for i in range(len(signal_list) - 1):
        entry = signal_list.iloc[i]
        exit = signal_list.iloc[i + 1]
        
        if entry['position'] == 2:  # Entered long
            pnl = ((exit['close'] - entry['close']) / entry['close']) * 100
            trades.append({
                'entry_time': entry['timestamp'],
                'exit_time': exit['timestamp'],
                'entry_price': entry['close'],
                'exit_price': exit['close'],
                'entry_rsi': entry['rsi_14'],
                'exit_rsi': exit['rsi_14'],
                'return': pnl
            })
    
    # Display trades
    if trades:
        for i, trade in enumerate(trades, 1):
            print(f"\nTrade {i}:")
            print(f"  Entry: {trade['entry_time']} @ ${trade['entry_price']:.2f} (RSI: {trade['entry_rsi']:.1f})")
            print(f"  Exit:  {trade['exit_time']} @ ${trade['exit_price']:.2f} (RSI: {trade['exit_rsi']:.1f})")
            print(f"  Return: {trade['return']:+.3f}%")
        
        # Summary stats
        total_return = sum(t['return'] for t in trades)
        win_rate = len([t for t in trades if t['return'] > 0]) / len(trades) * 100
        
        print("\n" + "-"*60)
        print(f"Total trades:    {len(trades)}")
        print(f"Total return:    {total_return:+.3f}%")
        print(f"Avg per trade:   {total_return/len(trades):+.3f}%")
        print(f"Win rate:        {win_rate:.1f}%")
else:
    print("Not enough signals to calculate P&L")