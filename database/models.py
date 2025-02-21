from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
_stock_table_cache = {}

# ==============================
# 📊 BẢNG CHỨNG KHOÁN VNINDEX
# ==============================
class StockPrice(Base):
    """Bảng lưu dữ liệu VNINDEX"""
    __tablename__ = "vnindex_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

# ==============================
# 📜 BẢNG ORDER BOOK
# ==============================
class OrderBook(Base):
    """Bảng lưu dữ liệu Order Book của các mã chứng khoán"""
    __tablename__ = "order_books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True)
    time = Column(DateTime)
    price = Column(Float)
    volume = Column(Float)
    type = Column(String)

# ==============================
# 🏛 HÀM TẠO BẢNG CHỨNG KHOÁN RIÊNG
# ==============================
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
        date = Column(DateTime, nullable=False)
        open = Column(Float, nullable=False)
        high = Column(Float, nullable=False)
        low = Column(Float, nullable=False)
        close = Column(Float, nullable=False)
        volume = Column(Integer, nullable=False)
    _stock_table_cache[symbol] = StockTable
    return StockTable