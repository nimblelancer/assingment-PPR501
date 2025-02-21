from database.database import save_vnindex_prices, save_stock_prices, engine
from services.fetch_data import fetch_vnindex_data, fetch_stock_data
from datetime import datetime, timedelta
from sqlalchemy import inspect

def table_exists(table_name):
    """Kiểm tra bảng có tồn tại trong database không."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def init_db():
    """Khởi tạo database bằng cách lấy toàn bộ dữ liệu từ API."""
    today = datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")  # Lấy dữ liệu 1 năm

    # Chỉ init nếu chưa có dữ liệu
    if not table_exists("stock_prices"):
        print("🚀 Fetching initial VNINDEX data...")
        vnindex_df = fetch_vnindex_data(start_date, today)
        if not vnindex_df.empty:
            save_vnindex_prices(vnindex_df)
    
    symbols = ["VND", "HPG", "VCB"]  # Danh sách mã chứng khoán
    for symbol in symbols:
        table_name = f"stock_prices_{symbol.lower()}"
        if not table_exists(table_name):
            print(f"🚀 Fetching initial data for {symbol}...")
            stock_df = fetch_stock_data(symbol, start_date, today)
            if not stock_df.empty:
                save_stock_prices(symbol, stock_df)

    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_db()