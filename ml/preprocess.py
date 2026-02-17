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

    df["Attrition"] = (df["Status"] == "Resigned").astype(int)

    # MUST MATCH TRAINING EXACTLY
    feature_cols = [
        "Age",
        "Salary",
        "Experience_Years",
        "Engagement_Score",
        "Performance_Rating"
    ]

    X = df[feature_cols].copy()
    X = X.fillna(X.mean())

    y = df["Attrition"]

    return X, y

