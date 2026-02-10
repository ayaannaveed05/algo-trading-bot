"""Yahoo Finance data provider implementation"""

import yfinance as yf
import pandas as pd
from datetime import datetime
from .base import DataProvider


class YahooProvider(DataProvider):
    """Fetches market data from Yahoo Finance"""
    
    def get_bars(self, symbol: str, start: datetime, end: datetime, interval: str = '1m') -> pd.DataFrame:
        """Download historical bars from Yahoo Finance API"""
        
        print(f"Fetching {symbol} from Yahoo Finance: {start} to {end}, interval={interval}")
        
        # Create ticker object for the symbol
        ticker = yf.Ticker(symbol)
        
        # Download historical data for the date range
        df = ticker.history(start=start, end=end, interval=interval)
        
        # Standardize column names to lowercase
        df.columns = [col.lower() for col in df.columns]
        
        # Keep only OHLCV columns
        df = df[['open', 'high', 'low', 'close', 'volume']]
        
        print(f"✓ Fetched {len(df)} bars")
        return df