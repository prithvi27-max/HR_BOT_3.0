# ml/predict.py

import joblib
import pandas as pd

MODEL_PATH = "ml/models/attrition_ensemble.pkl"

FEATURES = [
    "Age",
    "Salary",
    "Experience_Years",
    "Engagement_Score",
    "Performance_Rating"
]


def risk_bucket(p):
    if p >= 0.7:
        return "High"
    elif p >= 0.4:
        return "Medium"
    return "Low"


def load_attrition_model():
    return joblib.load(MODEL_PATH)


def predict_attrition(df: pd.DataFrame):
    """
    Returns attrition risk for ALL employees
    """
    model = load_attrition_model()

    X = df[FEATURES].copy()
    X = X.fillna(X.mean())

    probs = model.predict_proba(X)[:, 1]

    out = df[["Employee_ID", "Status"]].copy()
    out["Attrition_Risk"] = probs.round(4)
    out["Risk_Bucket"] = out["Attrition_Risk"].apply(risk_bucket)

    return out
