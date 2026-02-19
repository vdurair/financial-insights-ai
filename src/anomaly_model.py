from sklearn.ensemble import IsolationForest

def train_anomaly_model(df):
    model = IsolationForest(
        contamination=0.05,
        random_state=42,
        n_estimators=200
    )
    model.fit(df[["amount"]])
    return model

def score_transactions(model, df):
    df = df.copy()
    df["anomaly_score"] = model.decision_function(df[["amount"]])
    df["is_anomaly"] = model.predict(df[["amount"]]) == -1
    return df

# Class-based interface for anomaly detection
class AnomalyDetector:
    def __init__(self, contamination=0.05, random_state=42, n_estimators=200):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=n_estimators
        )
        self.is_fitted = False

    def fit(self, df):
        self.model.fit(df[["amount"]])
        self.is_fitted = True

    def score(self, df):
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        df = df.copy()
        df["anomaly_score"] = self.model.decision_function(df[["amount"]])
        df["is_anomaly"] = self.model.predict(df[["amount"]]) == -1
        return df

    def is_anomaly(self, transaction):
        # transaction: dict with 'amount' key
        if not self.is_fitted:
            raise RuntimeError("Model not fitted. Call fit() first.")
        import numpy as np
        amount = transaction["amount"]
        pred = self.model.predict(np.array([[amount]]))
        return pred[0] == -1