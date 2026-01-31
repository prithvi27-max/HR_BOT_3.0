import pandas as pd
from plotly.graph_objs import Figure

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
# NLU (EXISTING FUNCTIONS ONLY)
# ===============================
from modules.nlu import (
    extract_metric,
    extract_dimension,
    extract_chart_type
)

from modules.charts import build_chart
from modules.llm_engine import call_llm

# ===============================
# ML (EXISTING FILES ONLY)
# ===============================
from ml.predict import predict_attrition
from ml.evaluate import load_ml_metrics
from ml.predict import add_risk_bucket  # you already added this

# ======================================================
# MAIN ROUTER
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
    # 3️⃣ SIGNAL EXTRACTION (NO detect_intent)
    # ==================================================
    metric = extract_metric(query)
    dimension = extract_dimension(query)
    chart_type = extract_chart_type(query)

    wants_chart = any(k in q for k in ["chart", "plot", "graph", "bar", "pie", "line"])
    wants_definition = any(k in q for k in ["what is", "define", "explain", "meaning"])
    wants_prediction = any(k in q for k in ["predict", "prediction", "risk", "likely to leave"])
    wants_model_metrics = any(k in q for k in ["model performance", "auc", "precision", "recall"])

    # ==================================================
    # 4️⃣ DEFINITIONS → LLM
    # ==================================================
    if wants_definition:
        return call_llm(query, language)

    # ==================================================
    # 5️⃣ ML ATTRITION (🔥 OVERRIDE – VERY IMPORTANT)
    # ==================================================
    if wants_prediction:
        try:
            pred_df = predict_attrition(df)
            pred_df = add_risk_bucket(pred_df)

            if wants_chart:
                risk_counts = pred_df["Risk_Bucket"].value_counts()
                return build_chart(risk_counts, chart_type)

            return (
                pred_df
                .sort_values("Attrition_Risk", ascending=False)
                .head(10000)
            )
        except Exception:
            return "⚠ Unable to run attrition prediction model."

    # ==================================================
    # 6️⃣ ML MODEL EVALUATION
    # ==================================================
    if wants_model_metrics:
        try:
            return load_ml_metrics()
        except Exception:
            return "⚠ ML evaluation metrics not found. Train the model first."

    # ==================================================
    # 7️⃣ HEADCOUNT
    # ==================================================
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
    # 8️⃣ ATTRITION (DESCRIPTIVE ONLY)
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
                "Metric": ["Average Salary"],
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
                "Metric": ["Average Engagement Score"],
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
    # 1️⃣2️⃣ FALLBACK → LLM
    # ==================================================
    return call_llm(query, language)
