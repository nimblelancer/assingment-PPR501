import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from vnstock import Vnstock
import constants.strings as strings

def stock_comparison_screen(start_date, end_date, tickers):
    # Initialize session_state if not exist
    if "update_data_comparison" not in st.session_state:
        st.session_state.update_data_comparison = True

    if "stock_data" not in st.session_state:
        st.session_state.stock_data = None
    
    if st.button("🔄 Refresh Data"):
            st.session_state.update_data_stock = True
            st.rerun()
    if st.session_state.update_data_comparison:
        try:
            fig = go.Figure()
            
            for ticker in tickers:
                stock = Vnstock().stock(symbol=ticker, source='VCI')
                df = stock.quote.history(symbol=ticker, start=start_date.strftime('%Y-%m-%d'), 
                end=end_date.strftime('%Y-%m-%d'), interval="1D")

                if not df.empty:
                    df.rename(columns={"time": "date"}, inplace=True)
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)

                    fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines',
                                            name=ticker, line=dict(width=2), 
                                            hovertemplate='%{y:,.3f} VND<br>%{x|%Y-%m-%d}'))

            fig.update_layout(title=dict(
                                text=strings.STOCK_COMPARISON_TITLE,
                                font=dict(size=28)
                            ),xaxis_title="Date", yaxis_title="Price (VND)")
            st.plotly_chart(fig)
        except Exception as e:
            st.error(strings.ERROR_MESSAGE.format(e))