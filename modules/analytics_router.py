# modules/analytics_router.py

import streamlit as st
import numpy as np
import pandas as pd
from modules.analytics import load_master
from modules.llm_engine import call_llm
from modules.nlu import detect_intent
from modules.charts import create_visual

# ---------------------
# LLM EXPLANATION WRAPPER
# ---------------------
def llm_explain(metric_name, value, language="en"):
    prompt = f"""
    You are an HR analytics expert.
    Convert this number into:
    • One short insight
    • One short recommendation
    No long paragraphs. 
    Respond in {language}.
    
    Metric: {metric_name}
    Value: {value}
    """
    return call_llm(prompt, language)


# ---------------------
# MAIN QUERY PROCESSOR
# ---------------------
def process_query(query, language="en"):
    df = load_master()
    intent = detect_intent(query)

    # --------------------
    # BASIC METRICS
    # --------------------
    if intent == "HEADCOUNT":
        value = len(df)
        return llm_explain("Total Active Employees", value, language)

    if intent == "ATTRITION":
        if "Attrition" not in df.columns:
            return "⚠ Attrition column missing."
        value = round(df["Attrition"].mean() * 100, 2)
        return llm_explain("Attrition Rate (%)", value, language)

    if intent == "SALARY":
        if "Salary" not in df.columns:
            return "⚠ Salary column missing."
        value = round(df["Salary"].mean(), 2)
        return llm_explain("Average Salary", value, language)

    if intent == "GENDER":
        gender_counts = df["Gender"].value_counts().to_dict()
        return llm_explain("Gender Distribution", gender_counts, language)

    if intent == "ENGAGEMENT":
        if "EngagementScore" not in df.columns:
            return "⚠ Engagement score column missing."
        value = round(df["EngagementScore"].mean(), 2)
        return llm_explain("Employee Engagement Score", value, language)

    # --------------------
    # TRENDS
    # --------------------
    if intent == "HEADCOUNT_TREND":
        if "Year" not in df.columns:
            return "⚠ No Year column in dataset."
        trend = df.groupby("Year")["EmployeeID"].count().reset_index()
        fig = create_visual(trend, x="Year", y="EmployeeID", chart_type="line")
        st.plotly_chart(fig)
        return "📈 Displaying headcount trend by year."

    if intent == "ATTRITION_TREND":
        if "Year" not in df.columns or "Attrition" not in df.columns:
            return "⚠ Required Year/Attrition columns missing."
        trend = df.groupby("Year")["Attrition"].mean().reset_index()
        trend["Attrition"] = trend["Attrition"] * 100
        fig = create_visual(trend, x="Year", y="Attrition", chart_type="line")
        st.plotly_chart(fig)
        return "📉 Attrition trend over time."

    if intent == "SALARY_TREND":
        if "Year" not in df.columns or "Salary" not in df.columns:
            return "⚠ Missing Salary/Year columns."
        trend = df.groupby("Year")["Salary"].mean().reset_index()
        fig = create_visual(trend, x="Year", y="Salary", chart_type="line")
        st.plotly_chart(fig)
        return "📈 Salary trend by year."

    # --------------------
    # STATISTICS
    # --------------------
    if intent == "STATS_MEAN":
        return np.mean(df["Salary"])

    if intent == "STATS_MEDIAN":
        return np.median(df["Salary"])

    if intent == "STATS_MODE":
        return float(df["Salary"].mode()[0])

    if intent == "STATS_STD":
        return float(df["Salary"].std())

    if intent == "STATS_PERCENTILE":
        return {
            "p90_salary": float(np.percentile(df["Salary"], 90)),
            "p75_salary": float(np.percentile(df["Salary"], 75)),
            "p50_salary": float(np.percentile(df["Salary"], 50))
        }

    # --------------------
    # CHARTS (GENERIC)
    # --------------------
    if intent == "CHART":
        st.write("📊 Please specify metric and type. Examples:")
        st.write("- headcount bar chart by department")
        st.write("- salary boxplot by job role")
        st.write("- attrition pie by gender")
        st.write("- hiring trend line")
        return

    # --------------------
    # PLACEHOLDER FOR ML
    # --------------------
    if intent == "PREDICT_ATTRITION":
        return "🤖 Attrition ML model coming soon."

    # --------------------
    # FALLBACK — PURE LLM
    # --------------------
    fallback = f"You are an HR assistant. Respond short.\nUser said: {query}\nLanguage: {language}"
    return call_llm(fallback, language)
