import os
import pandas as pd
from sqlalchemy import create_engine

# ============================
# CONFIG
# ============================
CSV_PATH = "data/hr_master_10000.csv"

# DATABASE_URL will be set only in LOCAL or CLOUD DB
DB_URL = os.getenv("DATABASE_URL")


# ============================
# DATA LOADER
# ============================
def load_master():
    """
    Loads HR master data.
    Priority:
    1. Cloud / Local Database (if DATABASE_URL exists)
    2. CSV fallback (Streamlit-safe)
    """

    if DB_URL:
        try:
            engine = create_engine(DB_URL)
            df = pd.read_sql("SELECT * FROM hr_master", engine)
            return df
        except Exception as e:
            print("⚠ Database unavailable, using CSV:", e)

    # Safe fallback
    return pd.read_csv(CSV_PATH)


# ============================
# HR METRICS
# ============================
def headcount(df):
    return df[df["Status"] == "Active"].shape[0]


def attrition_rate(df):
    total = len(df)
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
        "high_engagement": round((df["Engagement_Score"] > 80).mean(), 2),
        "low_engagement": round((df["Engagement_Score"] < 50).mean(), 2),
    }
