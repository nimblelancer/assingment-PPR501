from vnstock import Vnstock
import pandas as pd

from constants import strings

def fetch_vnindex_data(start_date, end_date):
    """Lấy dữ liệu VNINDEX từ API."""
    try:
        stock = Vnstock().stock(symbol=strings.VNINDEX, source='VCI')
        df = stock.quote.history(symbol=strings.VNINDEX, start=start_date.strftime('%Y-%m-%d'), 
            end=end_date.strftime('%Y-%m-%d'), interval="1D")
        if df.empty:
            print("⚠️ Không có dữ liệu VNINDEX!")
        return df
    except Exception as e:
        print(f"❌ Lỗi khi fetch VNINDEX: {e}")
        return pd.DataFrame()

def fetch_stock_data(symbol, start_date, end_date):
    """Lấy dữ liệu cổ phiếu từ API."""
    try:
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        df = stock.quote.history(symbol=symbol, start=start_date.strftime('%Y-%m-%d'), 
                             end=end_date.strftime('%Y-%m-%d'), interval="1m")
        if df.empty:
            print(f"⚠️ Không có dữ liệu cho {symbol}!")
        return df
    except Exception as e:
        print(f"❌ Lỗi khi fetch {symbol}: {e}")
        return pd.DataFrame()
    
def fetch_order_book_stock_data(symbol):
    """Lấy dữ liệu khớp lệnh cổ phiếu từ API."""
    try:
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        order_book_df = stock.quote.intraday(symbol=symbol, show_log=False)
        if order_book_df.empty:
            print(f"⚠️ Không có dữ liệu cho {symbol}!")
        return order_book_df
    except Exception as e:
        print(f"❌ Lỗi khi fetch {symbol}: {e}")
        return pd.DataFrame()
