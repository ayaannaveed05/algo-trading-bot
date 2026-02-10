from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name):
        self.name = name
    
    @abstractmethod
    def generate_signals(self, df):
        """
        Generate trading signals from data
        
        Args:
            df: DataFrame with OHLCV data and any indicators
        
        Returns:
            DataFrame with additional 'signal' column:
                1 = BUY
                -1 = SELL
                0 = HOLD
        """
        pass
    
    def __repr__(self):
        return f"<Strategy: {self.name}>"