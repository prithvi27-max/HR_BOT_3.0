import pandas as pd
import requests
import streamlit as st

# =========================================================
# SUPABASE CONFIG
# =========================================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# =========================================================
# DATA LOADER
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
    df.columns = [c.strip() for c in df.columns]
    return df


# =========================================================
# DATE NORMALIZATION (INTERNAL UTILITY)
# =========================================================
def _normalize_dates(df):
    df = df.copy()
    if "Hire_Date" in df.columns:
        df["Hire_Date"] = pd.to_datetime(df["Hire_Date"], errors="coerce")
    if "Exit_Date" in df.columns:
        df["Exit_Date"] = pd.to_datetime(df["Exit_Date"], errors="coerce")
    return df


# =========================================================
# SIMPLE KPI HELPERS (DASHBOARD LEVEL)
# =========================================================
def headcount(df):
    """
    Simple active headcount (legacy KPI)
    """
    if "Status" not in df.columns:
        return 0
    return int((df["Status"] == "Active").sum())


def attrition_rate(df):
    """
    Simple attrition % (legacy KPI)
    """
    if "Status" not in df.columns or len(df) == 0:
        return 0.0
    resigned = (df["Status"] == "Resigned").sum()
    return round((resigned / len(df)) * 100, 2)


def avg_salary(df):
    if "Salary" not in df.columns:
        return None
    return round(df["Salary"].mean(), 2)


def gender_mix(df):
    if "Gender" not in df.columns:
        return None
    return df["Gender"].value_counts(normalize=True).round(2)


def engagement_stats(df):
    if "Engagement_Score" not in df.columns:
        return None
    return {
        "mean_engagement": round(df["Engagement_Score"].mean(), 2),
        "high_engagement_ratio": round((df["Engagement_Score"] >= 80).mean(), 2),
        "low_engagement_ratio": round((df["Engagement_Score"] < 50).mean(), 2),
    }


# =========================================================
# ENTERPRISE-CORRECT ANALYTICS (USED BY ROUTER)
# =========================================================

# ---------- HEADCOUNT ----------
def total_headcount(df):
    """
    Enterprise-correct headcount:
    DISTINCT Employee_ID
    """
    if "Employee_ID" not in df.columns:
        return 0
    return df["Employee_ID"].nunique()


def headcount_by_dimension(df, column):
    """
    Headcount by department / location / gender
    """
    if column not in df.columns or "Employee_ID" not in df.columns:
        return None
    return df.groupby(column)["Employee_ID"].nunique()


def headcount_by_year_snapshot(df):
    """
    Snapshot headcount by year.
    Matches Excel pivot logic exactly.
    """
    if "Hire_Date" not in df.columns:
        return None

    df = _normalize_dates(df)

    min_year = int(df["Hire_Date"].dt.year.min())
    max_year = int(df["Hire_Date"].dt.year.max())

    result = {}

    for year in range(min_year, max_year + 1):
        start = pd.Timestamp(f"{year}-01-01")
        end = pd.Timestamp(f"{year}-12-31")

        active = df[
            (df["Hire_Date"] <= end) &
            (
                df["Exit_Date"].isna() |
                (df["Exit_Date"] >= start)
            )
        ]

        result[year] = active["Employee_ID"].nunique()

    return pd.Series(result)


# ---------- ATTRITION ----------
def attrition_count_by_dimension(df, column):
    """
    Distinct attrition count by dimension
    """
    if column not in df.columns or "Status" not in df.columns:
        return None

    resigned = df[df["Status"] == "Resigned"]
    return resigned.groupby(column)["Employee_ID"].nunique()


def attrition_count_by_year(df):
    """
    Distinct attrition count by exit year
    """
    if "Exit_Date" not in df.columns or "Employee_ID" not in df.columns:
        return None

    df = _normalize_dates(df)
    resigned = df[df["Status"] == "Resigned"]

    return resigned.groupby(
        resigned["Exit_Date"].dt.year
    )["Employee_ID"].nunique()


# ---------- SALARY ----------
def avg_salary_by_dimension(df, column):
    if column not in df.columns or "Salary" not in df.columns:
        return None
    return df.groupby(column)["Salary"].mean().round(2)


# ---------- ENGAGEMENT ----------
def avg_engagement_by_dimension(df, column):
    if column not in df.columns or "Engagement_Score" not in df.columns:
        return None
    return df.groupby(column)["Engagement_Score"].mean().round(2)
