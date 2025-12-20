import streamlit as st
from modules.analytics import load_master
from modules.charts import compute_metric, compute_trend_metric, build_chart
from modules.llm_engine import call_llm
from modules.nlu import extract_metric, extract_dimension, extract_chart_type, detect_intent

def process_query(query, language="en"):
    df = load_master()
    parsed = detect_intent(query)
    intent = parsed.get("intent")

    # 1. Definition
    if intent == "DEFINITION":
        return call_llm(f"Explain in HR context: {query}", language)

    # 2. Generic LLM answer
    if intent == "GENERAL":
        return call_llm(query, language)

    # 3. Metric or Chart
    if intent in ["METRIC", "CHART"]:
        metric = extract_metric(query)
        dimension = extract_dimension(query)
        chart = extract_chart_type(query)

        # TREND (LINE)
        if dimension in ["YEAR", "MONTH", "QUARTER"]:
            data = compute_trend_metric(df, metric, dimension)
            fig = build_chart(data, metric, chart, dimension)
            st.plotly_chart(fig)
            return f"📈 Showing {metric} trend by {dimension.lower()}"

        # NO DIMENSION → simple KPI
        data = compute_metric(df, metric)
        return f"🔹 {metric.upper()}: {data}"

    # 4. Forecast
    if intent == "FORECAST":
        return "🔮 Forecast ML model will be added in Phase-2"

    return "❓ I could not classify this query."
