import pandas as pd
from datetime import datetime

def load_master(path="data/hr_master_10000.csv"):
    df = pd.read_csv(path)
    return df

def headcount(df):
    return df[df["Status"] == "Active"].shape[0]

def attrition_rate(df):
    total = df.shape[0]
    resigned = df[df["Status"] == "Resigned"].shape[0]
    return round((resigned / total) * 100, 2)

def avg_salary(df, group=None):
    if group and group in df.columns:
        return df.groupby(group)["Salary"].mean().round(2).to_dict()
    return round(df["Salary"].mean(), 2)

def gender_mix(df):
    return df["Gender"].value_counts(normalize=True).round(2).to_dict()

def engagement_stats(df):
    return {
        "mean_engagement": round(df["Engagement_Score"].mean(), 2),
        "high_engagement": (df["Engagement_Score"] > 80).mean().round(2),
        "low_engagement": (df["Engagement_Score"] < 50).mean().round(2),
    }
