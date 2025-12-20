import pandas as pd
import plotly.express as px

# --------------------------------
# 1. SIMPLE METRIC CALCULATIONS
# --------------------------------
def compute_metric(df, metric):
    if metric == "headcount":
        return df["Employee_ID"].count()

    if metric == "attrition":
        # assumes AttritionFlag or Attrition column exists
        if "AttritionFlag" in df.columns:
            return round(df["AttritionFlag"].mean() * 100, 2)
        if "Attrition" in df.columns:
            # yes/no to numeric
            return round(df["Attrition"].replace({"Yes":1,"No":0}).mean() * 100, 2)

    if metric == "salary":
        # detect any salary-like column
        sal_col = next((c for c in df.columns if "salary" in c.lower() or "comp" in c.lower()), None)
        if sal_col:
            return round(df[sal_col].mean(), 2)

    if metric == "gender":
        return df["Gender"].value_counts(normalize=True).round(2).to_dict()

    return None


# -------------------------------------
# 2. TREND METRICS (YEAR / MONTH / QUARTER)
# -------------------------------------
def compute_trend_metric(df, metric, dimension):
    # 1. Find a usable Year column
    time_col = None
    for col in df.columns:
        if "year" in col.lower():
            time_col = col
            break

    # 2. If no year exists, try extracting from a date
    if not time_col:
        # search any date column
        date_col = next((c for c in df.columns if "date" in c.lower()), None)
        if date_col:
            df["Year"] = pd.to_datetime(df[date_col], errors="coerce").dt.year
            time_col = "Year"

    # if still nothing, abort
    if not time_col:
        return None  

    # 3. Calculate trend
    if metric == "headcount":
        return df.groupby(time_col)["Employee_ID"].count()

    if metric == "attrition":
        if "AttritionFlag" in df.columns:
            return df.groupby(time_col)["AttritionFlag"].mean() * 100
        if "Attrition" in df.columns:
            return df.groupby(time_col)["Attrition"].replace({"Yes":1,"No":0}).mean() * 100

    if metric == "salary":
        sal_col = next((c for c in df.columns if "salary" in c.lower() or "comp" in c.lower()), None)
        return df.groupby(time_col)[sal_col].mean()

    return None


# ----------------------------
# 3. UNIVERSAL CHART BUILDER
# ----------------------------
def build_chart(data, metric, chart_type, dimension=None):
    if data is None:
        return None

    # convert Series to DataFrame
    if not hasattr(data, "index"):
        return None

    # LINE CHART
    if chart_type == "LINE":
        fig = px.line(
            x=data.index, 
            y=data.values, 
            title=f"{metric.title()} trend over {dimension.lower()}"
        )
        fig.update_traces(mode="lines+markers")
        return fig

    # PIE CHART
    if chart_type == "PIE":
        fig = px.pie(
            names=data.index,
            values=data.values,
            title=f"{metric.title()} ratio"
        )
        return fig

    # BAR CHART
    if chart_type == "BAR":
        fig = px.bar(
            x=data.index, 
            y=data.values, 
            title=f"{metric.title()} comparison by {dimension}"
        )
        return fig

    # HISTOGRAM
    if chart_type == "HIST":
        fig = px.histogram(
            x=data,
            title=f"{metric.title()} distribution histogram"
        )
        return fig

    # DEFAULT
    return px.bar(x=data.index, y=data.values)
