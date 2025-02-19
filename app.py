import streamlit as st
import constants
from vnindex_infor import vnindex_screen
from stock_detail import stock_detail_screen
from stock_comparison import stock_comparison_screen
from vnstock import Vnstock
import pandas as pd

st.set_page_config(page_title="Stock Analytics", layout="wide", page_icon="📈")

st.title(constants.APP_TITLE)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header(constants.SIDEBAR_HEADER)

    # Get list stock code VN30
    popular_stocks = Vnstock().stock().listing.symbols_by_group('VN30')

    # Select stock code
    symbol = st.selectbox(constants.STOCK_SELECTION, popular_stocks, index=None) 

    # Select start date and end date
    start_date = st.date_input(constants.START_DATE, pd.to_datetime("2023-01-01"))
    end_date = st.date_input(constants.END_DATE, pd.to_datetime("today"))

    # Select comparison stock
    tickers_to_compare = st.multiselect(constants.COMPARISON_SELECTION, popular_stocks, default=[])
    if len(tickers_to_compare) < 2:
        st.info(constants.SELECT_MORE_STOCKS_INFO)

# Navigation depending on user selection
screen_placeholder = st.empty()
with screen_placeholder.container():
    if len(tickers_to_compare) >= 2:
        stock_comparison_screen(start_date, end_date, tickers_to_compare)
    elif symbol is not None:
        stock_detail_screen(symbol, start_date, end_date)
    else:
        vnindex_screen(start_date, end_date)
