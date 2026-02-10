"""Moving Average Crossover trading strategy"""

from .base_strategy import BaseStrategy
import pandas as pd


class MovingAverageCrossover(BaseStrategy):
    """Strategy that buys when fast MA crosses above slow MA, sells when it crosses below"""
    
    def __init__(self, short_period=10, long_period=50):
        """Initialize with short and long MA periods"""
        super().__init__(f"MA_Crossover_{short_period}_{long_period}")
        self.short_period = short_period
        self.long_period = long_period
    
    def generate_signals(self, df):
        """Generate BUY/SELL signals based on MA crossovers"""
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Calculate short MA if not present
        if f'sma_{self.short_period}' not in df.columns:
            df[f'sma_{self.short_period}'] = df['close'].rolling(window=self.short_period).mean()
        
        # Calculate long MA if not present
        if f'sma_{self.long_period}' not in df.columns:
            df[f'sma_{self.long_period}'] = df['close'].rolling(window=self.long_period).mean()
        
        # Initialize signal column to 0 (neutral)
        df['signal'] = 0
        
        # BUY signal (1) when short MA > long MA (uptrend)
        df.loc[df[f'sma_{self.short_period}'] > df[f'sma_{self.long_period}'], 'signal'] = 1
        
        # SELL signal (-1) when short MA < long MA (downtrend)
        df.loc[df[f'sma_{self.short_period}'] < df[f'sma_{self.long_period}'], 'signal'] = -1
        
        # Detect crossovers (position = 2 means crossed up, -2 means crossed down)
        df['position'] = df['signal'].diff()
        
        return df