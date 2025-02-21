import threading
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor
from vnstock import Vnstock
import constants.strings as strings
from database.database import save_stock_prices, get_stock_prices, save_order_book, get_order_book

# 🛠 Tạo ThreadPoolExecutor để giới hạn số thread chạy đồng thời
executor = ThreadPoolExecutor(max_workers=2)

def fetch_stock_data(symbol, start_date, end_date):
    """ Lấy dữ liệu chứng khoán từ API hoặc database """
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    df = stock.quote.history(symbol=symbol, start=start_date.strftime('%Y-%m-%d'), 
                             end=end_date.strftime('%Y-%m-%d'), interval="1m")

    if df.empty:
        df = get_stock_prices(symbol, start_date, end_date)
    # else:
    #     df_copy = df.copy()  # 🔹 Sao chép DataFrame để tránh lỗi `KeyError`
    #     executor.submit(save_stock_prices, symbol, df_copy)  # 🔹 Chạy thread tối ưu

    if df.empty:
        st.error(strings.ERROR_NO_DATA.format(symbol, start_date, end_date))
        return None

    df.rename(columns={"time": "date"}, inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    return df

def plot_stock_chart(df, show_ma, ma_period):
    """ Vẽ biểu đồ giá cổ phiếu """
    fig = go.Figure()

    # 📈 Giá đóng cửa
    fig.add_trace(go.Scatter(
        x=df.index, y=df['close'], mode='lines',
        name='Closing Price', line=dict(color='#2a4d8f', width=2),
        hovertemplate='%{y:,.3f} VND<br>%{x|%Y-%m-%d}'
    ))

    # 📉 Đường trung bình động (MA)
    if show_ma:
        if 'MA' in df.columns:
            df.drop(columns=['MA'], inplace=True)  # 🔹 Xóa cột MA cũ nếu đã tồn tại
        
        df['MA'] = df['close'].rolling(window=ma_period).mean()  # 🔹 Tạo lại MA mới
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MA'], mode='lines',
            name=f'MA{ma_period}', line=dict(color='#ff6b35', width=2, dash='dash'),
            hovertemplate='%{y:,.3f} VND<br>%{x|%Y-%m-%d}'
        ))

    # 🎨 Layout
    fig.update_layout(
        title=dict(text=strings.MAIN_CHART_TITLE, font=dict(size=28)),
        xaxis_title="Date", yaxis_title="Price (VND)",
        xaxis=dict(showgrid=True), yaxis=dict(showgrid=True, tickformat=",.3f VND"),
        template='plotly_white', hovermode='x unified'
    )

    st.plotly_chart(fig)


def display_market_info(df, symbol, ma_period):
    """ Hiển thị thông tin thị trường """
    st.subheader(strings.MARKET_INFO_TITLE)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(strings.CURRENT_PRICE.format(symbol))
        st.markdown(f"<h2 style='color: #2a4d8f;'>{df['close'].iloc[-1]:,.3f} VND</h2>", unsafe_allow_html=True)

    with col2:
        st.markdown(strings.MOVING_AVERAGE_PRICE.format(ma_period))
        st.markdown(f"<h2 style='color: #ff6b35;'>{df['MA'].iloc[-1]:,.3f} VND</h2>", unsafe_allow_html=True)

    with col3:
        trend = strings.TREND_UP if df['close'].iloc[-1] > df['MA'].iloc[-1] else strings.TREND_DOWN
        trend_color = "#2ecc71" if "Up" in trend else "#e74c3c"
        st.markdown(strings.TREND_FORECAST)
        st.markdown(f"<h2 style='color: {trend_color};'>{trend}</h2>", unsafe_allow_html=True)

def display_order_book(stock, symbol):
    """ Hiển thị Order Book """
    st.subheader(strings.ORDER_BOOK_TITLE)
    try:
        order_book_df = stock.quote.intraday(symbol=symbol, show_log=False)
        
        if order_book_df.empty: 
            order_book_df = get_order_book(symbol)
        # else: 
        #     order_book_df_copy = order_book_df.copy()  # 🔹 Sao chép DataFrame để tránh lỗi `KeyError`
        #     executor.submit(save_order_book, symbol, order_book_df_copy)  # 🔹 Chạy thread tối ưu

        order_book_df.rename(columns={"time": "Time", "price": "Price", "volume": "Volume", 
                                      "match_type": "Type", "id": "ID"}, inplace=True)
        st.dataframe(order_book_df.sort_values(by="Time", ascending=False).head(20), height=300, use_container_width=True)
    except:
        order_book_df = get_order_book(symbol)
        
def display_raw_data(df):
    """ Hiển thị dữ liệu gốc """
    st.subheader(strings.RAW_DATA_TITLE)
    
    df.rename(columns={"date": "Date", "open": "Open", "volume": "Volume", 
                       "high": "High", "low": "Low", "close": "Close"}, inplace=True)
    st.dataframe(df.sort_index(ascending=False), height=400, use_container_width=True)

def stock_detail_screen(symbol, start_date, end_date):
    """ Màn hình chi tiết cổ phiếu """
    st.subheader(f"Stock Detail: {symbol}")

    # 🛠 Setup session_state
    if "update_data_stock" not in st.session_state:
        st.session_state.update_data_stock = True

    if "stock_data" not in st.session_state:
        st.session_state.stock_data = None

    # 🎛️ UI: Chọn MA & Refresh
    col_left, col_right = st.columns([3, 1])
    with col_left:
        ma_period = st.slider(strings.MOVING_AVERAGE_PERIOD, min_value=5, max_value=50, value=20)
        show_ma = st.checkbox(strings.MOVING_AVERAGE_TOGGLE, value=True)

    with col_right:
        if st.button(strings.REFRESH_DATA):
            st.session_state.update_data_stock = True
            st.rerun()

    # 🔄 Cập nhật dữ liệu chứng khoán
    if st.session_state.update_data_stock:
        df = fetch_stock_data(symbol, start_date, end_date)
        if df is not None:
            st.session_state.stock_data = df
            st.session_state.update_data_stock = False
        else:
            return

    df = st.session_state.stock_data
    df.columns = df.columns.str.lower()
    # 📊 Hiển thị biểu đồ & thông tin thị trường
    plot_stock_chart(df, show_ma, ma_period)
    display_market_info(df, symbol, ma_period)

    # 🔍 Tab Order Book & Raw Data
    tab1, tab2 = st.tabs([strings.ORDER_BOOK_TAB, strings.RAW_DATA_TAB])

    with tab1:
        # display_order_book(stock, symbol)
        print()

    with tab2:
        display_raw_data(df)