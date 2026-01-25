import pandas as pd
import requests
import streamlit as st

# Read from Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

# -----------------------------
# DATA LOADER (SUPABASE REST)
# -----------------------------
def load_master():
    url = f"{SUPABASE_URL}/rest/v1/hr_master?select=*"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return pd.DataFrame(response.json())

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
        return df.groupby(group)["Salary"].mean().round(2)
    return round(df["Salary"].mean(), 2)

def gender_mix(df):
    return df["Gender"].value_counts(normalize=True).round(2)

def engagement_stats(df):
    return {
        "mean": round(df["Engagement_Score"].mean(), 2),
        "high": round((df["Engagement_Score"] > 80).mean(), 2),
        "low": round((df["Engagement_Score"] < 50).mean(), 2),
    }
