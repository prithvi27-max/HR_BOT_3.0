import streamlit as st

from modules.analytics import load_master
from modules.llm_engine import call_llm
from modules.nlu import detect_intent, extract_metric, extract_dimension
from modules.charts import compute_metric, compute_trend_metric, build_chart
from modules.domain_guard import classify_domain
from modules.filter_extractor import extract_filters

# =================================================
# FINAL ROUTER (NO HALLUCINATION, NO CRASH)
# =================================================
def process_query(query, language="en"):

    # -------- Session init (CRITICAL) --------
    if "context" not in st.session_state:
        st.session_state.context = {
            "metric": None,
            "dimension": None
        }

    df = load_master()

    # -------- Domain guard --------
    if classify_domain(query).get("domain") != "HR":
        return call_llm(query, language)

    # -------- Intent --------
    intent = detect_intent(query).get("intent")

    # -------- Definitions --------
    if intent == "DEFINITION":
        return call_llm(query, language)

    # -------- Charts / Analytics --------
    if intent == "CHART":

        metric = extract_metric(query) or st.session_state.context["metric"]
        dimension = extract_dimension(query) or st.session_state.context["dimension"]
        filters = extract_filters(query)

        if not metric:
            return "❓ Please specify a metric like headcount or salary."

        st.session_state.context.update({
            "metric": metric,
            "dimension": dimension
        })

        # ---- Trend ----
        if any(w in query.lower() for w in ["trend", "over time", "year"]):
            data = compute_trend_metric(df, metric)
            if data is None:
                return "⚠ Trend not available."
            fig = build_chart(data, metric, "LINE")
            st.plotly_chart(fig, use_container_width=True)
            return None

        # ---- Normal chart ----
        data = compute_metric(
            df=df,
            metric=metric,
            dimension=dimension,
            filters=filters
        )

        if data is None:
            return "⚠ Unable to compute this metric from HR data."

        fig = build_chart(data, metric, "BAR")
        st.plotly_chart(fig, use_container_width=True)
        return None

    # -------- HARD BLOCK hallucinated metrics --------
    if extract_metric(query):
        return (
            "⚠ I can only provide HR metrics based on actual data. "
            "Please refine your request."
        )

    # -------- Safe fallback --------
    return call_llm(query, language)
