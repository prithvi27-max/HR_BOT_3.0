# modules/analytics_router.py

import pandas as pd
from plotly.graph_objs import Figure

# ===============================
# ANALYTICS
# ===============================
from modules.analytics import (
    load_master,

    active_headcount,
    total_headcount,
    active_headcount_by,
    active_headcount_by_year,

    attrition_rate,
    attrition_rate_by,
    attrition_by_year,

    average_salary,
    average_salary_by,

    average_engagement,
    engagement_by,

    gender_distribution
)

# ===============================
# NLU + CHARTS
# ===============================
from modules.nlu import extract_metric, extract_dimension, extract_chart_type
from modules.charts import build_chart
from modules.llm_engine import call_llm

# ===============================
# ML
# ===============================
from ml.predict import predict_attrition
from ml.evaluate import load_ml_metrics
from ml.interpret import get_feature_importance
from ml.predict import add_risk_bucket


# ======================================================
# MAIN ROUTER
# ======================================================
def process_query(query: str, language: str = "en"):
    q = query.lower().strip()

    # ===============================
    # 1️⃣ GREETINGS
    # ===============================
    if q in ["hi", "hello", "hey", "hii"]:
        return (
            "👋 **Hi! I’m HR-GPT 3.0**\n\n"
            "You can ask me:\n"
            "- Total / active headcount\n"
            "- Headcount by department / year\n"
            "- Attrition rate & trends\n"
            "- Salary & engagement analysis\n"
            "- Predict employee attrition risk\n"
            "- ML model performance"
        )

    # ===============================
    # 2️⃣ LOAD DATA
    # ===============================
    try:
        df = load_master()
    except Exception as e:
        return "⚠ Unable to load HR data."

    if df is None or df.empty:
        return "⚠ HR dataset is empty."

    # ===============================
    # 3️⃣ EXTRACT INTENT SIGNALS
    # ===============================
    metric = extract_metric(query)
    dimension = extract_dimension(query)
    chart_type = extract_chart_type(query)

    wants_chart = any(k in q for k in ["chart", "plot", "graph", "bar", "pie", "line"])
    wants_definition = any(k in q for k in ["what is", "define", "explain"])
    wants_prediction = any(k in q for k in ["predict", "risk", "likely to leave"])
    wants_model_metrics = any(k in q for k in ["model performance", "auc", "precision", "recall"])
    wants_feature_importance = any(k in q for k in ["feature importance", "why attrition", "drivers"])

    # ===============================
    # 4️⃣ DEFINITIONS → LLM
    # ===============================
    if wants_definition:
        return call_llm(query, language)

    # ===============================
    # 5️⃣ HEADCOUNT
    # ===============================
    if metric == "headcount":

        if "total" in q:
            return pd.DataFrame({
                "Metric": ["Total Headcount"],
                "Value": [total_headcount(df)]
            })

        if not dimension:
            return pd.DataFrame({
                "Metric": ["Active Headcount"],
                "Value": [active_headcount(df)]
            })

        if dimension == "YEAR":
            data = active_headcount_by_year(df)
        else:
            column_map = {
                "DEPARTMENT": "Department",
                "LOCATION": "Location",
                "GENDER": "Gender"
            }
            col = column_map.get(dimension)
            data = active_headcount_by(df, col)

        if wants_chart:
            return build_chart(data, chart_type)

        return data.reset_index(name="Headcount")

    # ===============================
    # 6️⃣ ATTRITION
    # ===============================
    if metric == "attrition":

        if not dimension:
            return pd.DataFrame({
                "Metric": ["Attrition Rate (%)"],
                "Value": [attrition_rate(df)]
            })

        if dimension == "YEAR":
            data = attrition_by_year(df)
        else:
            column_map = {
                "DEPARTMENT": "Department",
                "LOCATION": "Location",
                "GENDER": "Gender"
            }
            col = column_map.get(dimension)
            data = attrition_rate_by(df, col)

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

        col = {
            "DEPARTMENT": "Department",
            "LOCATION": "Location",
            "GENDER": "Gender"
        }.get(dimension)

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

        col = {
            "DEPARTMENT": "Department",
            "LOCATION": "Location",
            "GENDER": "Gender"
        }.get(dimension)

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
    if wants_prediction:
        pred_df = predict_attrition(df)
        pred_df = add_risk_bucket(pred_df)

        return (
            pred_df
            .sort_values("Attrition_Risk", ascending=False)
            .head(20)
        )

    # ===============================
    # 1️⃣1️⃣ FEATURE IMPORTANCE
    # ===============================
    if wants_feature_importance:
        return get_feature_importance().reset_index(
            name="Importance"
        ).rename(columns={"index": "Feature"})

    # ===============================
    # 1️⃣2️⃣ MODEL PERFORMANCE
    # ===============================
    if wants_model_metrics:
        return load_ml_metrics()

    # ===============================
    # 1️⃣3️⃣ FALLBACK → LLM
    # ===============================
    return call_llm(query, language)
