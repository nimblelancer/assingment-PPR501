# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LinearRegression
# import pickle
# from database.db import get_db
# from database.models import StockPrice

# def train_model(symbol: str):
#     """Huấn luyện mô hình dự đoán giá cổ phiếu"""
#     db = next(get_db())
#     stock_data = db.query(StockPrice).filter(StockPrice.symbol == symbol).all()
#     db.close()

#     df = pd.DataFrame([s.__dict__ for s in stock_data])
#     df = df.drop(columns=['_sa_instance_state', 'id', 'symbol'])

#     # Dữ liệu đầu vào (features) và đầu ra (target)
#     df['date'] = pd.to_datetime(df['date']).map(pd.Timestamp.toordinal)
#     X = df[['date', 'open_price', 'high_price', 'low_price', 'volume']]
#     y = df['close_price']

#     # Chia tập dữ liệu
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#     # Huấn luyện mô hình
#     model = LinearRegression()
#     model.fit(X_train, y_train)

#     # Lưu mô hình vào file
#     with open(f'ml_model/{symbol}_model.pkl', 'wb') as f:
#         pickle.dump(model, f)

#     print(f"Model trained and saved for {symbol}!")