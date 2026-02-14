# modules/analytics.py

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
    try:
        url = f"{SUPABASE_URL}/rest/v1/hr_master?select=*"
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        df = pd.DataFrame(resp.json())
    except Exception:
        return pd.DataFrame()

    if df.empty:
        return df

    df.columns = [c.strip() for c in df.columns]

    # Standard cleanup
    if "Employee_ID" in df.columns:
        df["Employee_ID"] = df["Employee_ID"].astype(str)

    if "Hire_Date" in df.columns:
        df["Hire_Date"] = pd.to_datetime(df["Hire_Date"], errors="coerce")
        df["Hire_Year"] = df["Hire_Date"].dt.year

    if "Exit_Date" in df.columns:
        df["Exit_Date"] = pd.to_datetime(df["Exit_Date"], errors="coerce")
        df["Exit_Year"] = df["Exit_Date"].dt.year

    return df


# =========================================================
# HEADCOUNT
# =========================================================
def active_headcount(df):
    if "Status" not in df.columns:
        return 0
    active = df[df["Status"] == "Active"]
    return active["Employee_ID"].nunique()


def total_headcount(df):
    if "Employee_ID" not in df.columns:
        return 0
    return df["Employee_ID"].nunique()


def active_headcount_by(df, column):
    if "Status" not in df.columns or column not in df.columns:
        return None

    active = df[df["Status"] == "Active"]
    if active.empty:
        return None

    return (
        active.groupby(column)["Employee_ID"]
        .nunique()
        .sort_values(ascending=False)
    )


# ✅ Industry-correct headcount trend logic
def active_headcount_by_year(df):
    if "Hire_Year" not in df.columns:
        return None

    results = {}

    years = sorted(df["Hire_Year"].dropna().unique())

    for year in years:
        active = df[
            (df["Hire_Year"] <= year)
            & (
                df["Exit_Year"].isna()
                | (df["Exit_Year"] > year)
            )
        ]
        results[year] = active["Employee_ID"].nunique()

    if not results:
        return None

    return pd.Series(results).sort_index()


# =========================================================
# ATTRITION
# =========================================================
def attrition_count(df):
    if "Status" not in df.columns:
        return 0

    exited = df[df["Status"].isin(["Resigned", "Terminated"])]
    return exited["Employee_ID"].nunique()


# ✅ More stable enterprise formula
def attrition_rate(df):
    if df.empty:
        return 0.0

    exited = attrition_count(df)
    total = total_headcount(df)

    if total == 0:
        return 0.0

    return round((exited / total) * 100, 2)


def attrition_rate_by(df, column):
    if column not in df.columns:
        return None

    results = {}

    for val in df[column].dropna().unique():
        sub = df[df[column] == val]

        total = total_headcount(sub)
        exited = attrition_count(sub)

        results[val] = round((exited / total) * 100, 2) if total else 0

    if not results:
        return None

    return pd.Series(results).sort_values(ascending=False)


def attrition_by_year(df):
    if "Exit_Year" not in df.columns:
        return None

    exited = df[df["Status"].isin(["Resigned", "Terminated"])]

    if exited.empty:
        return None

    return (
        exited.groupby("Exit_Year")["Employee_ID"]
        .nunique()
        .sort_index()
    )


# =========================================================
# SALARY
# =========================================================
def average_salary(df):
    if "Salary" not in df.columns or df.empty:
        return 0.0
    return round(df["Salary"].mean(), 2)


def average_salary_by(df, column):
    if column not in df.columns or "Salary" not in df.columns:
        return None

    grouped = df.groupby(column)["Salary"].mean().round(2)

    if grouped.empty:
        return None

    return grouped.sort_values(ascending=False)


# =========================================================
# ENGAGEMENT
# =========================================================
def average_engagement(df):
    if "Engagement_Score" not in df.columns or df.empty:
        return 0.0
    return round(df["Engagement_Score"].mean(), 2)


def engagement_by(df, column):
    if column not in df.columns or "Engagement_Score" not in df.columns:
        return None

    grouped = df.groupby(column)["Engagement_Score"].mean().round(2)

    if grouped.empty:
        return None

    return grouped.sort_values(ascending=False)


# =========================================================
# DIVERSITY
# =========================================================
def gender_distribution(df):
    if "Gender" not in df.columns or "Status" not in df.columns:
        return None

    active = df[df["Status"] == "Active"]

    if active.empty:
        return None

    return active["Gender"].value_counts()
