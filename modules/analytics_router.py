import streamlit as st

from modules.analytics import (
    load_master,
    total_headcount,
    headcount_by_dimension,
    headcount_by_year_snapshot,
    attrition_count_by_dimension,
    attrition_count_by_year,
    avg_salary_by_dimension,
    avg_engagement_by_dimension,
)

from modules.charts import build_chart, render_table
from modules.question_pool import classify_question
from modules.llm_engine import call_llm
from modules.nlu import extract_metric, extract_dimension

# ML (will be used next step)
# from ml.predict import predict_attrition


# ==================================================
# MAIN ROUTER
# ==================================================
def process_query(query, language="en"):

    # ---------------- Load data ----------------
    df = load_master()
    q = query.lower()

    # ---------------- Question type ----------------
    question_type = classify_question(query)

    # ==================================================
    # 1️⃣ DEFINITIONS (LLM ONLY)
    # ==================================================
    if question_type == "DEFINITION":
        return call_llm(query, language)

    # ==================================================
    # 2️⃣ EXPLANATION / WHY (LLM ONLY)
    # ==================================================
    if question_type == "EXPLANATION":
        return call_llm(
            f"""
You are an HR expert.
Explain using HR concepts and best practices.
Do NOT fabricate numbers or metrics.

Question:
{query}
""",
            language
        )

    # ==================================================
    # 3️⃣ METRICS / ANALYTICS
    # ==================================================
    metric = extract_metric(query)
    dimension = extract_dimension(query)

    if not metric:
        return call_llm(query, language)

    # ---------------- Output preference ----------------
    wants_chart = any(k in q for k in ["chart", "graph", "plot"])
    chart_type = None

    if wants_chart:
        if "line" in q or "trend" in q:
            chart_type = "LINE"
        elif "pie" in q:
            chart_type = "PIE"
        else:
            chart_type = "BAR"

    # ==================================================
    # METRIC DISPATCH
    # ==================================================
    data = None

    # -------- HEADCOUNT --------
    if metric == "headcount":
        if not dimension:
            data = total_headcount(df)
        elif dimension == "YEAR":
            data = headcount_by_year_snapshot(df)
        else:
            data = headcount_by_dimension(df, dimension)

    # -------- ATTRITION --------
    elif metric == "attrition":
        if dimension == "YEAR":
            data = attrition_count_by_year(df)
        else:
            data = attrition_count_by_dimension(df, dimension)

    # -------- SALARY --------
    elif metric == "salary":
        data = avg_salary_by_dimension(df, dimension)

    # -------- ENGAGEMENT --------
    elif metric == "engagement":
        data = avg_engagement_by_dimension(df, dimension)

    if data is None:
        return "⚠ Unable to compute this metric with available data."

    # ==================================================
    # OUTPUT
    # ==================================================
    if isinstance(data, (int, float)):
        st.metric(
            label=f"Total {metric.replace('_', ' ').title()}",
            value=int(data)
        )
        return None

    # Table (default)
    if not wants_chart:
        st.dataframe(render_table(data), use_container_width=True)
        return None

    # Chart (only if requested)
    fig = build_chart(data, chart_type)
    st.plotly_chart(fig, use_container_width=True)
    return None
