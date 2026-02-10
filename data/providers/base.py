from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime

class DataProvider(ABC):
    """Abstract base class for data providers"""
    
    @abstractmethod
    def get_bars(self, symbol: str, start: datetime, end: datetime, interval: str) -> pd.DataFrame:
        """
        Fetch OHLCV bars for a symbol
        
        Args:
            symbol: Stock ticker (e.g., 'SPY')
            start: Start datetime
            end: End datetime
            interval: Bar interval ('1m', '5m', '1h', '1d')
        
        Returns:
            DataFrame with columns: open, high, low, close, volume
        """
        pass