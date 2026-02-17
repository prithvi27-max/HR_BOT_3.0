# modules/nlu.py

import re

# ==================================================
# TEXT NORMALIZATION
# ==================================================
def normalize_text(text: str) -> str:
    """
    Lowercase + remove extra spaces
    """
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_phrase(text: str, phrase: str) -> bool:
    """
    Word-boundary safe phrase matching
    Prevents accidental substring matches
    """
    pattern = r"\b" + re.escape(phrase) + r"\b"
    return re.search(pattern, text) is not None


# ==================================================
# METRIC KEYWORDS
# ==================================================
metric_keywords = {
    "headcount": [
        "headcount", "employee count", "employees",
        "workforce", "staff size", "total employees",
        "manpower", "number of employees"
    ],
    "attrition": [
        "attrition", "turnover", "churn",
        "resignation", "exit rate", "separation",
        "leaving rate"
    ],
    "salary": [
        "salary", "ctc", "compensation",
        "pay", "package", "remuneration",
        "average pay"
    ],
    "gender": [
        "gender", "gender mix", "male female",
        "diversity", "dei", "gender distribution"
    ],
    "engagement": [
        "engagement", "satisfaction",
        "happiness", "sentiment",
        "employee satisfaction"
    ],
    "performance": [
        "performance", "rating", "kpi", "okr"
    ],
    "promotion": [
        "promotion", "career growth", "progression"
    ],
    "tenure": [
        "tenure", "experience", "years worked"
    ],
    "forecast": [
        "forecast", "predict", "projection"
    ]
}


# ==================================================
# DIMENSION KEYWORDS
# ==================================================
dimension_keywords = {
    "YEAR": [
        "year", "yearly", "annual",
        "over time", "trend", "by year"
    ],
    "DEPARTMENT": [
        "department", "function", "team",
        "business unit"
    ],
    "LOCATION": [
        "location", "region", "country",
        "city", "office"
    ],
    "GENDER": [
        "gender", "male", "female"
    ]
}


# ==================================================
# METRIC EXTRACTION
# ==================================================
def extract_metric(query: str):
    q = normalize_text(query)

    for metric, synonyms in metric_keywords.items():
        for phrase in synonyms:
            if contains_phrase(q, phrase):
                return metric

    return None


# ==================================================
# DIMENSION EXTRACTION
# ==================================================
def extract_dimension(query: str):
    q = normalize_text(query)

    for dim, synonyms in dimension_keywords.items():
        for phrase in synonyms:
            if contains_phrase(q, phrase):
                return dim

    return None


# ==================================================
# CHART TYPE EXTRACTION
# ==================================================
def extract_chart_type(query: str):
    q = normalize_text(query)

    if any(contains_phrase(q, k) for k in ["line", "trend", "over time", "time series"]):
        return "LINE"

    if any(contains_phrase(q, k) for k in ["pie", "ratio", "share"]):
        return "PIE"

    if any(contains_phrase(q, k) for k in ["bar", "compare", "comparison"]):
        return "BAR"

    return "BAR"  # default
