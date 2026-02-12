"""RSI Mean Reversion trading strategy"""

from .base_strategy import BaseStrategy
import pandas as pd


class RSIMeanReversion(BaseStrategy):
    """Strategy that buys when RSI is oversold, sells when overbought"""
    
    def __init__(self, rsi_period=14, oversold=30, overbought=70):
        """Initialize with RSI parameters"""
        super().__init__(f"RSI_MeanReversion_{rsi_period}_{oversold}_{overbought}")
        self.rsi_period = rsi_period
        self.oversold = oversold  # Buy threshold
        self.overbought = overbought  # Sell threshold
    
    def generate_signals(self, df):
        """Generate BUY/SELL signals based on RSI levels"""
        
        # Make copy to avoid modifying original
        df = df.copy()
        
        # Calculate RSI if not present
        if f'rsi_{self.rsi_period}' not in df.columns:
            # Calculate price changes
            delta = df['close'].diff()
            
            # Separate gains and losses
            gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
            
            # Calculate RSI
            rs = gain / loss
            df[f'rsi_{self.rsi_period}'] = 100 - (100 / (1 + rs))
        
        # Initialize signal column
        df['signal'] = 0
        
        # BUY when RSI < oversold threshold (price too low, expect bounce)
        df.loc[df[f'rsi_{self.rsi_period}'] < self.oversold, 'signal'] = 1
        
        # SELL when RSI > overbought threshold (price too high, expect drop)
        df.loc[df[f'rsi_{self.rsi_period}'] > self.overbought, 'signal'] = -1
        
        # Detect signal changes
        df['position'] = df['signal'].diff()
        
        return df