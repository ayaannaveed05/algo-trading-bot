from data.providers.yahoo import YahooProvider
from datetime import datetime, timedelta

# Initialize provider
provider = YahooProvider()

# Fetching 1 week of SPY data
symbol = 'SPY'
end = datetime.now()
start = end - timedelta(days=7)

bars = provider.get_bars(symbol, start, end, interval='1m')

print(f"\nSuccessfully fetched {len(bars)} bars")
print("\nFirst 5 rows:")
print(bars.head())
print("\nLast 5 rows:")
print(bars.tail())
print(f"\nColumns: {bars.columns.tolist()}")
print(f"Date range: {bars.index.min()} to {bars.index.max()}")