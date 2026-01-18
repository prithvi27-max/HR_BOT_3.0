import pandas as pd
from sqlalchemy import create_engine

# 🔹 MySQL connection (use the same credentials that worked earlier)
engine = create_engine(
    "mysql+mysqlconnector://root:mysql123@localhost/hr_analytics_db"
)

# -----------------------------
# DATA LOADER (MySQL)
# -----------------------------
def load_master():
    """
    Loads HR master data from MySQL database.
    """
    query = "SELECT * FROM hr_master"
    df = pd.read_sql(query, engine)
    return df


# -----------------------------
# BASIC HR METRICS
# -----------------------------
def headcount(df):
    """
    Returns active employee headcount.
    """
    return df[df["Status"] == "Active"].shape[0]


def attrition_rate(df):
    """
    Returns attrition percentage.
    """
    total = df.shape[0]
    resigned = df[df["Status"] == "Resigned"].shape[0]
    return round((resigned / total) * 100, 2)


def avg_salary(df, group=None):
    """
    Returns average salary.
    If group is provided (e.g., Department), returns grouped averages.
    """
    if group and group in df.columns:
        return df.groupby(group)["Salary"].mean().round(2).to_dict()
    return round(df["Salary"].mean(), 2)


def gender_mix(df):
    """
    Returns gender ratio.
    """
    return df["Gender"].value_counts(normalize=True).round(2).to_dict()


def engagement_stats(df):
    """
    Returns engagement statistics.
    """
    return {
        "mean_engagement": round(df["Engagement_Score"].mean(), 2),
        "high_engagement": round((df["Engagement_Score"] > 80).mean(), 2),
        "low_engagement": round((df["Engagement_Score"] < 50).mean(), 2),
    }
