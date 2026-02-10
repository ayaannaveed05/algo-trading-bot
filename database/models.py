from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class MarketBar(Base):
    """OHLCV market data bar"""
    __tablename__ = 'market_bars'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    interval = Column(String(5), nullable=False)  # '1m', '5m', '1h', '1d'
    
    # Index for fast queries
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Bar {self.symbol} {self.timestamp} close={self.close}>"


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_url='sqlite:///trading_bot.db'):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.Session()
    
    def save_bars(self, symbol, bars_df, interval='1m'):
        """Save DataFrame of bars to database"""
        session = self.get_session()
        
        bars_added = 0
        for timestamp, row in bars_df.iterrows():
            # Check if bar already exists
            existing = session.query(MarketBar).filter_by(
                symbol=symbol,
                timestamp=timestamp,
                interval=interval
            ).first()
            
            if not existing:
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
        
        session.commit()
        session.close()
        print(f"✓ Saved {bars_added} new bars to database")
        return bars_added
    
    def get_bars(self, symbol, start=None, end=None, interval='1m'):
        """Retrieve bars from database"""
        session = self.get_session()
        
        query = session.query(MarketBar).filter_by(symbol=symbol, interval=interval)
        
        if start:
            query = query.filter(MarketBar.timestamp >= start)
        if end:
            query = query.filter(MarketBar.timestamp <= end)
        
        query = query.order_by(MarketBar.timestamp)
        
        bars = query.all()
        session.close()
        
        return bars