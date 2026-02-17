# modules/analytics_router.py

import pandas as pd
import json
import logging
from functools import lru_cache

# ===============================
# LOGGING CONFIG
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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
# FALLBACK NLU
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
# DATASET CACHING
# ======================================================
@lru_cache(maxsize=1)
def get_cached_dataset():
    return load_master()


# ======================================================
# INTENT CACHING
# ======================================================
@lru_cache(maxsize=100)
def classify_intent_llm_cached(query: str):

    prompt = f"""
You are an HR analytics intent classifier.

Supported metrics:
- headcount
- attrition
- salary
- engagement
- gender

Supported dimensions:
- YEAR
- DEPARTMENT
- LOCATION
- GENDER
- NONE

Supported chart types:
- BAR
- LINE
- PIE
- NONE

Return ONLY valid JSON in this format:

{{
  "metric": "...",
  "dimension": "...",
  "chart": "...",
  "confidence": 0.0
}}

Confidence must be between 0 and 1.

If not HR-related:
{{
  "metric": null,
  "dimension": null,
  "chart": "NONE",
  "confidence": 0.0
}}

Question:
{query}
"""

    try:
        response = call_llm(prompt, language="en")
        response = response.strip()
        response = response.replace("```json", "").replace("```", "")
        parsed = json.loads(response)

        logging.info(f"LLM intent: {parsed}")

        return parsed

    except Exception as e:
        logging.error(f"LLM intent classification failed: {e}")
        return None


# ======================================================
# MAIN ROUTER
# ======================================================
def process_query(query: str, language: str = "en"):

    if not query or not query.strip():
        return "Please enter a valid HR analytics question."

    original_query = query.strip()

    # ==================================================
    # TRANSLATION
    # ==================================================
    if language != "en":
        try:
            translated_query = call_llm(
                f"""
Translate the following HR analytics question into English.
Return ONLY the translated sentence.

Question:
{original_query}
""",
                language="en"
            )
            q = translated_query.lower().strip()
            logging.info(f"Translated query: {q}")
        except Exception as e:
            logging.error(f"Translation failed: {e}")
            return "⚠ Unable to process multilingual request."
    else:
        q = original_query.lower().strip()

    # ==================================================
    # GREETING
    # ==================================================
    if q in ["hi", "hello", "hey", "hola", "hallo"]:
        return "👋 Hello! Ask me about headcount, attrition, salary, engagement, or diversity."

    # ==================================================
    # DEFINITION
    # ==================================================
    if any(k in q for k in ["what is", "define", "explain", "meaning"]):
        return call_llm(
            f"Explain this HR concept clearly:\n\n{q}",
            language="en"
        )

    # ==================================================
    # LOAD DATA (CACHED)
    # ==================================================
    try:
        df = get_cached_dataset()
    except Exception as e:
        logging.error(f"Dataset load failed: {e}")
        return "⚠ Unable to load HR data."

    if df is None or df.empty:
        return "⚠ HR dataset empty."

    # ==================================================
    # LLM INTENT CLASSIFICATION
    # ==================================================
    intent = classify_intent_llm_cached(q)

    metric = None
    dimension = None
    chart_type = "NONE"
    confidence = 0.0

    if intent:
        metric = intent.get("metric")
        dimension = intent.get("dimension")
        chart_type = intent.get("chart")
        confidence = intent.get("confidence", 0.0)

    # ==================================================
    # CONFIDENCE THRESHOLD
    # ==================================================
    if confidence < 0.6:
        logging.info("Low confidence → fallback to rule-based NLU")
        metric = extract_metric(q)
        dimension = extract_dimension(q)
        chart_type = extract_chart_type(q)

    wants_chart = chart_type in ["BAR", "LINE", "PIE"]

    # ==================================================
    # MODEL METRICS
    # ==================================================
    if any(k in q for k in ["auc", "precision", "recall"]):
        return load_ml_metrics()

    # ==================================================
    # PREDICTION
    # ==================================================
    if any(k in q for k in ["predict", "risk"]):
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
    if not metric:
        return (
            "⚠ This assistant is limited to HR analytics.\n\n"
            "Supported topics:\n"
            "- Headcount\n"
            "- Attrition\n"
            "- Salary\n"
            "- Engagement\n"
            "- Workforce diversity"
        )

    col_map = {
        "DEPARTMENT": "Department",
        "LOCATION": "Location",
        "GENDER": "Gender"
    }

    # ==================================================
    # HEADCOUNT
    # ==================================================
    if metric == "headcount":

        if not dimension or dimension == "NONE":
            return pd.DataFrame({
                "Metric": ["Active Headcount"],
                "Value": [active_headcount(df)]
            })

        if dimension == "YEAR":
            data = active_headcount_by_year(df)
        else:
            data = active_headcount_by(df, col_map.get(dimension))

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Headcount")

    # ==================================================
    # ATTRITION
    # ==================================================
    if metric == "attrition":

        if not dimension or dimension == "NONE":
            return pd.DataFrame({
                "Metric": ["Attrition Rate (%)"],
                "Value": [attrition_rate(df)]
            })

        if dimension == "YEAR":
            data = attrition_by_year(df)
        else:
            data = attrition_rate_by(df, col_map.get(dimension))

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Attrition Rate")

    # ==================================================
    # SALARY
    # ==================================================
    if metric == "salary":

        if not dimension or dimension == "NONE":
            return pd.DataFrame({
                "Metric": ["Average Salary"],
                "Value": [average_salary(df)]
            })

        data = average_salary_by(df, col_map.get(dimension))

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Average Salary")

    # ==================================================
    # ENGAGEMENT
    # ==================================================
    if metric == "engagement":

        if not dimension or dimension == "NONE":
            return pd.DataFrame({
                "Metric": ["Average Engagement Score"],
                "Value": [average_engagement(df)]
            })

        data = engagement_by(df, col_map.get(dimension))

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Engagement Score")

    # ==================================================
    # GENDER
    # ==================================================
    if metric == "gender":

        data = gender_distribution(df)

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Count")
