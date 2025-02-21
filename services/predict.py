import pickle
import pandas as pd
import os
from datetime import datetime, timedelta
from database.database import SessionLocal
from database.models import create_stock_table
from constants import strings

def calculate_ma_volatility(symbol: str, target_date: str):
    """Calculate MA10 and Volatility for target date based on historical data"""
    db = SessionLocal()
    StockTable = create_stock_table(symbol)
    
    # Convert target_date to datetime format
    target_date_dt = datetime.strptime(target_date, '%Y-%m-%d')

    # Get data 10 days before target date
    stock_data = db.query(StockTable).filter(
        StockTable.time < target_date_dt
    ).order_by(StockTable.time.desc()).limit(10).all()
    
    db.close()

    if len(stock_data) < 10:
        return None, None

    df = pd.DataFrame([s.__dict__ for s in stock_data])
    df = df.drop(columns=['_sa_instance_state', 'id'])

    df.set_index('time', inplace=True)

    ma_10 = df['close'].rolling(window=10, min_periods=1).mean().iloc[-1]
    returns = df['close'].pct_change().fillna(0)
    volatility = returns.rolling(window=5, min_periods=1).std().iloc[-1]

    return ma_10, volatility

def predict_stock_price(symbol: str, target_date: str, open_price: float, high_price: float, low_price: float, volume: float):
    """Predict the closing price of a stock on a specific date"""
    model_path = os.path.join(strings.MODEL_DIR, f"{symbol}_model.pkl")
    
    if not os.path.exists(model_path):
        return f"⚠️ Model for {symbol} not found. Please train the model first."

    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    try:
        target_date_str = target_date  
    except ValueError:
        return "❌ Invalid date format. Use YYYY-MM-DD."

    # Calculate ma_10 and volatility before converting target_date to ordinal
    ma_10, volatility = calculate_ma_volatility(symbol, target_date_str)

    if ma_10 is None or volatility is None:
        return f"⚠️ Not enough historical data to compute MA10 and volatility for {symbol}."

    target_date = datetime.strptime(target_date, '%Y-%m-%d').toordinal()

    # Prepare input data
    input_data = pd.DataFrame([[target_date, open_price, high_price, low_price, volume, ma_10, volatility]],
                              columns=['time', 'open', 'high', 'low', 'volume', 'ma_10', 'volatility'])

    predicted_price = model.predict(input_data)
    return round(predicted_price[0], 3)
