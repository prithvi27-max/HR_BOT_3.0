import streamlit as st
import pandas as pd
from plotly.graph_objs import Figure

# ===============================
# INTERNAL IMPORTS (SAFE ONLY)
# ===============================
from modules.analytics import (
    load_master,
    headcount,
    attrition_rate,
    yearly_headcount,
    yearly_attrition,
    group_count
)

from modules.charts import build_chart, render_table
from modules.nlu import (
    detect_intent,
    extract_metric,
    extract_dimension,
    extract_chart_type
)

from modules.llm_engine import call_llm

# ML
from ml.attrition_model import predict_attrition


# ======================================================
# MAIN ROUTER
# ======================================================
def process_query(query: str, language: str = "en"):
    query_l = query.lower().strip()

    # ===============================
    # 1️⃣ GREETINGS (UX FIX)
    # ===============================
    if query_l in ["hi", "hello", "hey", "hii", "good morning", "good evening"]:
        return (
            "👋 **Hi! I’m HR-GPT 3.0**\n\n"
            "You can ask me things like:\n"
            "- Total headcount\n"
            "- Headcount by department\n"
            "- Attrition rate by year\n"
            "- Salary analysis\n"
            "- HR definitions (e.g. *What is attrition?*)"
        )

    # ===============================
    # 2️⃣ LOAD DATA
    # ===============================
    try:
        df = load_master()
    except Exception as e:
        return "⚠ Unable to load HR data."

    if df is None or len(df) == 0:
        return "⚠ HR dataset is empty."

    # ===============================
    # 3️⃣ INTENT DETECTION
    # ===============================
    intent_info = detect_intent(query)
    intent = intent_info.get("intent")

    metric = extract_metric(query)
    dimension = extract_dimension(query)
    chart_type = extract_chart_type(query)

    wants_chart = intent == "CHART"
    wants_forecast = intent == "FORECAST"
    wants_definition = intent == "DEFINITION"

    # ===============================
    # 4️⃣ DEFINITIONS → LLM
    # ===============================
    if wants_definition:
        return call_llm(query, language)

    # ===============================
    # 5️⃣ TOTAL HEADCOUNT
    # ===============================
    if metric == "headcount" and not dimension:
        total = headcount(df)
        table = pd.DataFrame({
            "Metric": ["Total Active Headcount"],
            "Value": [total]
        })
        st.dataframe(table, use_container_width=True)
        return None

    # ===============================
    # 6️⃣ GROUPED HEADCOUNT
    # ===============================
    if metric == "headcount" and dimension:
        data = group_count(df, dimension)

        if data is None:
            return "⚠ Unable to compute headcount for this dimension."

        if wants_chart:
            fig = build_chart(data, chart_type)
            return fig

        st.dataframe(render_table(data), use_container_width=True)
        return None

    # ===============================
    # 7️⃣ ATTRITION RATE
    # ===============================
    if metric == "attrition" and not dimension:
        rate = attrition_rate(df)
        table = pd.DataFrame({
            "Metric": ["Overall Attrition Rate (%)"],
            "Value": [rate]
        })
        st.dataframe(table, use_container_width=True)
        return None

    # ===============================
    # 8️⃣ ATTRITION BY YEAR
    # ===============================
    if metric == "attrition" and dimension == "YEAR":
        data = yearly_attrition(df)

        if wants_chart:
            fig = build_chart(data, chart_type)
            return fig

        st.dataframe(render_table(data), use_container_width=True)
        return None

    # ===============================
    # 9️⃣ HEADCOUNT BY YEAR
    # ===============================
    if metric == "headcount" and dimension == "YEAR":
        data = yearly_headcount(df)

        if wants_chart:
            fig = build_chart(data, chart_type)
            return fig

        st.dataframe(render_table(data), use_container_width=True)
        return None

    # ===============================
    # 🔟 ML ATTRITION PREDICTION
    # ===============================
    if wants_forecast or "predict attrition" in query_l:
        try:
            pred_df = predict_attrition(df)
            st.dataframe(pred_df.head(20), use_container_width=True)
            return (
                "🤖 **Attrition Risk Prediction Generated**\n\n"
                "Showing top employees with predicted attrition risk."
            )
        except Exception as e:
            return "⚠ Unable to run attrition prediction model."

    # ===============================
    # 1️⃣1️⃣ FALLBACK → LLM
    # ===============================
    return call_llm(query, language)
