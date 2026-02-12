import pandas as pd

# ===============================
# CORE ANALYTICS
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
# 🌍 UI LABEL TRANSLATIONS
# ======================================================
LABELS = {
    "en": {
        "ACTIVE_HEADCOUNT": "Active Headcount",
        "TOTAL_HEADCOUNT": "Total Headcount",
        "ATTRITION_RATE": "Attrition Rate (%)",
        "AVERAGE_SALARY": "Average Salary",
        "AVERAGE_ENGAGEMENT": "Average Engagement Score"
    }
}

def t(key, lang):
    return LABELS.get(lang, LABELS["en"]).get(key, key)


# ======================================================
# 🔒 QUERY NORMALIZER
# ======================================================
def normalize_query_to_english(query: str) -> str:

    prompt = f"""
Translate the following HR analytics question to English.

Rules:
- Use ONLY these words if applicable:
  headcount, attrition, salary, engagement, gender, department, year, location, chart
- Return ONE short sentence only

Query:
{query}
"""

    translated = call_llm(prompt, language="en")
    return translated.strip().lower()


# ======================================================
# 🚦 MAIN ROUTER
# ======================================================
def process_query(query: str, language: str = "en"):

    # ==================================================
    # 1️⃣ DEFINITION / KNOWLEDGE INTENT
    # ==================================================
    definition_keywords = [
        "what is", "definition", "define",
        "explain", "meaning", "tell me about"
    ]

    if any(k in query.lower() for k in definition_keywords):
        return call_llm(
            f"""
You are an HR analytics assistant.
Explain the following HR concept clearly.

Concept:
{query}
""",
            language
        )

    # ==================================================
    # 2️⃣ NORMALIZE QUERY
    # ==================================================
    if language != "en":
        normalized_query = normalize_query_to_english(query)
    else:
        normalized_query = query.lower().strip()

    q = normalized_query

    # ==================================================
    # 3️⃣ GREETING
    # ==================================================
    if q in ["hi", "hello", "hey"]:
        return "👋 Hi! Ask me HR analytics questions."

    # ==================================================
    # 4️⃣ LOAD DATA
    # ==================================================
    try:
        df = load_master()
    except Exception:
        return "⚠ Unable to load HR data."

    if df is None or df.empty:
        return "⚠ HR dataset empty."

    # ==================================================
    # 5️⃣ NLU EXTRACTION
    # ==================================================
    metric = extract_metric(normalized_query)
    dimension = extract_dimension(normalized_query)
    chart_type = extract_chart_type(normalized_query)

    wants_chart = any(k in q for k in ["chart", "plot", "graph", "bar", "pie", "line"])
    wants_prediction = any(k in q for k in ["predict", "risk"])
    wants_model_metrics = any(k in q for k in ["auc", "precision", "recall"])

    # ==================================================
    # 🔐 DOMAIN GUARD
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

    # ==================================================
    # 🤖 ML PREDICTION
    # ==================================================
    if wants_prediction:
        pred_df = predict_attrition(df)
        pred_df = add_risk_bucket(pred_df)

        if wants_chart:
            return build_chart(pred_df["Risk_Bucket"].value_counts(), chart_type)

        return pred_df.sort_values("Attrition_Risk", ascending=False)

    # ==================================================
    # 📉 MODEL METRICS
    # ==================================================
    if wants_model_metrics:
        return load_ml_metrics()

    # ==================================================
    # 👥 HEADCOUNT
    # ==================================================
    if metric == "headcount":

        if "total" in q:
            return pd.DataFrame({
                "Metric": [t("TOTAL_HEADCOUNT", language)],
                "Value": [total_headcount(df)]
            })

        if not dimension:
            return pd.DataFrame({
                "Metric": [t("ACTIVE_HEADCOUNT", language)],
                "Value": [active_headcount(df)]
            })

        if dimension == "YEAR":
            data = active_headcount_by_year(df)
        else:
            col_map = {
                "DEPARTMENT": "Department",
                "LOCATION": "Location",
                "GENDER": "Gender"
            }
            data = active_headcount_by(df, col_map.get(dimension))

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Headcount")

    # ==================================================
    # 🔄 ATTRITION
    # ==================================================
    if metric == "attrition":

    if not dimension:
        return pd.DataFrame({
            "Metric": [t("ATTRITION_RATE", language)],
            "Value": [attrition_rate(df)]
        })

    col_map = {
        "DEPARTMENT": "Department",
        "LOCATION": "Location",
        "GENDER": "Gender"
    }

    # ---- Get Data ----
    data = (
        attrition_by_year(df)
        if dimension == "YEAR"
        else attrition_rate_by(df, col_map.get(dimension))
    )

    # ---- SAFETY CHECK ----
    if data is None or len(data) == 0:
        return "⚠ Attrition data not available for this breakdown."

    return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Attrition Rate")

    # ==================================================
    # 💰 SALARY
    # ==================================================
    if metric == "salary":

        if not dimension:
            return pd.DataFrame({
                "Metric": [t("AVERAGE_SALARY", language)],
                "Value": [average_salary(df)]
            })

        col_map = {
            "DEPARTMENT": "Department",
            "LOCATION": "Location",
            "GENDER": "Gender"
        }

        data = average_salary_by(df, col_map.get(dimension))

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Average Salary")

    # ==================================================
    # ❤️ ENGAGEMENT
    # ==================================================
    if metric == "engagement":

        if not dimension:
            return pd.DataFrame({
                "Metric": [t("AVERAGE_ENGAGEMENT", language)],
                "Value": [average_engagement(df)]
            })

        col_map = {
            "DEPARTMENT": "Department",
            "LOCATION": "Location",
            "GENDER": "Gender"
        }

        data = engagement_by(df, col_map.get(dimension))

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Engagement Score")

    # ==================================================
    # 👩‍💼 DIVERSITY
    # ==================================================
    if metric == "gender":
        data = gender_distribution(df)
        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Count")
