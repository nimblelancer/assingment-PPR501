from vnstock import Vnstock
import pandas as pd

from constants import strings

def fetch_vnindex_data(start_date, end_date):
    """Get VNINDEX data from API."""
    try:
        stock = Vnstock().stock(symbol=strings.VNINDEX, source='VCI')
        df = stock.quote.history(symbol=strings.VNINDEX, start=start_date, 
            end=end_date, interval="1D")
        if df.empty:
            print("⚠️ No VNINDEX data!")
        return df
    except Exception as e:
        print(f"❌ Error when fetching VNINDEX: {e}")
        return pd.DataFrame()

def fetch_stock_data(symbol, start_date, end_date):
    """Get stock data from API."""
    try:
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        df = stock.quote.history(symbol=symbol, start=start_date, 
            end=end_date, interval="1m")
        if df.empty:
            print(f"⚠️No data for {symbol}!")
        return df
    except Exception as e:
        print(f"❌ Error when fetching {symbol}: {e}")
        return pd.DataFrame()
    
def fetch_order_book_stock_data(symbol):
    """Get stock order matching data from API."""
    try:
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        order_book_df = stock.quote.intraday(symbol=symbol, show_log=False)
        if order_book_df.empty:
            print(f"⚠️ No data for {symbol}!")
        return order_book_df
    except Exception as e:
        print(f"❌ Error when fetching {symbol}: {e}")
        return pd.DataFrame()
