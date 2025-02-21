import datetime
import os
import streamlit as st
import constants.strings as strings
import pandas as pd
from templates.vnindex_infor import vnindex_screen
from templates.stock_detail import stock_detail_screen
from templates.stock_comparison import stock_comparison_screen
from templates.stock_predict import stock_predict_screen
from vnstock import Vnstock
from database.database import init_db


# Check the database file is exist, if not init the database
if not os.path.exists(strings.DATABASE_ABS_PATH):
    init_db()

st.set_page_config(page_title="Stock Analytics", layout="wide", page_icon="📈")

st.title(strings.APP_TITLE)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header(strings.SIDEBAR_HEADER)

    # Get list stock code VN30
    popular_stocks = Vnstock().stock().listing.symbols_by_group('VN30')

    # Select stock code
    symbol = st.selectbox(strings.STOCK_SELECTION, popular_stocks, index=None) 

    # Select start date and end date
    start_date = st.date_input(strings.START_DATE, pd.to_datetime(datetime.date.today() - datetime.timedelta(days=365)))
    end_date = st.date_input(strings.END_DATE, datetime.date.today())

    # Select comparison stock
    tickers_to_compare = st.multiselect(strings.COMPARISON_SELECTION, popular_stocks, default=[])
    if len(tickers_to_compare) < 2:
        st.info(strings.SELECT_MORE_STOCKS_INFO)

    # Select the model to predict
    model_predict = st.selectbox(strings.STOCK_PREDICT, strings.STOCK_PREDICT_MODEL, index=None)

screen_placeholder = st.empty()
# Define the mapping of conditions to screen functions
screen_mapping = {
    "comparison": (len(tickers_to_compare) >= 2, stock_comparison_screen, (start_date, end_date, tickers_to_compare)),
    "detail": (symbol is not None, stock_detail_screen, (symbol, start_date, end_date)),
    "predict": (model_predict is not None, stock_predict_screen, ())
}

# Default screen is vnindex_screen
screen_func = vnindex_screen
screen_args = (start_date, end_date)

# Iterate over screen_mapping to find the first matching condition
for key, (condition, func, args) in screen_mapping.items():
    if condition:
        screen_func, screen_args = func, args
        break  # Stop at the first matched condition

# Render the selected screen
with screen_placeholder.container():
    # Ensure args is always a tuple
    if not isinstance(screen_args, tuple):
        screen_args = (screen_args,)
    screen_func(*screen_args)