from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()
_stock_table_cache = {}
_order_book_table_cache = {}

class VNIndexPrice(Base):
    """Bảng lưu dữ liệu VNINDEX"""
    __tablename__ = "vnindex_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

def create_stock_table(symbol: str):
    """
    Tạo bảng riêng cho từng mã chứng khoán (ví dụ: stock_vnd, stock_hpg).
    """
    if symbol in _stock_table_cache:
        return _stock_table_cache[symbol]
    
    table_name = f"stock_{symbol.lower()}"

    class StockTable(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}

        id = Column(Integer, primary_key=True, autoincrement=True)
        time = Column(DateTime, nullable=False)
        open = Column(Float, nullable=False)
        high = Column(Float, nullable=False)
        low = Column(Float, nullable=False)
        close = Column(Float, nullable=False)
        volume = Column(Integer, nullable=False)

    _stock_table_cache[symbol] = StockTable
    return StockTable

def create_order_book_table(symbol: str):
    """
    Tạo bảng riêng cho từng mã chứng khoán trong Order Book (ví dụ: order_book_vnd, order_book_hpg).
    """
    if symbol in _order_book_table_cache:
        return _order_book_table_cache[symbol]

    table_name = f"order_book_{symbol.lower()}"

    class OrderBookTable(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}

        id = Column(Integer, primary_key=True, autoincrement=True)
        time = Column(DateTime, nullable=False)
        price = Column(Float, nullable=False)
        volume = Column(Float, nullable=False)
        match_type = Column(String, nullable=False)
        order_book_id = Column(Integer, nullable=False)

    _order_book_table_cache[symbol] = OrderBookTable
    return OrderBookTable
