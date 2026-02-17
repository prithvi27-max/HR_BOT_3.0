# modules/analytics_router.py

import pandas as pd

# ===============================
# CORE ANALYTICS
# ===============================
from modules.analytics import (
    load_master,
    active_headcount,
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
# NLU
# ===============================
from modules.nlu import (
    extract_metric,
    extract_dimension,
    extract_chart_type
)

from modules.charts import build_chart
from modules.llm_engine import call_llm

# ===============================
# ML
# ===============================
from ml.predict import predict_attrition, add_risk_bucket
from ml.evaluate import load_ml_metrics


# ======================================================
# MAIN ROUTER
# ======================================================
def process_query(query: str, language: str = "en"):

    if not query or not query.strip():
        return "Please enter a valid HR analytics question."

    original_query = query.strip()

    # ==================================================
    # STEP 1: TRANSLATE FIRST (CRITICAL FIX)
    # ==================================================
    if language != "en":
        try:
            translated_query = call_llm(
                f"""
Translate the following HR analytics question into English.
Return ONLY the translated sentence.
Do NOT add explanation.

Question:
{original_query}
""",
                language="en"
            )

            q = translated_query.lower().strip()

        except Exception:
            return "⚠ Unable to process multilingual request."
    else:
        q = original_query.lower().strip()

    # ==================================================
    # STEP 2: GREETING (STRICT MATCH ONLY)
    # ==================================================
    greetings = ["hi", "hello", "hey", "hii", "hola", "hallo"]

    if q in greetings:
        return "👋 Hello! Ask me about headcount, attrition, salary, engagement, or diversity."

    # ==================================================
    # STEP 3: DEFINITION INTENT
    # ==================================================
    definition_keywords = ["what is", "definition", "define", "explain", "meaning"]

    if any(k in q for k in definition_keywords):

        response = call_llm(
            f"""
You are an HR analytics assistant.
Explain this HR concept clearly in simple business language.

Concept:
{q}
""",
            language="en"
        )

        if language != "en":
            response = call_llm(
                f"Translate this into {language}:\n\n{response}",
                language
            )

        return response

    # ==================================================
    # STEP 4: LOAD DATA
    # ==================================================
    try:
        df = load_master()
    except Exception:
        return "⚠ Unable to load HR data."

    if df is None or df.empty:
        return "⚠ HR dataset empty."

    # ==================================================
    # STEP 5: NLU EXTRACTION
    # ==================================================
    metric = extract_metric(q)
    dimension = extract_dimension(q)
    chart_type = extract_chart_type(q)

    # Support plural year automatically
    if "years" in q:
        dimension = "YEAR"

    wants_chart = any(k in q for k in ["chart", "plot", "graph", "bar", "pie", "line"])
    wants_prediction = any(k in q for k in ["predict", "prediction", "risk"])
    wants_model_metrics = any(k in q for k in ["auc", "precision", "recall"])

    # ==================================================
    # MODEL METRICS
    # ==================================================
    if wants_model_metrics:
        return load_ml_metrics()

    # ==================================================
    # PREDICTION
    # ==================================================
    if wants_prediction:

        pred_df = predict_attrition(df)
        pred_df = add_risk_bucket(pred_df)

        if wants_chart:
            return build_chart(
                pred_df["Risk_Bucket"].value_counts(),
                chart_type
            )

        return pred_df.sort_values("Attrition_Risk", ascending=False)

    # ==================================================
    # DOMAIN GUARD
    # ==================================================
    if metric is None:
        return (
            "⚠ This assistant is limited to HR analytics.\n\n"
            "Supported topics:\n"
            "- Headcount\n"
            "- Attrition\n"
            "- Salary\n"
            "- Engagement\n"
            "- Workforce diversity"
        )

    # Shared dimension mapping
    col_map = {
        "DEPARTMENT": "Department",
        "LOCATION": "Location",
        "GENDER": "Gender"
    }

    # ==================================================
    # HEADCOUNT
    # ==================================================
    if metric == "headcount":

        if not dimension:
            return pd.DataFrame({
                "Metric": ["Active Headcount"],
                "Value": [active_headcount(df)]
            })

        if dimension == "YEAR":
            data = active_headcount_by_year(df)
        else:
            data = active_headcount_by(df, col_map.get(dimension))

        if data is None or len(data) == 0:
            return "⚠ Headcount data not available."

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Headcount")

    # ==================================================
    # ATTRITION
    # ==================================================
    if metric == "attrition":

        if not dimension:
            return pd.DataFrame({
                "Metric": ["Attrition Rate (%)"],
                "Value": [attrition_rate(df)]
            })

        if dimension == "YEAR":
            data = attrition_by_year(df)
        else:
            data = attrition_rate_by(df, col_map.get(dimension))

        if data is None or len(data) == 0:
            return "⚠ Attrition data not available."

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Attrition Rate")

    # ==================================================
    # SALARY
    # ==================================================
    if metric == "salary":

        if not dimension:
            return pd.DataFrame({
                "Metric": ["Average Salary"],
                "Value": [average_salary(df)]
            })

        data = average_salary_by(df, col_map.get(dimension))

        if data is None or len(data) == 0:
            return "⚠ Salary data not available."

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Average Salary")

    # ==================================================
    # ENGAGEMENT
    # ==================================================
    if metric == "engagement":

        if not dimension:
            return pd.DataFrame({
                "Metric": ["Average Engagement Score"],
                "Value": [average_engagement(df)]
            })

        data = engagement_by(df, col_map.get(dimension))

        if data is None or len(data) == 0:
            return "⚠ Engagement data not available."

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Engagement Score")

    # ==================================================
    # DIVERSITY
    # ==================================================
    if metric == "gender":

        data = gender_distribution(df)

        if data is None or len(data) == 0:
            return "⚠ Gender distribution not available."

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Count")
