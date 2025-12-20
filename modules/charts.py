import pandas as pd
import plotly.express as px


# =========================================================
# Required dataset formatting (matching your CSV columns)
# =========================================================
def ensure_date_and_year(df):
    df["Hire_Date"] = pd.to_datetime(df["Hire_Date"], errors="coerce", dayfirst=True)
    df["Hire_Year"] = df["Hire_Date"].dt.year
    return df


# =========================================================
# SINGLE METRIC GROUPED CHARTS
# =========================================================
def compute_metric(df, metric, dimension):
    df = ensure_date_and_year(df)

    # Headcount grouped
    if metric == "headcount" and dimension:
        return df.groupby(dimension)["Employee_ID"].count()

    # Salary grouped
    if metric == "salary" and dimension:
        return df.groupby(dimension)["Salary"].mean()

    # Gender grouped
    if metric == "gender" and dimension:
        return df.groupby(dimension)["Employee_ID"].count()

    return None


# =========================================================
# TREND METRIC COMPUTATION
# =========================================================
def compute_trend_metric(df, metric):
    # Normalize and extract year
    df["Hire_Date"] = pd.to_datetime(df["Hire_Date"], errors="coerce", dayfirst=True)
    df["Hire_Year"] = df["Hire_Date"].dt.year

    # Drop rows where year is missing
    df = df.dropna(subset=["Hire_Year"])

    # HEADCOUNT TREND
    if metric == "headcount":
        return df.groupby("Hire_Year")["Employee_ID"].count()

    # ATTRITION TREND
    if metric == "attrition":
        # Create numeric flag from Status
        df["Attrition_Flag"] = df["Status"].replace({"Resigned": 1, "Active": 0})

        # Force numeric
        df["Attrition_Flag"] = pd.to_numeric(df["Attrition_Flag"], errors="coerce").fillna(0)

        # Compute percentage
        trend = df.groupby("Hire_Year")["Attrition_Flag"].mean() * 100
        return trend

    # SALARY TREND
    if metric == "salary":
        return df.groupby("Hire_Year")["Salary"].mean()

    return None



# =========================================================
# CHART BUILDING
# =========================================================
def build_chart(data, metric, chart_type):
    if data is None or len(data) == 0:
        return None

    index = data.index
    values = data.values

    # 📊 Pie chart
    if chart_type == "pie":
        return px.pie(
            names=index,
            values=values,
            title=f"{metric.title()} Breakdown"
        )

    # 📉 Histogram (salary distribution)
    if chart_type == "hist":
        return px.histogram(
            x=values,
            nbins=10,
            title=f"{metric.title()} Distribution"
        )

    # 📊 Bar
    if chart_type == "bar":
        return px.bar(
            x=index,
            y=values,
            title=f"{metric.title()} by Group",
            text_auto=True
        )

    # 📈 Line (trend)
    if chart_type == "line":
        fig = px.line(
            x=index,
            y=values,
            title=f"{metric.title()} Trend by Year"
        )
        fig.update_traces(mode="lines+markers")
        return fig

    # Default → Bar
    return px.bar(x=index, y=values, title=f"{metric.title()} chart")
