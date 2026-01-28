import pandas as pd
import plotly.express as px

# ----------------------------------
# Dimension → Column mapping
# ----------------------------------
DIMENSION_COLUMN_MAP = {
    "DEPARTMENT": "Department",
    "LOCATION": "Location",
    "GENDER": "Gender",
    "YEAR": "Hire_Year"
}

# ----------------------------------
# Date normalization
# ----------------------------------
def ensure_date_and_year(df):
    if "Hire_Date" in df.columns:
        df["Hire_Date"] = pd.to_datetime(df["Hire_Date"], errors="coerce")
        df["Hire_Year"] = df["Hire_Date"].dt.year
    return df

# ----------------------------------
# Safe filter application
# ----------------------------------
def apply_filters(df, filters):
    if not filters:
        return df

    for f in filters:
        col = f.get("column")
        val = f.get("value")
        if col in df.columns:
            df = df[df[col] == val]

    return df

# ==================================================
# FINAL compute_metric (ONE TRUE SIGNATURE)
# ==================================================
def compute_metric(df, metric, dimension, filters=None):
    df = ensure_date_and_year(df)
    df = apply_filters(df, filters)

    if not dimension:
        return None

    column = DIMENSION_COLUMN_MAP.get(dimension)
    if column not in df.columns:
        return None

    if metric == "headcount":
        return df.groupby(column)["Employee_ID"].count()

    if metric == "salary":
        return df.groupby(column)["Salary"].mean().round(2)

    if metric == "gender":
        return df.groupby(column)["Employee_ID"].count()

    if metric == "attrition":
        df["_attr"] = (df["Status"] == "Resigned").astype(int)
        return (df.groupby(column)["_attr"].mean() * 100).round(2)

    return None

# ----------------------------------
# Trend metrics (ONLY when asked)
# ----------------------------------
def compute_trend_metric(df, metric):
    df = ensure_date_and_year(df)

    if "Hire_Year" not in df.columns:
        return None

    if metric == "headcount":
        return df.groupby("Hire_Year")["Employee_ID"].count()

    if metric == "salary":
        return df.groupby("Hire_Year")["Salary"].mean().round(2)

    if metric == "attrition":
        df["_attr"] = (df["Status"] == "Resigned").astype(int)
        return (df.groupby("Hire_Year")["_attr"].mean() * 100).round(2)

    return None

# ----------------------------------
# Chart builder (ONLY when requested)
# ----------------------------------
def build_chart(data, chart_type):
    if data is None or len(data) == 0:
        return None

    df_plot = data.reset_index()
    x, y = df_plot.columns

    if chart_type == "LINE":
        return px.line(df_plot, x=x, y=y, markers=True)

    if chart_type == "PIE":
        return px.pie(df_plot, names=x, values=y)

    # Default BAR
    return px.bar(df_plot, x=x, y=y, text_auto=True)
