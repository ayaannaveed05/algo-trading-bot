"""Helper functions for analyzing market data and calculating indicators"""

import pandas as pd
import numpy as np
from database.models import DatabaseManager


class DataAnalyzer:
    """Provides functions for loading data and adding technical indicators"""
    
    def __init__(self):
        """Initialize with database connection"""
        self.db = DatabaseManager()
    
    def bars_to_dataframe(self, bars):
        """Convert list of MarketBar objects to pandas DataFrame"""
        
        # Extract fields from each bar into dictionary
        data = {
            'timestamp': [bar.timestamp for bar in bars],
            'open': [bar.open for bar in bars],
            'high': [bar.high for bar in bars],
            'low': [bar.low for bar in bars],
            'close': [bar.close for bar in bars],
            'volume': [bar.volume for bar in bars],
        }
        
        # Create DataFrame and set timestamp as index
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def get_df(self, symbol, start, end, interval='1m'):
        """Load bars from database as DataFrame"""
        
        # Get bars from database
        bars = self.db.get_bars(symbol, start, end, interval)
        
        # Convert to DataFrame
        return self.bars_to_dataframe(bars)
    
    def add_returns(self, df):
        """Add percentage returns column (period-over-period change)"""
        df['returns'] = df['close'].pct_change()
        return df
    
    def add_sma(self, df, period, column='close'):
        """Add Simple Moving Average for given period"""
        df[f'sma_{period}'] = df[column].rolling(window=period).mean()
        return df
    
    def add_ema(self, df, period, column='close'):
        """Add Exponential Moving Average (weighted towards recent prices)"""
        df[f'ema_{period}'] = df[column].ewm(span=period, adjust=False).mean()
        return df
    
    def add_rsi(self, df, period=14, column='close'):
        """Add Relative Strength Index (0-100 momentum indicator)"""
        
        # Calculate price changes
        delta = df[column].diff()
        
        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Calculate relative strength and RSI
        rs = gain / loss
        df[f'rsi_{period}'] = 100 - (100 / (1 + rs))
        
        return df
    
    def add_bollinger_bands(self, df, period=20, std=2, column='close'):
        """Add Bollinger Bands (volatility channel around SMA)"""
        
        # Middle band is the SMA
        df[f'bb_middle_{period}'] = df[column].rolling(window=period).mean()
        
        # Calculate standard deviation
        rolling_std = df[column].rolling(window=period).std()
        
        # Upper band = middle + (std_multiplier * rolling_std)
        df[f'bb_upper_{period}'] = df[f'bb_middle_{period}'] + (rolling_std * std)
        
        # Lower band = middle - (std_multiplier * rolling_std)
        df[f'bb_lower_{period}'] = df[f'bb_middle_{period}'] - (rolling_std * std)
        
        return df
    
    def calculate_metrics(self, df):
        """Calculate summary performance metrics"""
        
        # Ensure returns column exists
        if 'returns' not in df.columns:
            df = self.add_returns(df)
        
        # Calculate various metrics
        metrics = {
            'total_return': (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100,  # Overall return
            'avg_return': df['returns'].mean() * 100,  # Mean return per period
            'volatility': df['returns'].std() * 100,  # Standard deviation of returns
            'max_price': df['close'].max(),  # Highest price
            'min_price': df['close'].min(),  # Lowest price
            'avg_volume': df['volume'].mean(),  # Average volume
        }
        
        return metrics