# modules/analytics_router.py

import streamlit as st

# -------------------- Analytics --------------------
from modules.analytics import (
    load_master,
    active_headcount,
    total_headcount,
    active_headcount_by,
    active_headcount_by_year,
    attrition_count,
    attrition_rate,
    attrition_rate_by,
    attrition_by_year,
    average_salary,
    average_salary_by,
    average_engagement,
    engagement_by,
    gender_distribution
)

# -------------------- ML --------------------
from ml.predict import predict_attrition

# -------------------- UI --------------------
from modules.charts import build_chart, render_table

# -------------------- NLU + LLM --------------------
from modules.nlu import extract_metric, extract_dimension
from modules.llm_engine import call_llm
from modules.nlu import extract_metric, extract_dimension

# ML (will be used next step)
# from ml.predict import predict_attrition


# ==================================================
# MAIN ROUTER
# ==================================================
def process_query(query, language="en"):
    df = load_master()
    q = query.lower()

    metric = extract_metric(query)
    dimension = extract_dimension(query)

    wants_chart = any(k in q for k in ["chart", "plot", "graph"])
    chart_type = "BAR"
    if "pie" in q:
        chart_type = "PIE"
    if "line" in q or "trend" in q:
        chart_type = "LINE"

    # --------------------------------------------------
    # DEFINITIONS / CONCEPTS
    # --------------------------------------------------
    if q_type in ["DEFINITION", "EXPLANATION"]:
        return call_llm(query, language)

    # ==================================================
    # 3️⃣ ANALYTICS (DETERMINISTIC)
    # ==================================================
    data = None

    # ---------------- HEADCOUNT ----------------
    if metric == "headcount":

        if "total" in q and "active" not in q:
            data = total_headcount(df)

        elif dimension == "YEAR":
            data = active_headcount_by_year(df)

        elif dimension:
            data = active_headcount_by(df, dimension)

        else:
            data = active_headcount(df)

    # ---------------- ATTRITION ----------------
    elif metric == "attrition":

        if "rate" in q and dimension:
            data = attrition_rate_by(df, dimension)

        elif "rate" in q:
            data = attrition_rate(df)

        elif dimension == "YEAR":
            data = attrition_by_year(df)

        else:
            data = attrition_count(df)

    # ---------------- SALARY ----------------
    elif metric == "salary":
        data = average_salary_by(df, dimension) if dimension else average_salary(df)

    # ---------------- ENGAGEMENT ----------------
    elif metric == "engagement":
        data = engagement_by(df, dimension) if dimension else average_engagement(df)

    # ---------------- DIVERSITY ----------------
    elif metric == "gender":
        data = gender_distribution(df)

    # ---------------- FALLBACK ----------------
    else:
        return call_llm(query, language)

    # ==================================================
    # 4️⃣ OUTPUT HANDLING
    # ==================================================
    if data is None:
        return "⚠ Unable to compute this metric."

    # Scalar KPI
    if isinstance(data, (int, float)):
        st.metric(label=query.capitalize(), value=data)
        return None

    # Table (default)
    if not wants_chart:
        st.dataframe(render_table(data), use_container_width=True)
        return None

    # Chart (explicit)
    fig = build_chart(data, chart_type)
    st.plotly_chart(fig, use_container_width=True)
    return None
