import streamlit as st

from modules.analytics import load_master
from modules.llm_engine import call_llm
from modules.nlu import extract_metric, extract_dimension
from modules.charts import compute_metric, compute_trend_metric, build_chart
from modules.domain_guard import classify_domain
from modules.filter_extractor import extract_filters


# ==================================================
# FINAL ANALYTICS ROUTER (LOCKED)
# ==================================================
def process_query(query, language="en"):

    # ---------------- SESSION INIT ----------------
    if "context" not in st.session_state:
        st.session_state.context = {
            "metric": None,
            "dimension": None
        }

    df = load_master()
    q = query.lower()

    # ---------------- DOMAIN GUARD ----------------
    if classify_domain(query).get("domain") != "HR":
        return call_llm(query, language)

    # ---------------- OUTPUT PREFERENCE ----------------
    output_type = "table"   # DEFAULT
    chart_type = None

    if "chart" in q or "graph" in q:
        output_type = "chart"
        if "bar" in q:
            chart_type = "BAR"
        elif "line" in q or "trend" in q:
            chart_type = "LINE"
        elif "pie" in q:
            chart_type = "PIE"

    if any(k in q for k in ["excel", "csv", "extract", "download"]):
        output_type = "excel"

    # ---------------- METRIC EXTRACTION ----------------
    metric = extract_metric(query) or st.session_state.context.get("metric")
    dimension = extract_dimension(query) or st.session_state.context.get("dimension")
    filters = extract_filters(query)

    if not metric:
        # Non-metric HR question → LLM allowed
        return call_llm(query, language)

    # Save conversational context
    st.session_state.context.update({
        "metric": metric,
        "dimension": dimension
    })

    # ---------------- TREND (ONLY WHEN ASKED) ----------------
    if output_type == "chart" and chart_type == "LINE":
        data = compute_trend_metric(df, metric)
        if data is None:
            return "⚠ Trend analysis not available for this metric."
        fig = build_chart(data, "LINE")
        st.plotly_chart(fig, use_container_width=True)
        return None

    # ---------------- COMPUTE DATA ONCE ----------------
    data = compute_metric(
        df=df,
        metric=metric,
        dimension=dimension,
        filters=filters
    )

    if data is None or len(data) == 0:
        return "⚠ No data found for the selected criteria."

    result_df = data.reset_index()

    # ---------------- DEFAULT: TABLE ----------------
    if output_type == "table":
        st.dataframe(result_df, use_container_width=True)
        return None

    # ---------------- EXCEL / CSV ----------------
    if output_type == "excel":
        csv = result_df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            f"{metric}_by_{dimension}.csv",
            "text/csv"
        )
        return None

    # ---------------- CHART (ONLY IF TYPE GIVEN) ----------------
    if output_type == "chart":

        if not chart_type:
            return "❓ Please specify the chart type (bar, line, pie)."

        fig = build_chart(data, chart_type)
        st.plotly_chart(fig, use_container_width=True)
        return None
