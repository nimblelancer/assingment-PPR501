import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from vnstock import Vnstock
import constants

def vnindex_screen(start_date, end_date):
    st.subheader("VNINDEX Information")

    # Initialize session_state if not exist
    if "update_data_vnindex" not in st.session_state:
        st.session_state.update_data_vnindex = True

    if "stock_data" not in st.session_state:
        st.session_state.stock_data = None

    col_left, col_right = st.columns([3, 1])
    with col_left:
        ma_period = st.slider(constants.MOVING_AVERAGE_PERIOD, min_value=5, max_value=50, value=20)
        show_ma = st.checkbox(constants.MOVING_AVERAGE_TOGGLE, value=True)

    with col_right:
        if st.button(constants.REFRESH_DATA):
            st.session_state.update_data_stock = True
            st.rerun()

    if st.session_state.update_data_vnindex:
        try:
            stock = Vnstock().stock(symbol=constants.VNINDEX, source='VCI')
            df = stock.quote.history(symbol=constants.VNINDEX, start=start_date.strftime('%Y-%m-%d'), 
                end=end_date.strftime('%Y-%m-%d'), interval="1D")

            if not df.empty:
                df.rename(columns={"time": "date"}, inplace=True)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                
                

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines',
                                        name='Closing Price', line=dict(color='#2a4d8f', width=2),
                                        hovertemplate='%{y:,.3f} VND<br>%{x|%Y-%m-%d}'))

                if show_ma:
                    df['MA'] = df['close'].rolling(window=ma_period).mean()
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA'], mode='lines',
                                            name=f'MA{ma_period}', line=dict(color='#ff6b35', width=2, dash='dash'),
                                            hovertemplate='%{y:,.3f} VND<br>%{x|%Y-%m-%d}'))

                fig.update_layout(title=dict(
                                text=constants.MAIN_CHART_TITLE,
                                font=dict(size=28)
                            ), xaxis_title="Date", yaxis_title="Price (VND)", 
                                xaxis=dict(showgrid=True), yaxis=dict(showgrid=True, tickformat=",.3f VND"),
                                template='plotly_white', hovermode='x unified')

                st.plotly_chart(fig)

            st.subheader(constants.MARKET_INFO_TITLE)
            col3, col4, col5 = st.columns(3)

            with col3:
                current_price = f"{df['close'].iloc[-1]:,.3f} VND"
                st.markdown(constants.CURRENT_PRICE.format(constants.VNINDEX))
                st.markdown(f"<h2 style='color: #2a4d8f;'>{current_price}</h2>", unsafe_allow_html=True)

            with col4:
                ma_price = f"{df['MA'].iloc[-1]:,.3f} VND"
                st.markdown(constants.MOVING_AVERAGE_PRICE.format(ma_period))
                st.markdown(f"<h2 style='color: #ff6b35;'>{ma_price}</h2>", unsafe_allow_html=True)

            with col5:
                trend = constants.TREND_UP if df['close'].iloc[-1] > df['MA'].iloc[-1] else constants.TREND_DOWN
                st.markdown(constants.TREND_FORECAST)
                st.markdown(f"<h2 style='color: {'#2ecc71' if constants.TREND_UP in trend else '#e74c3c'};'>{trend}</h2>", unsafe_allow_html=True)

            st.subheader(constants.RAW_DATA_TITLE)
            df.rename(columns={"date": "Date", "open": "Open", 
                                    "volume": "Volume", "high": "High", "low": "Low", "close": "Close", "ma": "MA"}, 
                                    inplace=True)
            st.dataframe(df.sort_index(ascending=False), height=400, use_container_width=True)
        except Exception as e:
            st.error(constants.ERROR_MESSAGE.format(e))