"""Abstract base class for all trading strategies"""

from abc import ABC, abstractmethod
import pandas as pd


class BaseStrategy(ABC):
    """Interface that all trading strategies must implement"""
    
    def __init__(self, name):
        """Initialize strategy with a name"""
        self.name = name
    
    @abstractmethod
    def generate_signals(self, df):
        """Generate trading signals (1=BUY, -1=SELL, 0=HOLD) from market data"""
        pass
    
    def __repr__(self):
        return f"<Strategy: {self.name}>"