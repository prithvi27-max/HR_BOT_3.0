# modules/analytics_router.py

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


# ======================================================
# 🌍 TRANSLATIONS
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
# 🌐 NORMALIZATION (MULTILINGUAL SAFE)
# ======================================================
def normalize_query_to_english(query: str) -> str:
    prompt = f"""
Translate this HR analytics question to English.

Rules:
- Use only HR terms like headcount, attrition, salary, engagement, gender, department, year.
- Return one short sentence only.

Query:
{query}
"""
    try:
        translated = call_llm(prompt, language="en")
        return translated.strip().lower()
    except:
        return query.lower().strip()


# ======================================================
# 🚦 MAIN ROUTER
# ======================================================
def process_query(query: str, language: str = "en"):

    original_query = query.strip().lower()

    # ==================================================
    # 1️⃣ GREETING (ALWAYS FIRST)
    # ==================================================
    greetings = [
        "hi", "hello", "hey", "hii",
        "hallo", "hola", "bonjour"
    ]

    if any(greet in original_query for greet in greetings):
        return "👋 Hello! I'm HR-GPT 3.0. Ask me about headcount, attrition, salary, engagement or diversity."

    # ==================================================
    # 2️⃣ DEFINITION INTENT
    # ==================================================
    definition_keywords = [
        "what is", "define", "definition",
        "meaning", "explain", "tell me about"
    ]

    if any(k in original_query for k in definition_keywords):
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
    # 3️⃣ NORMALIZE
    # ==================================================
    normalized_query = (
        normalize_query_to_english(query)
        if language != "en"
        else original_query
    )

    q = normalized_query

    # ==================================================
    # 4️⃣ LOAD DATA
    # ==================================================
    try:
        df = load_master()
    except:
        return "⚠ Unable to load HR data."

    if df is None or df.empty:
        return "⚠ HR dataset empty."

    # ==================================================
    # 5️⃣ NLU
    # ==================================================
    metric = extract_metric(q)
    dimension = extract_dimension(q)
    chart_type = extract_chart_type(q)

    wants_chart = any(k in q for k in ["chart", "graph", "plot", "bar", "line", "pie"])

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

        col_map = {
            "DEPARTMENT": "Department",
            "LOCATION": "Location",
            "GENDER": "Gender"
        }

        if dimension == "YEAR":
            data = active_headcount_by_year(df)
        else:
            data = active_headcount_by(df, col_map.get(dimension))

        if data is None:
            return "⚠ Headcount data not available for this breakdown."

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

        data = (
            attrition_by_year(df)
            if dimension == "YEAR"
            else attrition_rate_by(df, col_map.get(dimension))
        )

        if data is None:
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

        if data is None:
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

        if data is None:
            return "⚠ Engagement data not available for this breakdown."

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Engagement Score")

    # ==================================================
    # 👩‍💼 DIVERSITY
    # ==================================================
    if metric == "gender":

        data = gender_distribution(df)

        if data is None:
            return "⚠ Diversity data not available."

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Count")

    return "⚠ Unable to process request."
