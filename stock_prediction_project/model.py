import yfinance as yf
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression

def predict_stock(stock_name):

    # Download stock data
    data = yf.download(stock_name, period='1mo')

    # Fix columns
    data.columns = data.columns.get_level_values(0)

    # Keep only Close price
    data = data[['Close']]

    # Create days
    data['Days'] = np.arange(len(data))

    # Input
    X = data[['Days']]

    # Output
    y = data['Close']

    # ML Model
    model = LinearRegression()

    # Train model
    model.fit(X, y)

    # Predict next day
    future_day = [[len(data)]]

    prediction = model.predict(future_day)

    return round(float(prediction[0]), 2)