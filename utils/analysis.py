import pandas as pd
import numpy as np
from database.models import DatabaseManager

class DataAnalyzer:
    """Helper functions for analyzing market data"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def bars_to_dataframe(self, bars):
        """Convert list of MarketBar objects to DataFrame"""
        data = {
            'timestamp': [bar.timestamp for bar in bars],
            'open': [bar.open for bar in bars],
            'high': [bar.high for bar in bars],
            'low': [bar.low for bar in bars],
            'close': [bar.close for bar in bars],
            'volume': [bar.volume for bar in bars],
        }
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
    
    def get_df(self, symbol, start, end, interval='1m'):
        """Get bars as DataFrame from database"""
        bars = self.db.get_bars(symbol, start, end, interval)
        return self.bars_to_dataframe(bars)
    
    def add_returns(self, df):
        """Add returns column"""
        df['returns'] = df['close'].pct_change()
        return df
    
    def add_sma(self, df, period, column='close'):
        """Add Simple Moving Average"""
        df[f'sma_{period}'] = df[column].rolling(window=period).mean()
        return df
    
    def add_ema(self, df, period, column='close'):
        """Add Exponential Moving Average"""
        df[f'ema_{period}'] = df[column].ewm(span=period, adjust=False).mean()
        return df
    
    def add_rsi(self, df, period=14, column='close'):
        """Add Relative Strength Index"""
        delta = df[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df[f'rsi_{period}'] = 100 - (100 / (1 + rs))
        return df
    
    def add_bollinger_bands(self, df, period=20, std=2, column='close'):
        """Add Bollinger Bands"""
        df[f'bb_middle_{period}'] = df[column].rolling(window=period).mean()
        rolling_std = df[column].rolling(window=period).std()
        df[f'bb_upper_{period}'] = df[f'bb_middle_{period}'] + (rolling_std * std)
        df[f'bb_lower_{period}'] = df[f'bb_middle_{period}'] - (rolling_std * std)
        return df
    
    def calculate_metrics(self, df):
        """Calculate summary metrics"""
        if 'returns' not in df.columns:
            df = self.add_returns(df)
        
        metrics = {
            'total_return': (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100,
            'avg_return': df['returns'].mean() * 100,
            'volatility': df['returns'].std() * 100,
            'max_price': df['close'].max(),
            'min_price': df['close'].min(),
            'avg_volume': df['volume'].mean(),
        }
        return metrics