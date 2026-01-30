# ml/predict.py

import joblib
import pandas as pd

MODEL_PATH = "ml/models/attrition_ensemble.pkl"

REQUIRED_FEATURES = [
    "Age",
    "Salary",
    "Experience_Years",
    "Engagement_Score",
    "Performance_Rating"
]


def load_attrition_model():
    return joblib.load(MODEL_PATH)


def predict_attrition(df: pd.DataFrame) -> pd.DataFrame:
    model = load_attrition_model()

    # --- Validate required features ---
    missing = [c for c in REQUIRED_FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing ML features: {missing}")

    X = df[REQUIRED_FEATURES].copy()

    # --- Force numeric conversion ---
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")

    # --- Handle missing values ---
    X = X.fillna(X.mean())

    # --- Predict attrition probability ---
    probs = model.predict_proba(X)[:, 1]

    result = df[["Employee_ID"]].copy()
    result["Attrition_Risk"] = probs.round(4)

    return result

def add_risk_bucket(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts attrition probability into HR-friendly risk buckets
    """
    df = df.copy()

    df["Risk_Bucket"] = pd.cut(
        df["Attrition_Risk"],
        bins=[0, 0.4, 0.7, 1.0],
        labels=["Low", "Medium", "High"]
    )

    return df
