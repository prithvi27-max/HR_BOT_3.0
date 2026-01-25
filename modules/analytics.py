import pandas as pd
import requests
import streamlit as st

# =========================================================
# SUPABASE CONFIG (READ FROM STREAMLIT SECRETS)
# =========================================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# =========================================================
# DATA LOADER (SUPABASE REST API)
# =========================================================
@st.cache_data(ttl=300)
def load_master():
    """
    Loads HR master data from Supabase (REST API).
    Cached for performance.
    """
    url = f"{SUPABASE_URL}/rest/v1/hr_master?select=*"
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    df = pd.DataFrame(response.json())

    # Safety: normalize column names
    df.columns = [c.strip() for c in df.columns]

    return df


# =========================================================
# CORE HR METRICS
# =========================================================
def headcount(df):
    """
    Active employee headcount
    """
    if "Status" not in df.columns:
        return 0
    return int((df["Status"] == "Active").sum())


def attrition_rate(df):
    """
    Attrition percentage
    """
    if "Status" not in df.columns or len(df) == 0:
        return 0.0

    resigned = (df["Status"] == "Resigned").sum()
    return round((resigned / len(df)) * 100, 2)


def avg_salary(df, group=None):
    """
    Average salary overall or grouped
    """
    if "Salary" not in df.columns:
        return None

    if group and group in df.columns:
        return (
            df.groupby(group)["Salary"]
            .mean()
            .round(2)
            .sort_values(ascending=False)
        )

    return round(df["Salary"].mean(), 2)


def gender_mix(df):
    """
    Gender distribution
    """
    if "Gender" not in df.columns:
        return None

    return df["Gender"].value_counts(normalize=True).round(2)


def engagement_stats(df):
    """
    Engagement KPIs
    """
    if "Engagement_Score" not in df.columns:
        return None

    return {
        "mean_engagement": round(df["Engagement_Score"].mean(), 2),
        "high_engagement_ratio": round((df["Engagement_Score"] >= 80).mean(), 2),
        "low_engagement_ratio": round((df["Engagement_Score"] < 50).mean(), 2),
    }


# =========================================================
# TREND & GROUP HELPERS (USED BY CHARTS)
# =========================================================
def group_count(df, group_col):
    """
    Generic group-by count helper
    """
    if group_col not in df.columns:
        return None

    return (
        df[group_col]
        .value_counts()
        .sort_values(ascending=False)
    )


def yearly_headcount(df):
    """
    Headcount trend by year (Hire Year)
    """
    if "Hire_Date" not in df.columns:
        return None

    df["Hire_Year"] = pd.to_datetime(df["Hire_Date"], errors="coerce").dt.year
    return df.groupby("Hire_Year").size()


def yearly_attrition(df):
    """
    Attrition trend by year
    """
    if "Exit_Date" not in df.columns or "Status" not in df.columns:
        return None

    resigned = df[df["Status"] == "Resigned"].copy()
    resigned["Exit_Year"] = pd.to_datetime(
        resigned["Exit_Date"], errors="coerce"
    ).dt.year

    return resigned.groupby("Exit_Year").size()
