import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# -----------------------------
# DATABASE CONNECTION (SUPABASE)
# -----------------------------
@st.cache_resource
def get_engine():
    db_url = st.secrets["SUPABASE_DB_URL"]
    return create_engine(
        db_url,
        pool_pre_ping=True,
        connect_args={"sslmode": "require"}
    )

# -----------------------------
# DATA LOADER
# -----------------------------
def load_master():
    engine = get_engine()
    query = "SELECT * FROM hr_master"
    df = pd.read_sql(query, engine)
    return df

# -----------------------------
# HR METRICS
# -----------------------------
def headcount(df):
    return df[df["Status"] == "Active"].shape[0]

def attrition_rate(df):
    total = len(df)
    resigned = (df["Status"] == "Resigned").sum()
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
