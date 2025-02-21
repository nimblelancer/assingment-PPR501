import streamlit as st
from services.predict import predict_stock_price
from vnstock import Vnstock

def stock_predict_screen():
    st.subheader("📈 Stock Price Prediction")

    symbols = Vnstock().stock().listing.symbols_by_group('VN30')
    symbol = st.selectbox("Select stock symbol", symbols)
    
    target_date = st.date_input("Select prediction date")
    open_price = st.number_input("Opening price", min_value=0.0)
    high_price = st.number_input("Highest price", min_value=0.0)
    low_price = st.number_input("Lowest price", min_value=0.0)
    volume = st.number_input("Trading volume", min_value=0)

    if st.button("🔮 Predict"):
        if target_date and open_price and high_price and low_price and volume:
            prediction = predict_stock_price(symbol, target_date.strftime("%Y-%m-%d"), open_price, high_price, low_price, volume)
            st.success(f"📊 Predicted price: {prediction}")
        else:
            st.warning("⚠️ Please enter all required information!")

if __name__ == "__main__":
    stock_predict_screen()