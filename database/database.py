import os
import pandas as pd
import time
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, exists, inspect
from constants import strings
from database.models import Base, StockPrice, OrderBook, create_stock_table
from datetime import datetime, timedelta

# ==============================
# 🏛 CẤU HÌNH DATABASE
# ==============================
DATABASE_URL = strings.DATABASE_URL
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # ✅ Fix lỗi multi-thread
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ==============================
# 🏛 KHỞI TẠO DATABASE (CHẠY MỘT LẦN DUY NHẤT)
# ==============================
def init_db():
    """Khởi tạo database nếu chưa có"""
    Base.metadata.create_all(bind=engine)

# ==============================
# 📌 HÀM SAFE EXECUTION ĐỂ TRÁNH LỖI DATABASE LOCKED
# ==============================
def safe_execute(func, *args, **kwargs):
    """Thực thi hàm với retry nếu database bị khóa"""
    retries = 3
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "database is locked" in str(e):
                print(f"⚠️ Database is locked, retrying ({attempt+1}/{retries})...")
                time.sleep(1)  # Đợi 1 giây trước khi thử lại
            else:
                raise e

# ==============================
# 📊 LƯU DỮ LIỆU VNINDEX
# ==============================
def save_vnindex_prices(df: pd.DataFrame):
    """Lưu dữ liệu VNINDEX vào bảng `vnindex_prices`"""
    def _execute():
        with SessionLocal() as session:
            for _, row in df.iterrows():
                exists_query = session.query(
                    exists().where(StockPrice.date == row['date'])
                ).scalar()

                if not exists_query:
                    stock_data = StockPrice(
                        date=row['date'],
                        open_price=row['open'],
                        high_price=row['high'],
                        low_price=row['low'],
                        close_price=row['close'],
                        volume=row['volume']
                    )
                    session.add(stock_data)
            session.commit()

    safe_execute(_execute)

# ==============================
# 📊 LƯU DỮ LIỆU CHO CÁC MÃ CỔ PHIẾU
# ==============================
def save_stock_prices(symbol: str, df: pd.DataFrame):
    """Lưu dữ liệu giá cổ phiếu vào bảng riêng từng mã chứng khoán"""
    StockTable = create_stock_table(symbol)
    
    df.columns = df.columns.str.lower()
    if df.empty:
        print(f"⚠️ Data for {symbol} is empty!")
        return

    # 🔥 Kiểm tra bảng đã tồn tại trước khi truy vấn
    inspector = inspect(engine)
    table_exists = StockTable.__tablename__ in inspector.get_table_names()

    if not table_exists:
        print(f"🛠 Creating table {StockTable.__tablename__} for {symbol}...")
        with engine.begin() as conn:
            StockTable.__table__.create(bind=conn)  # Chỉ tạo bảng nếu chưa có

    def _execute():
        with SessionLocal() as session:
            for _, row in df.iterrows():
                exists_query = session.query(
                    exists().where(StockTable.date == row['time'])
                ).scalar()

                if not exists_query:
                    stock_data = StockTable(
                        date=row['time'],
                        open_price=row['open'],
                        high_price=row['high'],
                        low_price=row['low'],
                        close_price=row['close'],
                        volume=row['volume']
                    )
                    session.add(stock_data)
            session.commit()

    safe_execute(_execute)

# ==============================
# 📊 LẤY DỮ LIỆU CHỨNG KHOÁN
# ==============================
def get_stock_prices(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Lấy dữ liệu giá cổ phiếu từ bảng riêng từng mã chứng khoán"""
    StockTable = create_stock_table(symbol)

    # 🔥 Kiểm tra bảng tồn tại trước khi truy vấn
    inspector = inspect(engine)
    if StockTable.__tablename__ not in inspector.get_table_names():
        print(f"⚠️ Table {StockTable.__tablename__} does not exist!")
        return pd.DataFrame()  # Trả về DataFrame rỗng nếu bảng chưa tồn tại

    def _execute():
        with SessionLocal() as session:
            query = session.query(StockTable).filter(
                StockTable.date >= start_date,
                StockTable.date <= end_date
            ).order_by(StockTable.date.asc()).all()
            
            return pd.DataFrame([{
                "date": record.date,
                "open": record.open_price,
                "high": record.high_price,
                "low": record.low_price,
                "close": record.close_price,
                "volume": record.volume
            } for record in query])

    return safe_execute(_execute)

# ==============================
# 📜 ORDER BOOK FUNCTIONS
# ==============================
def save_order_book(symbol: str, df: pd.DataFrame):
    """Lưu dữ liệu Order Book vào database, tránh lưu trùng"""
    StockTable = create_stock_table(symbol)
    
    df.columns = df.columns.str.lower()
    if df.empty:
        print(f"⚠️ Data for {symbol} is empty!")
        return

    # 🔥 Kiểm tra bảng đã tồn tại trước khi truy vấn
    inspector = inspect(engine)
    table_exists = StockTable.__tablename__ in inspector.get_table_names()

    if not table_exists:
        print(f"🛠 Creating table {StockTable.__tablename__} for {symbol}...")
        with engine.begin() as conn:
            StockTable.__table__.create(bind=conn)  # Chỉ tạo bảng nếu chưa có
    
    def _execute():
        with SessionLocal() as session:
            for _, row in df.iterrows():
                exists_query = session.query(
                    exists().where(
                        (OrderBook.symbol == symbol) & 
                        (OrderBook.time == row['date']) & 
                        (OrderBook.price == row['price'])
                    )
                ).scalar()

                if not exists_query:
                    order_data = OrderBook(
                        symbol=symbol,
                        time=row['date'],
                        price=row['price'],
                        volume=row['volume'],
                        type=row['type']
                    )
                    session.add(order_data)

            session.commit()

    safe_execute(_execute)

def get_order_book(symbol: str) -> pd.DataFrame:
    """Lấy dữ liệu Order Book từ database"""
    def _execute():
        with SessionLocal() as session:
            query = session.query(OrderBook).filter(OrderBook.symbol == symbol).all()
            
            return pd.DataFrame([{
                "Time": record.time,
                "Price": record.price,
                "Volume": record.volume,
                "Type": record.type
            } for record in query])

    return safe_execute(_execute)