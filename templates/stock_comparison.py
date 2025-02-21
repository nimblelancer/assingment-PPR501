import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from vnstock import Vnstock
import constants.strings as strings
from database.database import get_stock_prices

def fetch_stock_data(ticker, start_date, end_date):
    """Get stock data from API or database backup"""
    stock = Vnstock().stock(symbol=ticker, source='VCI')
    df = stock.quote.history(symbol=ticker, start=start_date.strftime('%Y-%m-%d'), 
                             end=end_date.strftime('%Y-%m-%d'), interval="1D")
    if df.empty:
        df = get_stock_prices(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    if not df.empty:
        df.rename(columns={"time": "date"}, inplace=True)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    return df

def plot_stock_comparison_chart(stock_data):
    """Draw a chart comparing stock codes"""
    fig = go.Figure()

    for ticker, df in stock_data.items():
        fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines',
                                 name=ticker, line=dict(width=2), 
                                 hovertemplate='%{y:,.3f} VND<br>%{x|%Y-%m-%d}'))

    fig.update_layout(title=dict(text=strings.STOCK_COMPARISON_TITLE, font=dict(size=28)),
                      xaxis_title="Date", yaxis_title="Price (VND)")
    return fig

def stock_comparison_screen(start_date, end_date, tickers):
    """Stock price comparison interface"""

    if "update_data_comparison" not in st.session_state:
        st.session_state.update_data_comparison = True

    if st.button("🔄 Refresh Data"):
        st.session_state.update_data_stock = True
        st.rerun()

    if st.session_state.update_data_comparison:
        try:
            stock_data = {ticker: fetch_stock_data(ticker, start_date, end_date) for ticker in tickers}
            stock_data = {ticker: df for ticker, df in stock_data.items() if not df.empty}

            if stock_data:
                st.plotly_chart(plot_stock_comparison_chart(stock_data))
            else:
                st.warning("No data available for the selected stocks.")

        except Exception as e:
            st.error(strings.ERROR_MESSAGE.format(e))
