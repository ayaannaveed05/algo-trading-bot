"""Bollinger Bands Breakout trading strategy"""

from .base_strategy import BaseStrategy
import pandas as pd


class BollingerBands(BaseStrategy):
    """Strategy that buys near lower band, sells near upper band"""
    
    def __init__(self, period=20, std_dev=2):
        """
        Initialize Bollinger Bands strategy
        
        Args:
            period: Number of periods for moving average
            std_dev: Standard deviations for bands
        """
        super().__init__(f"BollingerBands_{period}_{std_dev}")
        self.period = period
        self.std_dev = std_dev
    
    def generate_signals(self, df):
        """Generate BUY/SELL signals based on Bollinger Band position"""
        
        # Make copy to avoid modifying original
        df = df.copy()
        
        # Calculate Bollinger Bands if not present
        if f'bb_middle_{self.period}' not in df.columns:
            # Middle band (SMA)
            df[f'bb_middle_{self.period}'] = df['close'].rolling(window=self.period).mean()
            
            # Standard deviation
            rolling_std = df['close'].rolling(window=self.period).std()
            
            # Upper and lower bands
            df[f'bb_upper_{self.period}'] = df[f'bb_middle_{self.period}'] + (rolling_std * self.std_dev)
            df[f'bb_lower_{self.period}'] = df[f'bb_middle_{self.period}'] - (rolling_std * self.std_dev)
        
        # Calculate %B indicator (where price is relative to bands)
        # %B = (close - lower) / (upper - lower)
        # %B = 0 means price at lower band
        # %B = 1 means price at upper band
        # %B = 0.5 means price at middle
        band_width = df[f'bb_upper_{self.period}'] - df[f'bb_lower_{self.period}']
        df['percent_b'] = (df['close'] - df[f'bb_lower_{self.period}']) / band_width
        
        # Initialize signal column
        df['signal'] = 0
        
        # BUY when %B < 0.2 (price in lower 20% of band - oversold)
        df.loc[df['percent_b'] < 0.2, 'signal'] = 1
        
        # SELL when %B > 0.8 (price in upper 20% of band - overbought)
        df.loc[df['percent_b'] > 0.8, 'signal'] = -1
        
        # HOLD when in middle zone (0.2 to 0.8)
        df.loc[(df['percent_b'] >= 0.2) & (df['percent_b'] <= 0.8), 'signal'] = 0
        
        # Detect signal changes
        df['position'] = df['signal'].diff()
        
        return df