# ml/preprocess.py

import pandas as pd

def load_base(path="data/hr_master_10000.csv"):
    """
    Loads the HR master dataset for ML models.
    Ensures Status column is clean.
    """
    df = pd.read_csv(path)
    
    # Basic cleanup
    if "Status" in df.columns:
        df["Status"] = df["Status"].astype(str).str.strip()

    return df


def preprocess_for_attrition(df):
    """
    Generates ML-ready features and target for attrition prediction.
    Target = 1 if Status == Resigned
    """

    # Target column
    df["Attrition"] = (df["Status"] == "Resigned").astype(int)

    # Select features
    feature_cols = [
        "Age",
        "Experience_Years",
        "Salary",
        "Performance_Rating",
        "Engagement_Score",
        "Job_Level"
    ]

    # Keep only features that exist in dataset (avoid KeyErrors)
    existing = [c for c in feature_cols if c in df.columns]

    X = df[existing].copy()
    X = X.fillna(X.mean())  # impute missing numeric values

    y = df["Attrition"]

    return X, y
