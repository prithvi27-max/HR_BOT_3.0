# modules/analytics_router.py

import streamlit as st

from modules.analytics import *
from modules.charts import build_chart, render_table
from modules.nlu import extract_metric, extract_dimension
from modules.question_pool import classify_question
from modules.llm_engine import call_llm
from modules.nlu import extract_metric, extract_dimension
from modules.filter_extractor import extract_filters

# ML (will be used next step)
# from ml.predict import predict_attrition


def process_query(query, language="en"):
    df = load_master()
    q = query.lower()

    # --------------------------------------------------
    # QUESTION TYPE
    # --------------------------------------------------
    q_type = classify_question(query)
    metric = extract_metric(query)
    dimension = extract_dimension(query)
    filters = extract_filters(query)

    if not metric:
        return call_llm(query, language)

    # --------------------------------------------------
    # HEADCOUNT
    # --------------------------------------------------
    if metric == "headcount":

        if "total" in q and "active" not in q:
            data = total_headcount(df)
        elif dimension == "YEAR":
            data = active_headcount_by_year(df)
        elif dimension:
            data = active_headcount_by(df, dimension)
        else:
            data = active_headcount(df)

    # --------------------------------------------------
    # ATTRITION
    # --------------------------------------------------
    elif metric == "attrition":

        if "rate" in q and dimension:
            data = attrition_rate_by(df, dimension)
        elif "rate" in q:
            data = attrition_rate(df)
        elif dimension == "YEAR":
            data = attrition_by_year(df)
        else:
            data = attrition_count(df)

    # --------------------------------------------------
    # SALARY
    # --------------------------------------------------
    elif metric == "salary":
        data = average_salary_by(df, dimension) if dimension else average_salary(df)

    # --------------------------------------------------
    # ENGAGEMENT
    # --------------------------------------------------
    elif metric == "engagement":
        data = engagement_by(df, dimension) if dimension else average_engagement(df)

    # --------------------------------------------------
    # DIVERSITY
    # --------------------------------------------------
    elif metric == "gender":
        data = gender_distribution(df)

    else:
        return call_llm(query, language)

    if data is None:
        return "⚠ Unable to compute this metric."

    # --------------------------------------------------
    # OUTPUT
    # --------------------------------------------------
    if isinstance(data, (int, float)):
        st.metric(label=query.capitalize(), value=data)
        return None

    if not wants_chart:
        st.dataframe(render_table(data), use_container_width=True)
        return None

    fig = build_chart(data, chart_type)
    st.plotly_chart(fig, use_container_width=True)
    return None
