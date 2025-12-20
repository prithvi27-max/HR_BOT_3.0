# modules/analytics_router.py

import streamlit as st
from modules.analytics import load_master
from modules.llm_engine import call_llm
from modules.nlu import detect_intent, extract_metric, extract_dimension, extract_chart_type
from modules.charts import compute_metric, plot_chart


def llm_explain(text, language="en"):
    prompt = f"Explain this briefly for HR: {text}. Respond in {language}"
    return call_llm(prompt, language)


def process_query(query, language="en"):
    df = load_master()
    result = detect_intent(query)
    intent = result.get("intent")

    if intent == "DEFINITION":
        return call_llm(query, language)

    if intent == "CHART":
        metric = extract_metric(query)
        dimension = extract_dimension(query)
        chart_type = extract_chart_type(query)

        if metric is None:
            return "❓ Please specify metric: headcount, salary, attrition."

        data = compute_metric(df, metric, dimension)
        if data is None:
            return "⚠ Metric not supported yet."

        fig = plot_chart(data, metric, chart_type)
        st.plotly_chart(fig)

        st.download_button(
            "📥 Download CSV",
            data.reset_index().to_csv(index=False),
            f"{metric}_chart.csv",
            "text/csv"
        )

        return f"📊 Showing {chart_type} chart for {metric}."

    if intent == "ML_PREDICT":
        return "🤖 ML prediction is coming next."

    if intent == "GENERAL":
        return call_llm(query, language)
