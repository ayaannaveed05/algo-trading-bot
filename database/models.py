"""Database models and manager for storing market data"""

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class MarketBar(Base):
    """Database model for a single OHLCV bar"""
    
    __tablename__ = 'market_bars'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Market data fields
    symbol = Column(String(10), nullable=False)  # Stock ticker
    timestamp = Column(DateTime, nullable=False)  # Bar timestamp
    open = Column(Float, nullable=False)  # Opening price
    high = Column(Float, nullable=False)  # Highest price
    low = Column(Float, nullable=False)  # Lowest price
    close = Column(Float, nullable=False)  # Closing price
    volume = Column(Integer, nullable=False)  # Trading volume
    interval = Column(String(5), nullable=False)  # Bar interval (1m, 5m, 1h, etc)
    
    # Index for fast queries by symbol and timestamp
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Bar {self.symbol} {self.timestamp} close={self.close}>"


class DatabaseManager:
    """Manages database operations (save, retrieve, query)"""
    
    def __init__(self, db_url='sqlite:///trading_bot.db'):
        """Initialize database connection and create tables if needed"""
        
        # Create database engine
        self.engine = create_engine(db_url, echo=False)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """Create a new database session"""
        return self.Session()
    
    def save_bars(self, symbol, bars_df, interval='1m'):
        """Save DataFrame of bars to database, skipping duplicates"""
        
        session = self.get_session()
        bars_added = 0
        
        # Loop through each bar in the DataFrame
        for timestamp, row in bars_df.iterrows():
            
            # Check if bar already exists (prevent duplicates)
            existing = session.query(MarketBar).filter_by(
                symbol=symbol,
                timestamp=timestamp,
                interval=interval
            ).first()
            
            # Only add if not already in database
            if not existing:
                # Create new MarketBar object
                bar = MarketBar(
                    symbol=symbol,
                    timestamp=timestamp.to_pydatetime() if hasattr(timestamp, 'to_pydatetime') else timestamp,
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=int(row['volume']),
                    interval=interval
                )
                session.add(bar)
                bars_added += 1
        
        # Commit all changes to database
        session.commit()
        session.close()
        
        print(f"✓ Saved {bars_added} new bars to database")
        return bars_added
    
    def get_bars(self, symbol, start=None, end=None, interval='1m'):
        """Retrieve bars from database for given symbol and time range"""
        
        session = self.get_session()
        
        # Build query for symbol and interval
        query = session.query(MarketBar).filter_by(symbol=symbol, interval=interval)
        
        # Add time filters if provided
        if start:
            query = query.filter(MarketBar.timestamp >= start)
        if end:
            query = query.filter(MarketBar.timestamp <= end)
        
        # Order by timestamp ascending
        query = query.order_by(MarketBar.timestamp)
        
        # Execute query and return results
        bars = query.all()
        session.close()
        
        return bars