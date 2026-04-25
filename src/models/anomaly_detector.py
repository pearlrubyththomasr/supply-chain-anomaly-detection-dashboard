from sklearn.ensemble import IsolationForest
import pandas as pd

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.trained = False

    def train(self, df):
        features = df[["demand", "inventory", "lead_time"]]
        self.model.fit(features)
        self.trained = True

    def predict(self, data):
        df = pd.DataFrame([data])
        pred = self.model.predict(df)
        return 1 if pred[0] == -1 else 0