# Stock Analytics Application

This application provides an interactive dashboard for analyzing Vietnamese stock market data. It is built using Streamlit, Pandas, and Plotly.

## Features

- **Stock Selection**: Choose from a list of popular Vietnamese stocks.
- **Date Range**: Select the start and end dates for the analysis.
- **Update Interval**: Set the frequency for data updates.
- **Comparison**: Compare the selected stock with other stocks.
- **Moving Average (MA)**: Display the moving average for the selected stock.
- **Real-time Information**: View real-time stock prices and trends.
- **Order Book**: Display the latest buy/sell orders.
- **Raw Data**: Access the raw stock data.

## Installation

To run this application, you need to have Python installed along with the following packages:

```bash
pip install streamlit pandas plotly vnstock
```

## Usage

Run the application using the following command:

```bash
streamlit run app.py
```

## Code Overview

The main components of the application are:

1. **Sidebar**: Allows users to configure parameters such as stock symbol, date range, update interval, and comparison stocks.
2. **Main Container**: Displays the main stock chart with options to show/hide the moving average.
3. **Real-time Information**: Shows the current stock price, moving average price, and trend prediction.
4. **Tabs**: Includes tabs for the order book, stock comparison, and raw data.

## Customization

You can customize the appearance and functionality of the application by modifying the Streamlit and Plotly configurations in the code.

## License

This project is licensed under the MIT License.

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/)
- [Vnstock](https://github.com/vnstock/vnstock)

Feel free to contribute to this project by submitting issues or pull requests.
