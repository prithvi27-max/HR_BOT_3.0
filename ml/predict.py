import joblib
import pandas as pd

MODEL_PATH = "ml/models/attrition_ensemble.pkl"

def load_attrition_model():
    return joblib.load(MODEL_PATH)

def predict_attrition(df):
    model = load_attrition_model()

    features = [
        "Age",
        "Salary",
        "Experience_Years",
        "Engagement_Score",
        "Performance_Rating"
    ]

    X = df[features]
    df["Attrition_Risk"] = model.predict_proba(X)[:, 1]

    return df[["Employee_ID", "Attrition_Risk"]]
