from prophet import Prophet
import pandas as pd

class DemandForecaster:
    def __init__(self):
        self.model = Prophet()

    def train(self, df):
        df = df.rename(columns={"date": "ds", "demand": "y"})
        self.model.fit(df)

    def predict(self, periods=10):
        future = self.model.make_future_dataframe(periods=periods)
        forecast = self.model.predict(future)
        return forecast[["ds", "yhat"]]