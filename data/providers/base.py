"""Abstract base class for all data providers"""

from abc import ABC, abstractmethod # for creating the abstract class
import pandas as pd
from datetime import datetime


class DataProvider(ABC):
    """Interface that all data providers must implement"""
    
    @abstractmethod
    def get_bars(self, symbol: str, start: datetime, end: datetime, interval: str) -> pd.DataFrame:
        """Fetch OHLCV bars for a symbol between start and end dates"""
        pass