import pandas as pd
import re

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
# 🌍 UI LABELS
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
# 🔎 DYNAMIC FILTER ENGINE (NO ARCH CHANGE)
# ======================================================
def apply_dynamic_filters(df, query: str):

    q = query.lower()

    # ---- Year filter ----
    year_match = re.search(r"\b(20\d{2})\b", q)
    if year_match and "Hire_Year" in df.columns:
        year = int(year_match.group(1))
        df = df[df["Hire_Year"] == year]

    # ---- Gender filter ----
    if "male" in q:
        df = df[df["Gender"] == "M"]
    if "female" in q:
        df = df[df["Gender"] == "F"]

    # ---- Department filter ----
    if "Department" in df.columns:
        for dept in df["Department"].dropna().unique():
            if str(dept).lower() in q:
                df = df[df["Department"] == dept]

    # ---- Location filter ----
    if "Location" in df.columns:
        for loc in df["Location"].dropna().unique():
            if str(loc).lower() in q:
                df = df[df["Location"] == loc]

    return df


# ======================================================
# 🚦 MAIN ROUTER
# ======================================================
def process_query(query: str, language: str = "en"):

    # ==================================================
    # 🧠 1️⃣ DEFINITION INTENT (Highest Priority)
    # ==================================================
    definition_keywords = [
        "what is", "definition", "define",
        "explain", "meaning", "tell me about"
    ]

    if any(k in query.lower() for k in definition_keywords):
        return call_llm(
            f"""
You are an HR analytics assistant.
Explain this HR concept clearly in simple business language.

Concept:
{query}
""",
            language
        )

    # ==================================================
    # 👋 2️⃣ GREETING
    # ==================================================
    if query.lower().strip() in ["hi", "hello", "hey"]:
        return "👋 Hi! Ask me HR analytics questions."

    # ==================================================
    # 📊 3️⃣ LOAD DATA
    # ==================================================
    try:
        df = load_master()
    except Exception:
        return "⚠ Unable to load HR data."

    if df is None or df.empty:
        return "⚠ HR dataset empty."

    # ==================================================
    # 🔎 APPLY MULTI FILTERS
    # ==================================================
    df = apply_dynamic_filters(df, query)

    # ==================================================
    # 🧠 4️⃣ NLU
    # ==================================================
    normalized_query = query.lower().strip()
    metric = extract_metric(normalized_query)
    dimension = extract_dimension(normalized_query)
    chart_type = extract_chart_type(normalized_query)

    wants_chart = any(k in normalized_query for k in ["chart", "plot", "graph", "bar", "pie", "line"])
    wants_prediction = any(k in normalized_query for k in ["predict", "risk"])
    wants_model_metrics = any(k in normalized_query for k in ["auc", "precision", "recall"])

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

        if "total" in normalized_query:
            return pd.DataFrame({
                "Metric": [t("TOTAL_HEADCOUNT", language)],
                "Value": [total_headcount(df)]
            })

        if not dimension:
            return pd.DataFrame({
                "Metric": [t("ACTIVE_HEADCOUNT", language)],
                "Value": [active_headcount(df)]
            })

        col_map = {
            "DEPARTMENT": "Department",
            "LOCATION": "Location",
            "GENDER": "Gender"
        }

        if dimension == "YEAR":
            data = active_headcount_by_year(df)
        else:
            data = active_headcount_by(df, col_map.get(dimension))

        if data is None or len(data) == 0:
            return "⚠ No headcount data available for this breakdown."

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

        data = attrition_by_year(df) if dimension == "YEAR" else attrition_rate_by(df, col_map.get(dimension))

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

        if data is None or len(data) == 0:
            return "⚠ Salary data not available for this breakdown."

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

        if data is None or len(data) == 0:
            return "⚠ Engagement data not available for this breakdown."

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Engagement Score")

    # ==================================================
    # 👩‍💼 DIVERSITY
    # ==================================================
    if metric == "gender":
        data = gender_distribution(df)

        if data is None or len(data) == 0:
            return "⚠ Gender data not available."

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Count")
