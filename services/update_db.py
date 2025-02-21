from database.database import save_vnindex_prices, save_stock_prices, get_latest_stock_date, get_latest_vnindex_date
from services.fetch_data import fetch_vnindex_data, fetch_stock_data
from datetime import datetime, timedelta

def update_db():
    """Cập nhật database với dữ liệu mới nhất (chỉ thêm dữ liệu mới)."""
    today = datetime.today().strftime("%Y-%m-%d")

    # ======= Cập nhật dữ liệu VNINDEX =======
    latest_vnindex_date = get_latest_vnindex_date()
    start_date_vnindex = latest_vnindex_date if latest_vnindex_date else (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")

    print(f"🔄 Fetching VNINDEX data from {start_date_vnindex} to {today}...")
    vnindex_df = fetch_vnindex_data(start_date_vnindex, today)
    if not vnindex_df.empty:
        save_vnindex_prices(vnindex_df)

    # ======= Cập nhật dữ liệu Cổ phiếu VN30 =======
    symbols = ["VND", "HPG", "VCB"]  # Danh sách mã chứng khoán cần cập nhật
    for symbol in symbols:
        latest_stock_date = get_latest_stock_date(symbol)
        start_date_stock = latest_stock_date if latest_stock_date else (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"🔄 Fetching stock data for {symbol} from {start_date_stock} to {today}...")
        stock_df = fetch_stock_data(symbol, start_date_stock, today)
        if not stock_df.empty:
            save_stock_prices(symbol, stock_df)

if __name__ == "__main__":
    update_db()