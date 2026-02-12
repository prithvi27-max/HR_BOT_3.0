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
    url = f"{SUPABASE_URL}/rest/v1/hr_master?select=*"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()

    df = pd.DataFrame(resp.json())
    df.columns = [c.strip() for c in df.columns]

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
    """Active headcount (default HR meaning)"""
    active = df[df["Status"] == "Active"]
    return active["Employee_ID"].nunique()


def total_headcount(df):
    """All employees ever (historical)"""
    return df["Employee_ID"].nunique()


def active_headcount_by(df, column):
    active = df[df["Status"] == "Active"]
    if column not in active.columns:
        return None
    return active.groupby(column)["Employee_ID"].nunique().sort_values(ascending=False)


def active_headcount_by_year(df):
    active = df[df["Status"] == "Active"]
    if "Hire_Year" not in active.columns:
        return None
    return active.groupby("Hire_Year")["Employee_ID"].nunique().sort_index()


# ==================================================
# 🔄 ATTRITION
# ==================================================
    if metric == "attrition":

        if not dimension:
            return pd.DataFrame({
            "Metric": [t("ATTRITION_RATE", language)],
            "Value": [attrition_rate(df)]
        })

    col_map = {
        "DEPARTMENT": "Department",
        "LOCATION": "Location",
        "GENDER": "Gender"
    }

    if dimension == "YEAR":
        data = attrition_by_year(df)
    else:
        data = attrition_rate_by(df, col_map.get(dimension))

    # 🛑 SAFE GUARD
    if data is None or len(data) == 0:
        return "⚠ No attrition data available for this breakdown."

    return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Attrition Rate")

# =========================================================
# SALARY
# =========================================================
def average_salary(df):
    return round(df["Salary"].mean(), 2)


def average_salary_by(df, column):
    if column not in df.columns:
        return None
    return df.groupby(column)["Salary"].mean().round(2).sort_values(ascending=False)


# =========================================================
# ENGAGEMENT
# =========================================================
def average_engagement(df):
    return round(df["Engagement_Score"].mean(), 2)


def engagement_by(df, column):
    if column not in df.columns:
        return None
    return df.groupby(column)["Engagement_Score"].mean().round(2).sort_values(ascending=False)


# =========================================================
# DIVERSITY
# =========================================================
def gender_distribution(df):
    active = df[df["Status"] == "Active"]
    return active["Gender"].value_counts()
