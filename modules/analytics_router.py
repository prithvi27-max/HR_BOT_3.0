from modules.analytics import load_master
from modules.domain_guard import classify_domain
from modules.nlu import extract_metric, extract_dimension, extract_chart_type
from modules.charts import render_table, build_chart
from modules.llm_engine import call_llm

import pandas as pd


def process_query(query, language="en"):
    q = query.lower()

    # Load data
    df = load_master()

    # ---------------- DOMAIN GUARD ----------------
    domain_result = classify_domain(query)
    if domain_result.get("domain") != "HR":
        return "🚫 This assistant is restricted to HR-related questions only."

    # ---------------- DEFINITIONS ----------------
    if any(k in q for k in ["what is", "define", "explain", "meaning"]):
        return call_llm(query, language)

    # ---------------- METRIC EXTRACTION ----------------
    metric = extract_metric(query)
    dimension = extract_dimension(query)
    chart_type = extract_chart_type(query)

    if not metric:
        return "⚠ Please specify an HR metric like headcount or attrition."

    # ==================================================
    # HEADCOUNT LOGIC
    # ==================================================
    if metric == "headcount":

        # TOTAL HEADCOUNT
        if "total" in q and "active" not in q:
            total = df["Employee_ID"].nunique()
            return f"👥 **Total Headcount:** {total}"

        # ACTIVE HEADCOUNT
        if "active" in q:
            active = df[df["Status"] == "Active"]["Employee_ID"].nunique()
            return f"👥 **Active Headcount:** {active}"

        # HEADCOUNT BY DIMENSION
        if dimension:
            column_map = {
                "DEPARTMENT": "Department",
                "GENDER": "Gender",
                "LOCATION": "Location",
                "YEAR": "Hire_Year"
            }

            col = column_map.get(dimension)
            if col not in df.columns:
                return "⚠ Requested breakdown not available."

            if col == "Hire_Year" and "Hire_Date" in df.columns:
                df["Hire_Year"] = pd.to_datetime(df["Hire_Date"], errors="coerce").dt.year

            data = df.groupby(col)["Employee_ID"].nunique()

            if "chart" in q or "bar" in q or "pie" in q or "line" in q:
                fig = build_chart(data, chart_type)
                return fig

            return render_table(data)

    # ==================================================
    # ATTRITION LOGIC
    # ==================================================
    if metric == "attrition":
        df["_attr"] = (df["Status"] == "Resigned").astype(int)

        if dimension:
            column_map = {
                "DEPARTMENT": "Department",
                "GENDER": "Gender",
                "LOCATION": "Location",
                "YEAR": "Hire_Year"
            }

            col = column_map.get(dimension)
            if col not in df.columns:
                return "⚠ Requested breakdown not available."

            if col == "Hire_Year" and "Hire_Date" in df.columns:
                df["Hire_Year"] = pd.to_datetime(df["Hire_Date"], errors="coerce").dt.year

            data = (df.groupby(col)["_attr"].mean() * 100).round(2)

            if "chart" in q or "bar" in q or "pie" in q or "line" in q:
                fig = build_chart(data, chart_type)
                return fig

            return render_table(data)

        # OVERALL ATTRITION
        rate = round(df["_attr"].mean() * 100, 2)
        return f"📉 **Overall Attrition Rate:** {rate}%"

    return "⚠ Unable to compute this metric with available data."
