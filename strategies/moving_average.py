from .base_strategy import BaseStrategy
import pandas as pd

class MovingAverageCrossover(BaseStrategy):
    """
    Moving Average Crossover Strategy
    
    Signals:
    - BUY: When short MA crosses above long MA
    - SELL: When short MA crosses below long MA
    """
    
    def __init__(self, short_period=10, long_period=50):
        super().__init__(f"MA_Crossover_{short_period}_{long_period}")
        self.short_period = short_period
        self.long_period = long_period
    
    def generate_signals(self, df):
        """Generate trading signals based on MA crossover"""
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Calculate moving averages if not already present
        if f'sma_{self.short_period}' not in df.columns:
            df[f'sma_{self.short_period}'] = df['close'].rolling(window=self.short_period).mean()
        
        if f'sma_{self.long_period}' not in df.columns:
            df[f'sma_{self.long_period}'] = df['close'].rolling(window=self.long_period).mean()
        
        # Initialize signal column
        df['signal'] = 0
        
        # Generate signals
        # BUY (1): Short MA > Long MA
        df.loc[df[f'sma_{self.short_period}'] > df[f'sma_{self.long_period}'], 'signal'] = 1
        
        # SELL (-1): Short MA < Long MA
        df.loc[df[f'sma_{self.short_period}'] < df[f'sma_{self.long_period}'], 'signal'] = -1
        
        # Detect crossovers (when signal changes)
        df['position'] = df['signal'].diff()
        # position = 2: crossed from SELL to BUY (strong buy)
        # position = -2: crossed from BUY to SELL (strong sell)
        
        return df