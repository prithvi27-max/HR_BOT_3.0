import pandas as pd
from plotly.graph_objs import Figure

# ===============================
# IMPORTS THAT ACTUALLY EXIST
# ===============================
from modules.analytics import (
    load_master,

    # Headcount
    active_headcount,
    total_headcount,
    active_headcount_by,
    active_headcount_by_year,

    # Attrition
    attrition_rate,
    attrition_rate_by,
    attrition_by_year,

    # Salary
    average_salary,
    average_salary_by,

    # Engagement
    average_engagement,
    engagement_by,

    # Diversity
    gender_distribution
)

from modules.nlu import (
    extract_metric,
    extract_dimension,
    extract_chart_type
)

from modules.charts import build_chart
from modules.llm_engine import call_llm

# ML
from ml.attrition_model import predict_attrition


# ======================================================
# MAIN ROUTER
# ======================================================
def process_query(query: str, language: str = "en"):
    q = query.lower().strip()

    # ===============================
    # 1️⃣ GREETINGS
    # ===============================
    if q in ["hi", "hello", "hey", "hii", "good morning", "good evening"]:
        return (
            "👋 **Hi! I’m HR-GPT 3.0**\n\n"
            "You can ask me:\n"
            "- Total headcount\n"
            "- Active headcount\n"
            "- Headcount by department\n"
            "- Attrition rate by year\n"
            "- Salary or engagement analysis\n"
            "- Predict attrition risk"
        )

    # ===============================
    # 2️⃣ LOAD DATA
    # ===============================
    try:
        df = load_master()
    except Exception:
        return "⚠ Unable to load HR data."

    if df is None or df.empty:
        return "⚠ HR dataset is empty."

    # ===============================
    # 3️⃣ EXTRACT SIGNALS (NO detect_intent)
    # ===============================
    metric = extract_metric(query)
    dimension = extract_dimension(query)
    chart_type = extract_chart_type(query)

    wants_chart = any(k in q for k in ["chart", "plot", "graph", "bar", "pie", "line"])
    wants_definition = any(k in q for k in ["what is", "define", "explain", "meaning"])
    wants_forecast = any(k in q for k in ["predict", "forecast", "risk", "probability"])

    # ===============================
    # 4️⃣ DEFINITIONS → LLM
    # ===============================
    if wants_definition:
        return call_llm(query, language)

    # ===============================
    # 5️⃣ HEADCOUNT
    # ===============================
    if metric == "headcount":

        # TOTAL HEADCOUNT
        if "total" in q:
            return pd.DataFrame({
                "Metric": ["Total Headcount"],
                "Value": [total_headcount(df)]
            })

        # ACTIVE HEADCOUNT (DEFAULT)
        if not dimension:
            return pd.DataFrame({
                "Metric": ["Active Headcount"],
                "Value": [active_headcount(df)]
            })

        # HEADCOUNT BY YEAR
        if dimension == "YEAR":
            data = active_headcount_by_year(df)

        # HEADCOUNT BY OTHER DIMENSIONS
        else:
            column_map = {
                "DEPARTMENT": "Department",
                "LOCATION": "Location",
                "GENDER": "Gender"
            }
            col = column_map.get(dimension)
            if not col:
                return "⚠ Unsupported headcount breakdown."

            data = active_headcount_by(df, col)

        if data is None or data.empty:
            return "⚠ Unable to compute headcount."

        if wants_chart:
            return build_chart(data, chart_type)

        return data.reset_index(name="Headcount")

    # ===============================
    # 6️⃣ ATTRITION
    # ===============================
    if metric == "attrition":

        # OVERALL ATTRITION RATE
        if not dimension:
            return pd.DataFrame({
                "Metric": ["Attrition Rate (%)"],
                "Value": [attrition_rate(df)]
            })

        # ATTRITION BY YEAR
        if dimension == "YEAR":
            data = attrition_by_year(df)

        # ATTRITION BY DIMENSION
        else:
            column_map = {
                "DEPARTMENT": "Department",
                "LOCATION": "Location",
                "GENDER": "Gender"
            }
            col = column_map.get(dimension)
            if not col:
                return "⚠ Unsupported attrition breakdown."

            data = attrition_rate_by(df, col)

        if data is None or data.empty:
            return "⚠ Unable to compute attrition."

        if wants_chart:
            return build_chart(data, chart_type)

        return data.reset_index(name="Attrition Rate")

    # ===============================
    # 7️⃣ SALARY
    # ===============================
    if metric == "salary":

        if not dimension:
            return pd.DataFrame({
                "Metric": ["Average Salary"],
                "Value": [average_salary(df)]
            })

        column_map = {
            "DEPARTMENT": "Department",
            "LOCATION": "Location",
            "GENDER": "Gender"
        }
        col = column_map.get(dimension)
        if not col:
            return "⚠ Unsupported salary breakdown."

        data = average_salary_by(df, col)

        if wants_chart:
            return build_chart(data, chart_type)

        return data.reset_index(name="Average Salary")

    # ===============================
    # 8️⃣ ENGAGEMENT
    # ===============================
    if metric == "engagement":

        if not dimension:
            return pd.DataFrame({
                "Metric": ["Average Engagement Score"],
                "Value": [average_engagement(df)]
            })

        column_map = {
            "DEPARTMENT": "Department",
            "LOCATION": "Location",
            "GENDER": "Gender"
        }
        col = column_map.get(dimension)
        if not col:
            return "⚠ Unsupported engagement breakdown."

        data = engagement_by(df, col)

        if wants_chart:
            return build_chart(data, chart_type)

        return data.reset_index(name="Engagement Score")

    # ===============================
    # 9️⃣ DIVERSITY
    # ===============================
    if metric == "gender":
        data = gender_distribution(df)

        if wants_chart:
            return build_chart(data, chart_type)

        return data.reset_index(name="Count")

    # ===============================
    # 🔟 ML ATTRITION PREDICTION
    # ===============================
    if wants_forecast:
        try:
            pred_df = predict_attrition(df)
            return (
                pred_df
                .sort_values("Attrition_Risk", ascending=False)
                .head(20)
            )
        except Exception:
            return "⚠ Unable to run attrition prediction model."

    # ===============================
    # 1️⃣1️⃣ FALLBACK → LLM
    # ===============================
    return call_llm(query, language)
