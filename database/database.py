import os
import pandas as pd
import time
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, exists, inspect
from vnstock import Vnstock
from services.fetch_data import fetch_vnindex_data, fetch_stock_data, fetch_order_book_stock_data
from constants import strings
from database.models import Base, VNIndexPrice, create_stock_table, create_order_book_table
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.sql import func

# Database configuration
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SQLITE_DIR = os.path.join(BASE_DIR, "SQLite")

# Create SQLite folder if not exist
if not os.path.exists(SQLITE_DIR):
    os.makedirs(SQLITE_DIR)

engine = create_engine(strings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_latest_stock_date(symbol: str):
    """
    Get the most recent date with data for the stock code from the database.
    If the table has no data, return None.
    """
    StockTable = create_stock_table(symbol)
    with SessionLocal() as session:
        latest_date = session.query(func.max(StockTable.time)).scalar()
    return latest_date

def get_latest_vnindex_date():
    """
    Get the most recent date with VNINDEX data from the database. 
    If the table has no data, return None.
    """
    with SessionLocal() as session:
        latest_date = session.query(func.max(VNIndexPrice.time)).scalar()
    return latest_date

def table_exists(table_name):
    """Check if the table exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def safe_execute(func, *args, **kwargs):
    """Execute function with retry if database is locked"""
    retries = 3
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "database is locked" in str(e):
                print(f"⚠️ Database is locked, retrying ({attempt+1}/{retries})...")
                time.sleep(1) 
            else:
                raise e

def save_vnindex_prices(df: pd.DataFrame):  
    """Save VNINDEX data to table `vnindex_prices`"""
    def _execute():
        with SessionLocal() as session:
            for _, row in df.iterrows():
                exists_query = session.query(
                    exists().where(VNIndexPrice.time == row['time'])
                ).scalar()

                if not exists_query:
                    stock_data = VNIndexPrice(
                        time=row['time'],
                        open=row['open'],
                        high=row['high'],
                        low=row['low'],
                        close=row['close'],
                        volume=row['volume']
                    )
                    session.add(stock_data)
            session.commit()

    safe_execute(_execute)

def save_stock_prices(symbol: str, df: pd.DataFrame):
    """Save stock price data in separate tables for each stock code"""
    StockTable = create_stock_table(symbol)
    
    if df.empty:
        print(f"⚠️ Data for {symbol} is empty!")
        return

    is_exists = table_exists(StockTable.__tablename__)

    if not is_exists:
        print(f"🛠 Creating table {StockTable.__tablename__} for {symbol}...")
        with engine.begin() as conn:
            StockTable.__table__.create(bind=conn)

    def _execute():
        with SessionLocal() as session:
            for _, row in df.iterrows():
                exists_query = session.query(
                    exists().where(StockTable.time == row['time'])
                ).scalar()

                if not exists_query:
                    stock_data = StockTable(
                        time=row['time'],
                        open=row['open'],
                        high=row['high'],
                        low=row['low'],
                        close=row['close'],
                        volume=row['volume']
                    )
                    session.add(stock_data)
            session.commit()

    safe_execute(_execute)

def get_stock_prices(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Get stock price data from separate table for each stock code"""
    StockTable = create_stock_table(symbol)

    inspector = inspect(engine)
    if StockTable.__tablename__ not in inspector.get_table_names():
        print(f"⚠️ Table {StockTable.__tablename__} does not exist!")
        return pd.DataFrame()

    def _execute():
        with SessionLocal() as session:
            query = session.query(StockTable).filter(
                StockTable.time >= start_date,
                StockTable.time <= end_date
            ).order_by(StockTable.time.asc()).all()
            
            return pd.DataFrame([{
                "time": record.time,
                "open": record.open,
                "high": record.high,
                "low": record.low,
                "close": record.close,
                "volume": record.volume
            } for record in query])

    return safe_execute(_execute)

def save_order_book(symbol: str, df: pd.DataFrame):
    """Save Order Book data to database, avoid duplicate storage"""
    OrderBookTable  = create_order_book_table(symbol)
    
    if df.empty:
        print(f"⚠️ Data for {symbol} is empty!")
        return

    is_exists = table_exists(OrderBookTable.__tablename__)

    if not is_exists:
        print(f"🛠 Creating table {OrderBookTable.__tablename__} for {symbol}...")
        with engine.begin() as conn:
            OrderBookTable.__table__.create(bind=conn)
    
    def _execute():
        with SessionLocal() as session:
            for _, row in df.iterrows():
                exists_query = session.query(
                    exists().where(
                        (OrderBookTable.order_book_id == row['id'])
                    )
                ).scalar()

                if not exists_query:
                    order_data = OrderBookTable(
                        time=row['time'],
                        price=row['price'],
                        volume=row['volume'],
                        match_type=row['match_type'],
                        order_book_id=row['id']
                    )
                    session.add(order_data)

            session.commit()

    safe_execute(_execute)

def get_order_book(symbol: str) -> pd.DataFrame:
    """Get Order Book data from database"""

    OrderBookTable = create_order_book_table(symbol)

    inspector = inspect(engine)
    if OrderBookTable.__tablename__ not in inspector.get_table_names():
        print(f"⚠️ Table {OrderBookTable.__tablename__} does not exist!")
        return pd.DataFrame()
    
    def _execute():
        with SessionLocal() as session:
            query = session.query(OrderBookTable).all()
            
            return pd.DataFrame([{
                "time": record.time,
                "price": record.price,
                "volume": record.volume,
                "match_type": record.match_type,
                "id" : record.order_book_id
            } for record in query])

    return safe_execute(_execute)

def get_vnindex_infor(start_date: str, end_date: str) -> pd.DataFrame:
    """Get data vnindex from database"""

    def _execute():
        with SessionLocal() as session:
            query = session.query(VNIndexPrice).filter(
                VNIndexPrice.time >= start_date,
                VNIndexPrice.time <= end_date
            ).order_by(VNIndexPrice.time.asc()).all()
            
            return pd.DataFrame([{
                "time": record.time,
                "open": record.open,
                "high": record.high,
                "low": record.low,
                "close": record.close,
                "volume": record.volume
            } for record in query])

    return safe_execute(_execute)

def init_db():
    """Initialize database: create tables and fetch data for the first time if needed."""
    print("🔧 Initializing database...")

    Base.metadata.create_all(bind=engine)

    today = datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.today() - relativedelta(years=3)).strftime("%Y-%m-%d") 
    print("🚀 Fetching initial VNINDEX data...")
    vnindex_df = fetch_vnindex_data(start_date, today)
    if not vnindex_df.empty:
        save_vnindex_prices(vnindex_df)

    symbols = Vnstock().stock().listing.symbols_by_group('VN30')
    for symbol in symbols:
        table_name = f"stock_prices_{symbol.lower()}"
        if not table_exists(table_name):
            print(f"🚀 Fetching initial data for {symbol}...")
            stock_df = fetch_stock_data(symbol, start_date, today)
            order_book_df = fetch_order_book_stock_data(symbol)
            if not stock_df.empty:
                save_stock_prices(symbol, stock_df)
            
            if not order_book_df.empty:
                save_order_book(symbol,order_book_df)

    print("✅ Database initialized successfully!")