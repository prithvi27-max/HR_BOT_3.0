import pandas as pd
import plotly.express as px


# =========================================================
# NLU → DATAFRAME COLUMN MAPPING
# =========================================================
DIMENSION_COLUMN_MAP = {
    "DEPARTMENT": "Department",
    "LOCATION": "Location",
    "GENDER": "Gender",
    "YEAR": "Hire_Year",
    "MONTH": "Hire_Month"
}


# =========================================================
# DATE NORMALIZATION (SAFE)
# =========================================================
def ensure_date_and_year(df):
    if "Hire_Date" in df.columns:
        df["Hire_Date"] = pd.to_datetime(
            df["Hire_Date"], errors="coerce", dayfirst=True
        )
        df["Hire_Year"] = df["Hire_Date"].dt.year
        df["Hire_Month"] = df["Hire_Date"].dt.month
    return df


# =========================================================
# GROUPED METRICS (BAR / PIE)
# =========================================================
def compute_metric(df, metric, dimension):
    df = ensure_date_and_year(df)

    if not dimension:
        return None

    # 🔑 Map NLU dimension → dataframe column
    column = DIMENSION_COLUMN_MAP.get(dimension)

    if column is None or column not in df.columns:
        return None

    # ---------------------------
    # HEADCOUNT
    # ---------------------------
    if metric == "headcount":
        return df.groupby(column)["Employee_ID"].count()

    # ---------------------------
    # SALARY
    # ---------------------------
    if metric == "salary":
        return df.groupby(column)["Salary"].mean().round(2)

    # ---------------------------
    # GENDER DISTRIBUTION
    # ---------------------------
    if metric == "gender":
        return df.groupby(column)["Employee_ID"].count()

    # ---------------------------
    # ATTRITION %
    # ---------------------------
    if metric == "attrition":
        df["Attrition_Flag"] = (df["Status"] == "Resigned").astype(int)
        return (df.groupby(column)["Attrition_Flag"].mean() * 100).round(2)

    return None


# =========================================================
# TREND METRICS (LINE)
# =========================================================
def compute_trend_metric(df, metric):
    df = ensure_date_and_year(df)

    if "Hire_Year" not in df.columns:
        return None

    df = df.dropna(subset=["Hire_Year"])

    if metric == "headcount":
        return df.groupby("Hire_Year")["Employee_ID"].count()

    if metric == "attrition":
        df["Attrition_Flag"] = (df["Status"] == "Resigned").astype(int)
        return (df.groupby("Hire_Year")["Attrition_Flag"].mean() * 100).round(2)

    if metric == "salary":
        return df.groupby("Hire_Year")["Salary"].mean().round(2)

    return None


# =========================================================
# CHART RENDERING
# =========================================================
def build_chart(data, metric, chart_type):
    if data is None or len(data) == 0:
        return None

    df_plot = data.reset_index()
    x_col = df_plot.columns[0]
    y_col = df_plot.columns[1]

    metric_title = metric.replace("_", " ").title()

    if chart_type.upper() == "PIE":
        return px.pie(
            df_plot,
            names=x_col,
            values=y_col,
            title=f"{metric_title} Distribution"
        )

    if chart_type.upper() == "LINE":
        fig = px.line(
            df_plot,
            x=x_col,
            y=y_col,
            title=f"{metric_title} Trend"
        )
        fig.update_traces(mode="lines+markers")
        return fig

    # Default BAR
    return px.bar(
        df_plot,
        x=x_col,
        y=y_col,
        title=f"{metric_title} by {x_col}",
        text_auto=True
    )
