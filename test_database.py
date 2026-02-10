from data.providers.yahoo import YahooProvider
from database.models import DatabaseManager
from datetime import datetime, timedelta
import pandas as pd

# Initialize
provider = YahooProvider()
db = DatabaseManager()

# Fetch and save data
symbol = 'SPY'
end = datetime.now()
start = end - timedelta(days=7)

print(f"Fetching {symbol} data...")
bars = provider.get_bars(symbol, start, end, interval='1m')

print(f"\nSaving to database...")
db.save_bars(symbol, bars, interval='1m')

# Retrieve from database to verify
print(f"\nRetrieving from database...")
saved_bars = db.get_bars(symbol, start, end, interval='1m')
print(f"✓ Retrieved {len(saved_bars)} bars from database")

print(f"\nFirst 3 bars from database:")
for bar in saved_bars[:3]:
    print(f"  {bar.timestamp}: close=${bar.close:.2f}, volume={bar.volume:,}")

print(f"\nLast 3 bars from database:")
for bar in saved_bars[-3:]:
    print(f"  {bar.timestamp}: close=${bar.close:.2f}, volume={bar.volume:,}")