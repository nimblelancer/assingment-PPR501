# Stock Market Analysis and Prediction

## Overview
This project provides tools for retrieving, storing, processing, and visualizing stock market data using Python. The system fetches data from the VNStock API and stores it in an SQLite database. It also features a machine learning model (Linear Regression) for predicting stock prices.

## Features
- Fetch real-time and historical stock data from the VNStock API
- Store stock data in SQLite for backup and performance optimization
- Predict stock prices using Linear Regression
- Visualize stock trends with interactive charts
- Separate modules for fetching, storing, and updating data efficiently

## Installation
```sh
pip install -r requirements.txt
```

## Usage
Run the Streamlit app:
```sh
streamlit run app.py
```

## Project Structure
- `database.py`: Manages SQLite database interactions
- `train.py`: Trains the Linear Regression model for stock prediction
- `predict.py`: Loads the trained model and predicts stock prices
- `stock_predict.py`: Streamlit-based UI for making predictions
- `app.py`: Main application entry point

## License
This project is licensed under the MIT License.