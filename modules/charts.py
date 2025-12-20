import pandas as pd
import plotly.express as px

# ----------------------------
# 1. Simple Metric (No Trend)
# ----------------------------
def compute_metric(df, metric):
    if metric == "headcount":
        return df["EmployeeID"].count()

    if metric == "attrition":
        # assuming AttritionFlag: 1 = exit, 0 = stay
        return round(df["AttritionFlag"].mean() * 100, 2)

    if metric == "salary":
        return round(df["Salary"].mean(), 2)

    if metric == "gender":
        counts = df["Gender"].value_counts(normalize=True) * 100
        return counts.round(1).to_dict()

    return None


# ----------------------------------
# 2. Trend Metric (Year, Month, etc.)
# ----------------------------------
def compute_trend_metric(df, metric, dimension):
    time_col = None

    # detect time column
    for col in df.columns:
        if "year" in col.lower():
            time_col = col
            break

    if not time_col:
        return None

    if metric == "headcount":
        return df.groupby(time_col)["EmployeeID"].count()

    if metric == "attrition":
        return df.groupby(time_col)["AttritionFlag"].mean() * 100

    if metric == "salary":
        return df.groupby(time_col)["Salary"].mean()

    return None


# ----------------------------
# 3. Chart Builder
# ----------------------------
def build_chart(data, metric, chart_type, dimension=None):
    if data is None or len(data) == 0:
        return None

    if chart_type == "LINE":
        fig = px.line(x=data.index, y=data.values, title=f"{metric} trend")
        fig.update_traces(mode="lines+markers")
        return fig

    if chart_type == "PIE":
        fig = px.pie(names=list(data.keys()), values=list(data.values))
        return fig

    if chart_type == "BAR":
        fig = px.bar(x=data.index, y=data.values, title=f"{metric} comparison")
        return fig

    if chart_type == "HIST":
        fig = px.histogram(x=data, title=f"{metric} distribution histogram")
        return fig

    # Default fallback
    return px.bar(x=data.index, y=data.values, title=f"{metric} breakdown")
