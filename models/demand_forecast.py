import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def forecast_demand(sales_df, days=7):
    sales_df = sales_df.copy()
    sales_df['day'] = np.arange(len(sales_df))

    X = sales_df[['day']]
    y = sales_df['quantity_sold']

    model = LinearRegression()
    model.fit(X, y)

    future_days = np.arange(len(sales_df), len(sales_df) + days).reshape(-1, 1)
    forecast = model.predict(future_days)

    return int(max(forecast.sum(), 0))