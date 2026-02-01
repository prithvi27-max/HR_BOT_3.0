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
# NLU (EXISTING ONLY)
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
# 🌍 UI LABEL TRANSLATIONS (DISPLAY ONLY)
# ======================================================
LABELS = {
    "en": {
        "ACTIVE_HEADCOUNT": "Active Headcount",
        "TOTAL_HEADCOUNT": "Total Headcount",
        "ATTRITION_RATE": "Attrition Rate (%)",
        "AVERAGE_SALARY": "Average Salary",
        "AVERAGE_ENGAGEMENT": "Average Engagement Score",
        "MODEL_METRICS": "ML Model Evaluation Metrics"
    },
    "de": {
        "ACTIVE_HEADCOUNT": "Aktiver Mitarbeiterbestand",
        "TOTAL_HEADCOUNT": "Gesamtmitarbeiterzahl",
        "ATTRITION_RATE": "Fluktuationsrate (%)",
        "AVERAGE_SALARY": "Durchschnittsgehalt",
        "AVERAGE_ENGAGEMENT": "Durchschnittliches Engagement",
        "MODEL_METRICS": "ML-Modellbewertung"
    },
    "fr": {
        "ACTIVE_HEADCOUNT": "Effectif actif",
        "TOTAL_HEADCOUNT": "Effectif total",
        "ATTRITION_RATE": "Taux d’attrition (%)",
        "AVERAGE_SALARY": "Salaire moyen",
        "AVERAGE_ENGAGEMENT": "Engagement moyen",
        "MODEL_METRICS": "Évaluation du modèle ML"
    },
    "es": {
        "ACTIVE_HEADCOUNT": "Número de empleados activos",
        "TOTAL_HEADCOUNT": "Número total de empleados",
        "ATTRITION_RATE": "Tasa de rotación (%)",
        "AVERAGE_SALARY": "Salario promedio",
        "AVERAGE_ENGAGEMENT": "Compromiso promedio",
        "MODEL_METRICS": "Evaluación del modelo ML"
    }
}

def t(key, lang):
    return LABELS.get(lang, LABELS["en"]).get(key, key)

# ======================================================
# 🔐 HR DOMAIN GUARD
# ======================================================
HR_METRICS = {
        "headcount",
        "attrition",
        "salary",
        "engagement",
        "gender"
}

# ======================================================
# 🔒 STRICT QUERY NORMALIZER (THIS FIXES MULTILINGUAL)
# ======================================================
def normalize_query_to_english(query: str) -> str:
    """
    Translate HR analytics query to STRICT English keywords.
    No explanations. One sentence only.
    """
    prompt = f"""
Translate the following HR analytics question to English.

Rules:
- Use ONLY these words if applicable:
  headcount, attrition, salary, engagement, gender, department, year, location, chart
- Do NOT explain
- Do NOT add examples
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

    # --------------------------------------------------
    # 🌐 NORMALIZE QUERY (CRITICAL)
    # --------------------------------------------------
    if language != "en":
        normalized_query = normalize_query_to_english(query)
    else:
        normalized_query = query.lower().strip()

    q = normalized_query

    # ==================================================
    # 1️⃣ GREETINGS
    # ==================================================
    if q in ["hi", "hello", "hey", "hii"]:
        return (
            "👋 **Hi! I’m HR-GPT 3.0**\n\n"
            "You can ask:\n"
            "- Total / Active headcount\n"
            "- Headcount by department / gender / year\n"
            "- Attrition rate & trends\n"
            "- Salary & engagement analysis\n"
            "- Predict attrition risk (ML)"
        )

    # ==================================================
    # 2️⃣ LOAD DATA
    # ==================================================
    try:
        df = load_master()
    except Exception:
        return "⚠ Unable to load HR data."

    if df is None or df.empty:
        return "⚠ HR dataset is empty."

    # ==================================================
    # 3️⃣ NLU (ONLY ON NORMALIZED QUERY)
    # ==================================================
    metric = extract_metric(normalized_query)
    dimension = extract_dimension(normalized_query)
    chart_type = extract_chart_type(normalized_query)

    wants_chart = any(k in q for k in ["chart", "plot", "graph", "bar", "pie", "line"])
    wants_definition = any(k in q for k in ["what is", "define", "explain", "meaning"])
    wants_prediction = any(k in q for k in ["predict", "prediction", "risk", "likely"])
    wants_model_metrics = any(k in q for k in ["model", "auc", "precision", "recall"])

    # ==================================================
    # 4️⃣ DEFINITIONS → LLM (USER LANGUAGE)
    # ==================================================
    if wants_definition:
        return call_llm(query, language)

    # ==================================================
    # 5️⃣ ML ATTRITION PREDICTION
    # ==================================================
    if wants_prediction:
        try:
            pred_df = predict_attrition(df)
            pred_df = add_risk_bucket(pred_df)

            if wants_chart:
                return build_chart(
                    pred_df["Risk_Bucket"].value_counts(),
                    chart_type
                )

            return pred_df.sort_values("Attrition_Risk", ascending=False)

        except Exception:
            return "⚠ Unable to run attrition prediction model."

    # ==================================================
    # 6️⃣ ML MODEL METRICS
    # ==================================================
    if wants_model_metrics:
        try:
            return load_ml_metrics()
        except Exception:
            return "⚠ ML evaluation metrics not found."

    # ==================================================
    # 7️⃣ HEADCOUNT
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
            col = {
                "DEPARTMENT": "Department",
                "LOCATION": "Location",
                "GENDER": "Gender"
            }.get(dimension)

            if not col:
                return "⚠ Unsupported headcount breakdown."

            data = active_headcount_by(df, col)

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Headcount")

    # ==================================================
    # 8️⃣ ATTRITION
    # ==================================================
    if metric == "attrition":

        if not dimension:
            return pd.DataFrame({
                "Metric": [t("ATTRITION_RATE", language)],
                "Value": [attrition_rate(df)]
            })

        data = (
            attrition_by_year(df)
            if dimension == "YEAR"
            else attrition_rate_by(
                df,
                {"DEPARTMENT": "Department", "LOCATION": "Location", "GENDER": "Gender"}.get(dimension)
            )
        )

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Attrition Rate")

    # ==================================================
    # 9️⃣ SALARY
    # ==================================================
    if metric == "salary":

        if not dimension:
            return pd.DataFrame({
                "Metric": [t("AVERAGE_SALARY", language)],
                "Value": [average_salary(df)]
            })

        col = {"DEPARTMENT": "Department", "LOCATION": "Location", "GENDER": "Gender"}.get(dimension)
        data = average_salary_by(df, col)

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Average Salary")

    # ==================================================
    # 🔟 ENGAGEMENT
    # ==================================================
    if metric == "engagement":

        if not dimension:
            return pd.DataFrame({
                "Metric": [t("AVERAGE_ENGAGEMENT", language)],
                "Value": [average_engagement(df)]
            })

        col = {"DEPARTMENT": "Department", "LOCATION": "Location", "GENDER": "Gender"}.get(dimension)
        data = engagement_by(df, col)

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Engagement Score")

    # ==================================================
    # 1️⃣1️⃣ DIVERSITY
    # ==================================================
    if metric == "gender":
        data = gender_distribution(df)
        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Count")


       # ==================================================
        # 1️⃣2️⃣ DOMAIN GUARD (ABSOLUTE – NO LLM)
        # ==================================================
    if metric is None:
        return (
            "⚠ This assistant is strictly limited to **HR analytics only**.\n\n"
            "You can ask about:\n"
            "- Headcount\n"
            "- Attrition\n"
            "- Salary\n"
            "- Engagement\n"
            "- Workforce diversity\n\n"
            "Please rephrase your question within the HR domain."
        )
