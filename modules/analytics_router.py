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
# QUERY NORMALIZER (Multilingual Safe)
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
# MAIN ROUTER
# ======================================================
def process_query(query: str, language: str = "en"):

    # ==================================================
    # 1️⃣ NORMALIZE FIRST (CRITICAL FOR MULTILINGUAL)
    # ==================================================
    if language != "en":
        normalized_query = normalize_query_to_english(query)
    else:
        normalized_query = query.lower().strip()

    q = normalized_query

    # ==================================================
    # 2️⃣ GREETING
    # ==================================================
    if q in ["hi", "hello", "hey"]:
        return "👋 Hi! Ask me HR analytics questions."

    # ==================================================
    # 3️⃣ DEFINITION INTENT
    # ==================================================
    definition_keywords = [
        "what is", "definition", "define",
        "explain", "meaning", "tell me about"
    ]

    if any(k in q for k in definition_keywords):
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
    # 4️⃣ LOAD DATA
    # ==================================================
    df = load_master()

    if df is None or df.empty:
        return "⚠ Unable to load HR data."

    # ==================================================
    # 5️⃣ NLU
    # ==================================================
    metric = extract_metric(q)
    dimension = extract_dimension(q)
    chart_type = extract_chart_type(q)

    wants_chart = any(k in q for k in ["chart", "plot", "graph", "bar", "pie", "line"])

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
            col_map = {
                "DEPARTMENT": "Department",
                "LOCATION": "Location",
                "GENDER": "Gender"
            }
            data = active_headcount_by(df, col_map.get(dimension))

        if data is None:
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

        col_map = {
            "DEPARTMENT": "Department",
            "LOCATION": "Location",
            "GENDER": "Gender"
        }

        if dimension == "YEAR":
            data = attrition_by_year(df)
        else:
            data = attrition_rate_by(df, col_map.get(dimension))

        if data is None:
            return "⚠ Attrition data not available for this breakdown."

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

        col_map = {
            "DEPARTMENT": "Department",
            "LOCATION": "Location",
            "GENDER": "Gender"
        }

        data = average_salary_by(df, col_map.get(dimension))

        if data is None:
            return "⚠ Salary data not available."

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Average Salary")

    # ==================================================
    # ENGAGEMENT
    # ==================================================
    if metric == "engagement":

        if not dimension:
            return pd.DataFrame({
                "Metric": ["Average Engagement"],
                "Value": [average_engagement(df)]
            })

        col_map = {
            "DEPARTMENT": "Department",
            "LOCATION": "Location",
            "GENDER": "Gender"
        }

        data = engagement_by(df, col_map.get(dimension))

        if data is None:
            return "⚠ Engagement data not available."

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Engagement Score")

    # ==================================================
    # DIVERSITY
    # ==================================================
    if metric == "gender":

        data = gender_distribution(df)

        if data is None:
            return "⚠ Gender data not available."

        return build_chart(data, chart_type) if wants_chart else data.reset_index(name="Count")
