import pickle
import pandas as pd
from datetime import datetime

def predict_stock_price(symbol: str, target_date: str, open_price: float, high_price: float, low_price: float, volume: float):
    """Dự đoán giá cổ phiếu vào một ngày cụ thể"""
    try:
        with open(f'ml_model/{symbol}_model.pkl', 'rb') as f:
            model = pickle.load(f)
    except FileNotFoundError:
        return "Model not found. Please train the model first."

    # Chuyển đổi ngày thành số
    target_date = datetime.strptime(target_date, '%Y-%m-%d').toordinal()

    # Chuẩn bị dữ liệu đầu vào
    input_data = pd.DataFrame([[target_date, open_price, high_price, low_price, volume]],
                              columns=['date', 'open_price', 'high_price', 'low_price', 'volume'])

    # Dự đoán giá đóng cửa
    predicted_price = model.predict(input_data)
    return round(predicted_price[0], 3)
