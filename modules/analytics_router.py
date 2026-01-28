import streamlit as st

from modules.analytics import load_master
from modules.llm_engine import call_llm

from modules.nlu import (
    detect_intent,
    extract_metric,
    extract_dimension,
    extract_chart_type
)

from modules.charts import (
    compute_metric,
    compute_trend_metric,
    build_chart
)

from modules.domain_guard import classify_domain

# 🆕 Advanced analytics helpers
from modules.filter_extractor import extract_filters
from modules.time_extractor import extract_time_window
from modules.comparison_extractor import extract_comparison
from modules.chart_selector import auto_chart


# ==================================================
# SESSION CONTEXT INITIALIZATION
# ==================================================
if "context" not in st.session_state:
    st.session_state.context = {
        "metric": None,
        "dimension": None,
        "intent": None
    }


# ==================================================
# MAIN ROUTER
# ==================================================
def process_query(query, language="en"):

    # ---------------- LOAD DATA ----------------
    df = load_master()

    # ---------------- DOMAIN ROUTING ----------------
    domain_result = classify_domain(query)
    domain = domain_result.get("domain", "HR")

    # If not HR → behave like ChatGPT (text only)
    if domain != "HR":
        return call_llm(query, language)

    # ---------------- INTENT ----------------
    intent_result = detect_intent(query)
    intent = intent_result.get("intent", "GENERAL")

    st.session_state.context["intent"] = intent

    # ---------------- DEFINITIONS ----------------
    if intent == "DEFINITION":
        return call_llm(query, language)

    # ---------------- HR ANALYTICS / CHARTS ----------------
    if intent == "CHART":

        # -------- Core NLU extraction --------
        metric = extract_metric(query) or st.session_state.context.get("metric")
        dimension = extract_dimension(query) or st.session_state.context.get("dimension")

        if not metric:
            return "❓ Please specify a metric like headcount, attrition, salary, or gender."

        # -------- Advanced HR logic --------
        filters = extract_filters(query)              # Region, Gender, Dept, etc.
        time_window = extract_time_window(query)      # last year, last 3 years
        comparison = extract_comparison(query)        # A vs B (future use)

        # -------- Persist conversational memory --------
        st.session_state.context.update({
            "metric": metric,
            "dimension": dimension
        })

        # ---------------- TREND ANALYSIS ----------------
        if any(k in query.lower() for k in [
            "trend", "over time", "year", "yearly", "monthly"
        ]):

            data = compute_trend_metric(df, metric)

            if data is None or len(data) == 0:
                return "⚠ Trend analysis is not available for this metric."

            fig = build_chart(data, metric, "LINE")
            st.plotly_chart(fig, use_container_width=True)
            return None

        # ---------------- STANDARD / FILTERED ANALYSIS ----------------
        data = compute_metric(
            df=df,
            metric=metric,
            dimension=dimension,
            filters=filters
        )

        if data is None or len(data) == 0:
            return "⚠ No data found for the selected criteria."

        chart_type = auto_chart(metric, dimension)
        fig = build_chart(data, metric, chart_type)
        st.plotly_chart(fig, use_container_width=True)
        return None

    # ---------------- ML PREDICTION ----------------
    if intent == "ML_PREDICT":
        return "🤖 Attrition risk prediction is enabled. Please select an employee or department."

    # ---------------- FALLBACK (SAFE HR LLM) ----------------
    safe_prompt = f"""
You are an HR analytics assistant.
Answer ONLY using HR concepts and workforce analytics.
If the question is unrelated to HR, politely refuse.

Question:
{query}

Respond in {language}.
"""
    return call_llm(safe_prompt, language)
