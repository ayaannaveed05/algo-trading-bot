from utils.analysis import DataAnalyzer
from datetime import datetime, timedelta

analyzer = DataAnalyzer()

# Get data from database
symbol = 'SPY'
end = datetime.now()
start = end - timedelta(days=7)

print(f"Loading {symbol} data from database...")
df = analyzer.get_df(symbol, start, end, interval='1m')
print(f"✓ Loaded {len(df)} bars\n")

# Add technical indicators
print("Adding technical indicators...")
df = analyzer.add_returns(df)
df = analyzer.add_sma(df, period=10)
df = analyzer.add_sma(df, period=50)
df = analyzer.add_rsi(df, period=14)
df = analyzer.add_bollinger_bands(df, period=20)
print("✓ Added: returns, SMA(10), SMA(50), RSI(14), Bollinger Bands\n")

# Show sample data
print("Sample data with indicators:")
print(df[['close', 'sma_10', 'sma_50', 'rsi_14', 'bb_upper_20', 'bb_lower_20']].tail(10))

# Calculate metrics
print("\n" + "="*50)
print("SUMMARY METRICS")
print("="*50)
metrics = analyzer.calculate_metrics(df)
for key, value in metrics.items():
    if 'return' in key or 'volatility' in key:
        print(f"{key:20s}: {value:8.3f}%")
    elif 'price' in key:
        print(f"{key:20s}: ${value:8.2f}")
    else:
        print(f"{key:20s}: {value:12,.0f}")