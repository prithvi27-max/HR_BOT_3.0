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


# -------------------------------------------------
# LLM Explanation Helper
# -------------------------------------------------
def llm_explain(text, language="en"):
    prompt = f"""
    You are an HR analytics expert.

    Explain the following insight briefly for HR leaders
    in ONE short paragraph.

    Insight:
    {text}

    Respond in {language}.
    """
    return call_llm(prompt, language)


# -------------------------------------------------
# MAIN ROUTER
# -------------------------------------------------
def process_query(query, language="en"):
    df = load_master()

    # -------------------------------------------------
    # 1️⃣ DOMAIN GUARD (LLM-based, SAFE)
    # -------------------------------------------------
    domain_result = classify_domain(query)

    if not domain_result or not isinstance(domain_result, dict):
        domain = "UNKNOWN"
    else:
        domain = domain_result.get("domain", "UNKNOWN")

    if domain != "HR":
        return "🚫 This assistant is restricted to HR-related questions only."

    # -------------------------------------------------
    # 2️⃣ INTENT DETECTION
    # -------------------------------------------------
    intent_result = detect_intent(query)

    if not intent_result or not isinstance(intent_result, dict):
        intent = "GENERAL"
    else:
        intent = intent_result.get("intent", "GENERAL")

    # -------------------------------------------------
    # 3️⃣ DEFINITIONS (Pure LLM)
    # -------------------------------------------------
    if intent == "DEFINITION":
        return call_llm(query, language)

    # -------------------------------------------------
    # 4️⃣ CHART REQUESTS
    # -------------------------------------------------
    if intent == "CHART":
        metric = extract_metric(query)
        dimension = extract_dimension(query)
        chart_type = extract_chart_type(query)

        if metric is None:
            return "❓ Please specify a metric like headcount, attrition, salary, or gender."

        # ---- TREND CHART ----
        if any(k in query.lower() for k in ["trend", "over time", "by year", "yearly"]):
            data = compute_trend_metric(df, metric)

            if data is None:
                return "⚠ Trend analysis is not available for this metric yet."

            fig = build_chart(data, metric, "LINE")
            st.plotly_chart(fig, use_container_width=True)

            st.download_button(
                "📥 Download Trend CSV",
                data.reset_index().to_csv(index=False),
                f"{metric}_trend.csv",
                "text/csv"
            )
            return None

        # ---- NORMAL BREAKDOWN CHART ----
        data = compute_metric(df, metric, dimension)

        if data is None:
            return "⚠ No breakdown available. Try: headcount by department or salary by location."

        fig = build_chart(data, metric, chart_type)
        st.plotly_chart(fig, use_container_width=True)

        st.download_button(
            "📥 Download CSV",
            data.reset_index().to_csv(index=False),
            f"{metric}_chart.csv",
            "text/csv"
        )
        return None

    # -------------------------------------------------
    # 5️⃣ ML PREDICTION PLACEHOLDER
    # -------------------------------------------------
    if intent == "ML_PREDICT":
        return "🤖 Attrition risk prediction is enabled. Please select an employee or department."

    # -------------------------------------------------
    # 6️⃣ FALLBACK (LLM, HR-ONLY)
    # -------------------------------------------------
    safe_prompt = f"""
    You are an HR analytics assistant.
    Answer ONLY using HR concepts and workforce analytics.
    If the question is unrelated to HR, politely refuse.

    Question:
    {query}

    Respond in {language}.
    """
    return call_llm(safe_prompt, language)
