import os
import pickle
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from constants import strings
from database.database import SessionLocal
from database.models import create_stock_table

def train_model(symbol: str):
    """Training a stock price prediction model for a stock symbol"""
    db = SessionLocal()
    StockTable = create_stock_table(symbol)
    stock_data = db.query(StockTable).all()
    db.close()

    if not stock_data:
        print(f"❌ No data found for {symbol}. Skipping training...")
        return
    
    df = pd.DataFrame([s.__dict__ for s in stock_data])
    df.drop(columns=['_sa_instance_state', 'id'], inplace=True)
    df['time'] = pd.to_datetime(df['time']).map(pd.Timestamp.toordinal)
    
    df['returns'] = df['close'].pct_change()
    df['volatility'] = df['returns'].rolling(window=5).std()
    df['ma_10'] = df['close'].rolling(window=10).mean()
    # Check and process data is miss
    df.dropna(inplace=True)
    
    X = df[['time', 'open', 'high', 'low', 'volume', 'ma_10', 'volatility']]
    y = df['close']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Model Evaluation
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"✅ {symbol}: R² = {r2:.4f}, MAE = {mae:.4f}")
    
    # Save model
    os.makedirs(strings.MODEL_DIR, exist_ok=True)
    model_path = os.path.join(strings.MODEL_DIR, f"{symbol}_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    
    print(f"✅ Model trained and saved for {symbol}!")


def train_all_models(symbols: list):
    """Train the model for the list of stock codes"""
    for symbol in symbols:
        train_model(symbol)


if __name__ == "__main__":
    from vnstock import Vnstock
    symbols = Vnstock().stock().listing.symbols_by_group('VN30')
    train_all_models(symbols)