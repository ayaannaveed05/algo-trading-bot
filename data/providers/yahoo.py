import yfinance as yf
import pandas as pd
from datetime import datetime
from .base import DataProvider

class YahooProvider(DataProvider):
    """Yahoo Finance data provider"""
    
    def get_bars(self, symbol: str, start: datetime, end: datetime, interval: str = '1m') -> pd.DataFrame:
        """Fetch bars from Yahoo Finance"""
        print(f"Fetching {symbol} from Yahoo Finance: {start} to {end}, interval={interval}")
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, interval=interval)
        
        # Standardize column names (lowercase)
        df.columns = [col.lower() for col in df.columns]
        
        # Keep only OHLCV
        df = df[['open', 'high', 'low', 'close', 'volume']]
        
        print(f"✓ Fetched {len(df)} bars")
        return df