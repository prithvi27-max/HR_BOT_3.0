import pandas as pd

# ===============================
# CORE ANALYTICS (EXISTING)
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

# ===============================
# NLU (ONLY EXISTING FUNCTIONS)
# ===============================
from modules.nlu import (
    extract_metric,
    extract_dimension,
    extract_chart_type
)

from modules.charts import build_chart
from modules.llm_engine import call_llm

# ===============================
# ML (ONLY EXISTING FILES)
# ===============================
from ml.predict import predict_attrition, add_risk_bucket
from ml.evaluate import load_ml_metrics


# ======================================================
# 🌍 MULTI-LANGUAGE LABEL MAP (SAFE & EXAM-READY)
# ======================================================
LABELS = {
    "en": {
        "ACTIVE_HEADCOUNT": "Active Headcount",
        "TOTAL_HEADCOUNT": "Total Headcount",
        "ATTRITION_RATE": "Attrition Rate (%)",
        "AVERAGE_SALARY": "Average Salary",
        "AVERAGE_ENGAGEMENT": "Average Engagement Score",
        "ATTRITION_PREDICTION": "Attrition Prediction Results",
        "MODEL_METRICS": "ML Model Evaluation Metrics"
    },
    "de": {
        "ACTIVE_HEADCOUNT": "Aktiver Mitarbeiterbestand",
        "TOTAL_HEADCOUNT": "Gesamtmitarbeiterzahl",
        "ATTRITION_RATE": "Fluktuationsrate (%)",
        "AVERAGE_SALARY": "Durchschnittsgehalt",
        "AVERAGE_ENGAGEMENT": "Durchschnittliches Engagement",
        "ATTRITION_PREDICTION": "Fluktuationsvorhersage",
        "MODEL_METRICS": "ML-Modellbewertung"
    },
    "fr": {
        "ACTIVE_HEADCOUNT": "Effectif actif",
        "TOTAL_HEADCOUNT": "Effectif total",
        "ATTRITION_RATE": "Taux d’attrition (%)",
        "AVERAGE_SALARY": "Salaire moyen",
        "AVERAGE_ENGAGEMENT": "Engagement moyen",
        "ATTRITION_PREDICTION": "Prédiction d’attrition",
        "MODEL_METRICS": "Évaluation du modèle ML"
    }
}


def t(key, lang):
    """Translate metric labels safely"""
    return LABELS.get(lang, LABELS["en"]).get(key, key)


# ======================================================
# 🚦 MAIN ROUTER
# ======================================================
def process_query(query: str, language: str = "en"):
    q = query.lower().strip()

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
    # 3️⃣ SIGNAL EXTRACTION
    # ==================================================
    metric = extract_metric(query)
    dimension = extract_dimension(query)
    chart_type = extract_chart_type(query)

    wants_chart = any(k in q for k in ["chart", "plot", "graph", "bar", "pie", "line"])
    wants_definition = any(k in q for k in ["what is", "define", "explain", "meaning"])
    wants_prediction = any(k in q for k in ["predict", "prediction", "risk", "likely to leave"])
    wants_model_metrics = any(k in q for k in ["model performance", "auc", "precision", "recall"])

    # ==================================================
    # 4️⃣ DEFINITIONS → LLM (MULTILINGUAL)
    # ==================================================
    if wants_definition:
        return call_llm(query, language)

    # ==================================================
    # 5️⃣ ML ATTRITION PREDICTION (🔥 PRIORITY)
    # ==================================================
    if wants_prediction:
        try:
            pred_df = predict_attrition(df)
            pred_df = add_risk_bucket(pred_df)

            # Chart: Risk bucket distribution
            if wants_chart:
                risk_counts = pred_df["Risk_Bucket"].value_counts()
                return build_chart(risk_counts, chart_type)

            # Return ALL active employees (not just top 20)
            return (
                pred_df
                .sort_values("Attrition_Risk", ascending=False)
                .reset_index(drop=True)
            )

        except Exception:
            return "⚠ Unable to run attrition prediction model."

    # ==================================================
    # 6️⃣ ML MODEL EVALUATION METRICS
    # ==================================================
    if wants_model_metrics:
        try:
            metrics_df = load_ml_metrics()
            metrics_df.insert(0, "Metric Type", t("MODEL_METRICS", language))
            return metrics_df
        except Exception:
            return "⚠ ML evaluation metrics not found. Train the model first."

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
            col_map = {
                "DEPARTMENT": "Department",
                "LOCATION": "Location",
                "GENDER": "Gender"
            }
            col = col_map.get(dimension)
            if not col:
                return "⚠ Unsupported headcount breakdown."
            data = active_headcount_by(df, col)

        if wants_chart:
            return build_chart(data, chart_type)

        return data.reset_index(name="Headcount")

    # ==================================================
    # 8️⃣ ATTRITION (DESCRIPTIVE)
    # ==================================================
    if metric == "attrition":

        if not dimension:
            return pd.DataFrame({
                "Metric": [t("ATTRITION_RATE", language)],
                "Value": [attrition_rate(df)]
            })

        if dimension == "YEAR":
            data = attrition_by_year(df)
        else:
            col_map = {
                "DEPARTMENT": "Department",
                "LOCATION": "Location",
                "GENDER": "Gender"
            }
            col = col_map.get(dimension)
            if not col:
                return "⚠ Unsupported attrition breakdown."
            data = attrition_rate_by(df, col)

        if wants_chart:
            return build_chart(data, chart_type)

        return data.reset_index(name="Attrition Rate")

    # ==================================================
    # 9️⃣ SALARY
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
        col = col_map.get(dimension)
        if not col:
            return "⚠ Unsupported salary breakdown."

        data = average_salary_by(df, col)

        if wants_chart:
            return build_chart(data, chart_type)

        return data.reset_index(name="Average Salary")

    # ==================================================
    # 🔟 ENGAGEMENT
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
        col = col_map.get(dimension)
        if not col:
            return "⚠ Unsupported engagement breakdown."

        data = engagement_by(df, col)

        if wants_chart:
            return build_chart(data, chart_type)

        return data.reset_index(name="Engagement Score")

    # ==================================================
    # 1️⃣1️⃣ DIVERSITY
    # ==================================================
    if metric == "gender":
        data = gender_distribution(df)

        if wants_chart:
            return build_chart(data, chart_type)

        return data.reset_index(name="Count")

    # ==================================================
    # 1️⃣2️⃣ FALLBACK → LLM (MULTILINGUAL)
    # ==================================================
    return call_llm(query, language)
