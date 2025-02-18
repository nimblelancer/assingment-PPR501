import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from vnstock import Vnstock

st.set_page_config(page_title="Stock Analytics", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .main {background-color: #F9F9F9;}
    h1 {color: #2a4d8f;}
    h2 {color: #1f3d7a;}
    .stSelectbox, .stDateInput, .stSlider, .stMultiSelect {padding: 10px; border-radius: 5px;}
    .stAlert {border-radius: 5px;}
    .block-container {padding-top: 2rem;}
    .st-b7 {color: #ffffff;}
    .stDataFrame {border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Ứng dụng Phân Tích Chứng Khoán Việt Nam")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Cài đặt tham số")
    popular_stocks = Vnstock().stock().listing.symbols_by_group('VN30')
    symbol = st.selectbox("**Chọn mã chứng khoán**", popular_stocks, index=0)
    start_date = st.date_input("**Ngày bắt đầu**", pd.to_datetime("2023-01-01"))
    end_date = st.date_input("**Ngày kết thúc**", pd.to_datetime("today"))
    time_interval = st.slider("**Tần suất cập nhật (giây)**", 10, 30, 20)
    tickers_to_compare = st.multiselect("**Mã so sánh**", popular_stocks, default=[symbol])
    st.markdown("---")
    st.markdown("🔄 Ứng dụng sẽ tự động cập nhật dữ liệu theo chu kỳ đã chọn")

placeholder = st.empty()

while True:
    with placeholder.container():
        try:
            # Create main container
            with st.container():
                # Section 1: Biểu đồ chính và MA
                col1, col2 = st.columns([4, 1])
                with col2:
                    st.subheader("📊 Cài đặt MA")
                    ma_period = st.slider("**Chu kỳ MA**", 10, 200, 50, key="ma_slider")

                with col1:
                    stock = Vnstock().stock(symbol=symbol, source='VCI')
                    df = stock.quote.history(symbol=symbol, start=start_date.strftime('%Y-%m-%d'), 
                                           end=end_date.strftime('%Y-%m-%d'), interval="1m")
                    
                    if not df.empty:
                        df.rename(columns={"time": "date"}, inplace=True)
                        df['date'] = pd.to_datetime(df['date'])
                        df.set_index('date', inplace=True)

                        # Định dạng lại cột giá về VND
                        vnd_columns = ['open', 'high', 'low', 'close']
                        df[vnd_columns] = df[vnd_columns].apply(lambda x: round(x, 2))

                        # Input từ người dùng để bật/tắt đường MA
                        ma_period = st.slider("Chọn số ngày trung bình động (MA)", min_value=5, max_value=50, value=20)
                        show_ma = st.checkbox("Hiển thị đường trung bình động (MA)", value=True)

                        # Tạo biểu đồ tương tác
                        fig = go.Figure()

                        fig.add_trace(go.Scatter(
                            x=df.index, y=df['close'], mode='lines',
                            name='Giá đóng cửa', line=dict(color='#2a4d8f', width=2),
                            hovertemplate='%{y:,.3f} VND<br>%{x|%Y-%m-%d}'
                        ))

                        # Thêm đường MA nếu được chọn
                        if show_ma:
                            df['MA'] = df['close'].rolling(window=ma_period).mean()
                            fig.add_trace(go.Scatter(
                                x=df.index, y=df['MA'], mode='lines',
                                name=f'MA{ma_period}', line=dict(color='#ff6b35', width=2, dash='dash'),
                                hovertemplate='%{y:,.3f} VND<br>%{x|%Y-%m-%d}'
                            ))

                        # Cấu hình layout
                        fig.update_layout(
                            title=f"📊 Biểu đồ giá {symbol}",
                            xaxis_title="Ngày", yaxis_title="Giá (VND)",
                            xaxis=dict(showgrid=True),
                            yaxis=dict(showgrid=True, tickformat=",.3f VND"),
                            template='plotly_white',
                            hovermode='x unified'
                        )

                        st.plotly_chart(fig)

                # Section 2: Thông tin thời gian thực
                st.subheader("📊 Thông tin thị trường")
                col3, col4, col5 = st.columns(3)
                
                with col3:
                    current_price = f"{df['close'].iloc[-1]:,.3f} VND"
                    st.markdown(f"**Giá hiện tại ({symbol}):**")
                    st.markdown(f"<h2 style='color: #2a4d8f;'>{current_price}</h2>", 
                               unsafe_allow_html=True)
                    
                with col4:
                    ma_price = f"{df['MA'].iloc[-1]:,.3f} VND"
                    st.markdown(f"**Giá trung bình ({ma_period} phiên):**")
                    st.markdown(f"<h2 style='color: #ff6b35;'>{ma_price}</h2>", 
                               unsafe_allow_html=True)
                    
                with col5:
                    trend = "Tăng 📈" if df['close'].iloc[-1] > df['MA'].iloc[-1] else "Giảm 📉"
                    st.markdown("**Xu hướng dự báo:**")
                    st.markdown(f"<h2 style='color: {'#2ecc71' if 'Tăng' in trend else '#e74c3c'};'>{trend}</h2>", 
                               unsafe_allow_html=True)

                # Section 3: Sổ lệnh và dữ liệu
                tab1, tab2, tab3 = st.tabs(["📋 Sổ lệnh", "📊 So sánh cổ phiếu", "📂 Dữ liệu thô"])

                with tab1:
                    st.subheader("📋 Sổ lệnh mua/bán")
                    order_book_df = stock.quote.intraday(symbol=symbol, show_log=False)
                    if not order_book_df.empty:
                        order_book_df.rename(columns={"time": "Thời gian", "price": "Giá", 
                                                    "volume": "Khối lượng", "match_type": "Loại giao dịch"}, 
                                           inplace=True)
                        st.dataframe(order_book_df.sort_values(by="Thời gian", ascending=False).head(20), 
                                   height=300, use_container_width=True)
                    else:
                        st.warning("Không tìm thấy dữ liệu khớp lệnh.")

                with tab2:
                    if len(tickers_to_compare) > 1:
                        st.subheader("📊 So sánh hiệu suất cổ phiếu")
                        fig_comparison = go.Figure()
                        
                        for ticker in tickers_to_compare:
                            df_compare = Vnstock().stock(symbol=ticker, source='VCI').quote.history(
                                symbol=ticker, start=start_date.strftime('%Y-%m-%d'), 
                                end=end_date.strftime('%Y-%m-%d'), interval="1D")
                            
                            if not df_compare.empty:
                                df_compare.rename(columns={"time": "date"}, inplace=True)
                                df_compare['date'] = pd.to_datetime(df_compare['date'])
                                df_compare.set_index('date', inplace=True)
                                
                                fig_comparison.add_trace(go.Scatter(
                                    x=df_compare.index, y=df_compare['close'], mode='lines',
                                    name=ticker, line=dict(width=2),
                                    hovertemplate='%{y:,.3f} VND<br>%{x|%Y-%m-%d}'
                                ))
                        
                        # Cấu hình layout
                        fig_comparison.update_layout(
                            xaxis_title="Ngày", yaxis_title="Giá (VND)",
                            xaxis=dict(showgrid=True),
                            yaxis=dict(showgrid=True, tickformat=",.3f VND"),
                            template='plotly_white',
                            hovermode='x unified'
                        )
                        
                        # Hiển thị biểu đồ trên Streamlit
                        st.plotly_chart(fig_comparison)
                    else:
                        st.info("Vui lòng chọn ít nhất 2 mã cổ phiếu để so sánh")

                with tab3:
                    st.subheader("📂 Dữ liệu giá gốc")
                    st.dataframe(df.sort_index(ascending=False), 
                                height=400, use_container_width=True)

        except Exception as e:
            st.error(f"⚠️ Có lỗi xảy ra: {str(e)}")
    
    time.sleep(time_interval)
    st.rerun()