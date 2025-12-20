import streamlit as st
from modules.analytics import load_master
from modules.llm_engine import call_llm
from modules.nlu import detect_intent, extract_metric, extract_dimension, extract_chart_type
from modules.charts import compute_metric, compute_trend_metric, build_chart


def llm_explain(text, language="en"):
    prompt = f"Explain briefly for HR leaders: {text}. Respond in {language}."
    return call_llm(prompt, language)


def process_query(query, language="en"):
    df = load_master()
    result = detect_intent(query)
    intent = result.get("intent")

    # 🤖 Generic LLM definition queries
    if intent == "DEFINITION":
        return call_llm(query, language)

    # 📊 CHART REQUEST
    if intent == "CHART":
        metric = extract_metric(query)
        dimension = extract_dimension(query)
        chart_type = extract_chart_type(query)

        if metric is None:
            return "❓ Please mention metric (headcount, salary, attrition, gender)."

        # TREND request
        if "trend" in query or "over years" in query or "by year" in query:
            data = compute_trend_metric(df, metric)
            if data is None:
                return "⚠ Trend metric not supported yet."

            fig = build_chart(data, metric, "line")
            st.plotly_chart(fig)

            st.download_button(
                "📥 Download Trend CSV",
                data.reset_index().to_csv(index=False),
                f"{metric}_trend.csv",
                "text/csv"
            )
            return None

        # Normal breakdown chart
        data = compute_metric(df, metric, dimension)
        if data is None:
            return "⚠ No breakdown available. Try: headcount by department / salary by location"

        fig = build_chart(data, metric, chart_type)
        st.plotly_chart(fig)

        st.download_button(
            "📥 Download CSV",
            data.reset_index().to_csv(index=False),
            f"{metric}_chart.csv",
            "text/csv"
        )

        return None

    # Fallback to LLM
    return call_llm(query, language)
