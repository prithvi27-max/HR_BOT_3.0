# modules/charts.py

import pandas as pd
import plotly.express as px

def compute_metric(df, metric, dimension=None):
    df = df.copy()

    if metric == "headcount":
        if dimension:
            data = df.groupby(dimension)["Employee_ID"].count()
        else:
            data = pd.Series({"headcount": len(df)})
        return data

    if metric == "salary":
        if dimension:
            data = df.groupby(dimension)["Salary"].mean()
        else:
            data = pd.Series({"avg_salary": df["Salary"].mean()})
        return data

    if metric == "attrition":
        df["Attr"] = (df["Status"] == "Resigned").astype(int)
        if dimension:
            data = df.groupby(dimension)["Attr"].mean() * 100
        else:
            data = pd.Series({"attrition_rate": df["Attr"].mean() * 100})
        return data

    return None


def plot_chart(data, metric, chart_type):
    df = data.reset_index()
    ycol = df.columns[1]
    xcol = df.columns[0]

    if chart_type == "pie":
        fig = px.pie(df, names=xcol, values=ycol, title=f"{metric.title()} Pie Chart")
    elif chart_type == "line":
        fig = px.line(df, x=xcol, y=ycol, markers=True, title=f"{metric.title()} Trend")
    elif chart_type == "hist":
        fig = px.histogram(df, x=ycol, title=f"{metric.title()} Distribution")
    else:
        fig = px.bar(df, x=xcol, y=ycol, text=ycol, title=f"{metric.title()} by {xcol}")

    return fig
