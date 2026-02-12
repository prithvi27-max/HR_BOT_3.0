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

    if df.empty:
        return df

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
    active = df[df["Status"] == "Active"]
    return active["Employee_ID"].nunique()


def total_headcount(df):
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


# =========================================================
# ATTRITION
# =========================================================
def attrition_count(df):
    exited = df[df["Status"].isin(["Resigned", "Terminated"])]
    return exited["Employee_ID"].nunique()


def attrition_rate(df):
    active = active_headcount(df)
    exited = attrition_count(df)

    if active == 0:
        return 0.0

    return round((exited / active) * 100, 2)


def attrition_rate_by(df, column):
    if column not in df.columns:
        return None

    rates = {}
    for val in df[column].dropna().unique():
        sub = df[df[column] == val]
        active = active_headcount(sub)
        exited = attrition_count(sub)
        rates[val] = round((exited / active) * 100, 2) if active else 0

    return pd.Series(rates).sort_values(ascending=False)


def attrition_by_year(df):
    exited = df[df["Status"].isin(["Resigned", "Terminated"])]
    if "Exit_Year" not in exited.columns:
        return None
    return exited.groupby("Exit_Year")["Employee_ID"].nunique().sort_index()


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
