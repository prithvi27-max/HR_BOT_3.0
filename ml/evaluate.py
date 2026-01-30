# ml/evaluate.py

import joblib
import pandas as pd

METRICS_PATH = "ml/models/attrition_metrics.pkl"


def load_ml_metrics():
    metrics = joblib.load(METRICS_PATH)

    return pd.DataFrame(
        metrics.items(),
        columns=["Metric", "Value"]
    ).round(3)
