import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================
# DATABASE CONNECTION
# ============================
DATABASE_URL = os.getenv("SUPABASE_DB_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800
)

# ============================
# LOAD MASTER DATA
# ============================
def load_master():
    """
    Load HR master data from Supabase Postgres
    """
    query = "SELECT * FROM hr_master"
    df = pd.read_sql(query, engine)

    # Convert date columns safely
    if "hire_date" in df.columns:
        df["hire_date"] = pd.to_datetime(df["hire_date"], errors="coerce")
        df["hire_year"] = df["hire_date"].dt.year

    return df


# ============================
# BASIC HR METRICS
# ============================
def headcount(df):
    return df[df["status"] == "Active"].shape[0]


def attrition_rate(df):
    total = len(df)
    resigned = df[df["status"] == "Resigned"].shape[0]
    return round((resigned / total) * 100, 2)


def avg_salary(df, group=None):
    if group and group.lower() in df.columns:
        return (
            df.groupby(group.lower())["salary"]
            .mean()
            .round(2)
            .to_dict()
        )
    return round(df["salary"].mean(), 2)


def gender_mix(df):
    return (
        df["gender"]
        .value_counts(normalize=True)
        .round(2)
        .to_dict()
    )


def engagement_stats(df):
    return {
        "mean_engagement": round(df["engagement_score"].mean(), 2),
        "high_engagement": round((df["engagement_score"] > 80).mean(), 2),
        "low_engagement": round((df["engagement_score"] < 50).mean(), 2),
    }
