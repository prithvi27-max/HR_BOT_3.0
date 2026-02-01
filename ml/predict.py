import joblib
import pandas as pd

MODEL_PATH = "ml/models/attrition_ensemble.pkl"

# -------------------------------
# Load trained ML model
# -------------------------------
def load_attrition_model():
    return joblib.load(MODEL_PATH)

# -------------------------------
# Predict attrition probability
# -------------------------------
def predict_attrition(df):
    model = load_attrition_model()

    features = [
        "Age",
        "Salary",
        "Experience_Years",
        "Engagement_Score",
        "Performance_Rating"
    ]

    # Safety check
    missing = [f for f in features if f not in df.columns]
    if missing:
        raise ValueError(f"Missing ML features: {missing}")

    X = df[features].copy()
    X = X.fillna(X.mean(numeric_only=True))

    df_out = df.copy()
    df_out["Attrition_Risk"] = model.predict_proba(X)[:, 1]

    return df_out[["Employee_ID", "Attrition_Risk"]]

# -------------------------------
# ADD RISK BUCKET (🔥 THIS WAS MISSING)
# -------------------------------
def add_risk_bucket(df):
    """
    Converts attrition probability into interpretable risk buckets
    """
    def bucketize(p):
        if p >= 0.70:
            return "High"
        elif p >= 0.40:
            return "Medium"
        else:
            return "Low"

    df = df.copy()
    df["Risk_Bucket"] = df["Attrition_Risk"].apply(bucketize)
    return df
