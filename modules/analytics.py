import pandas as pd
import requests
import streamlit as st
from datetime import datetime

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

    df["Hire_Date"] = pd.to_datetime(df["Hire_Date"], errors="coerce")
    df["Exit_Date"] = pd.to_datetime(df["Exit_Date"], errors="coerce")

    return df


# =========================================================
# HELPER → ACTIVE WORKFORCE SNAPSHOT
# =========================================================
def active_workforce(df, snapshot_date=None):

    if snapshot_date is None:
        snapshot_date = pd.Timestamp.today()

    return df[
        (df["Hire_Date"] <= snapshot_date)
        &
        (
            df["Exit_Date"].isna()
            | (df["Exit_Date"] > snapshot_date)
        )
    ]


# =========================================================
# HEADCOUNT
# =========================================================
def active_headcount(df):

    return active_workforce(df)["Employee_ID"].nunique()


def total_headcount(df):

    return df["Employee_ID"].nunique()


def active_headcount_by(df, column):

    wf = active_workforce(df)

    if column not in wf.columns:
        return None

    return wf.groupby(column)["Employee_ID"].nunique().sort_values(ascending=False)


def active_headcount_by_year(df):

    years = pd.date_range(df["Hire_Date"].min(), pd.Timestamp.today(), freq="Y")

    result = {}

    for d in years:
        result[d.year] = active_workforce(df, d)["Employee_ID"].nunique()

    return pd.Series(result)


# =========================================================
# ATTRITION
# =========================================================
def attrition_rate(df):

    current_year = pd.Timestamp.today().year

    exits = df[
        df["Exit_Date"].dt.year == current_year
    ]["Employee_ID"].nunique()

    workforce = active_workforce(
        df,
        pd.Timestamp(year=current_year, month=12, day=31)
    )["Employee_ID"].nunique()

    if workforce == 0:
        return 0

    return round((exits / workforce) * 100, 2)


def attrition_rate_by(df, column):

    if column not in df.columns:
        return None

    exited = df[df["Exit_Date"].notna()]

    result = {}

    for val in df[column].dropna().unique():

        sub = df[df[column] == val]

        exits = sub[sub["Exit_Date"].notna()]["Employee_ID"].nunique()
        workforce = active_workforce(sub)["Employee_ID"].nunique()

        if workforce == 0:
            result[val] = 0
        else:
            result[val] = round((exits / workforce) * 100, 2)

    return pd.Series(result).sort_values(ascending=False)


def attrition_by_year(df):

    exited = df[df["Exit_Date"].notna()]

    return exited.groupby(
        exited["Exit_Date"].dt.year
    )["Employee_ID"].nunique()


# =========================================================
# SALARY
# =========================================================
def average_salary(df):

    return round(active_workforce(df)["Salary"].mean(), 2)


def average_salary_by(df, column):

    wf = active_workforce(df)

    if column not in wf.columns:
        return None

    return wf.groupby(column)["Salary"].mean().round(2)


# =========================================================
# ENGAGEMENT
# =========================================================
def average_engagement(df):

    return round(active_workforce(df)["Engagement_Score"].mean(), 2)


def engagement_by(df, column):

    wf = active_workforce(df)

    if column not in wf.columns:
        return None

    return wf.groupby(column)["Engagement_Score"].mean().round(2)


# =========================================================
# DIVERSITY
# =========================================================
def gender_distribution(df):

    return active_workforce(df)["Gender"].value_counts()
