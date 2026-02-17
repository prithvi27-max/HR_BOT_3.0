# modules/nlu.py

import re

# ==================================================
# NORMALIZATION
# ==================================================
def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains(text: str, phrase: str) -> bool:
    """
    Safe word-boundary matching
    """
    pattern = r"\b" + re.escape(phrase) + r"\b"
    return re.search(pattern, text) is not None


# ==================================================
# METRIC KEYWORDS (FALLBACK ONLY)
# ==================================================
metric_keywords = {
    "headcount": [
        "headcount",
        "employee",
        "employees",
        "employee count",
        "workforce",
        "staff",
        "manpower",
        "people",
        "persons",
        "individuals",
        "participants"
    ],
    "attrition": [
        "attrition",
        "turnover",
        "resignation",
        "exit",
        "separation"
    ],
    "salary": [
        "salary",
        "compensation",
        "pay",
        "ctc",
        "remuneration"
    ],
    "engagement": [
        "engagement",
        "satisfaction",
        "sentiment",
        "happiness"
    ],
    "gender": [
        "gender",
        "diversity",
        "male",
        "female"
    ]
}


# ==================================================
# DIMENSION KEYWORDS (FALLBACK)
# ==================================================
dimension_keywords = {
    "YEAR": [
        "year",
        "years",
        "annual",
        "annually",
        "per year",
        "by year",
        "over time",
        "trend"
    ],
    "DEPARTMENT": [
        "department",
        "function",
        "team",
        "business unit"
    ],
    "LOCATION": [
        "location",
        "region",
        "country",
        "city",
        "office"
    ],
    "GENDER": [
        "gender",
        "male",
        "female"
    ]
}


# ==================================================
# METRIC EXTRACTION (FALLBACK)
# ==================================================
def extract_metric(query: str):
    q = normalize_text(query)

    for metric, words in metric_keywords.items():
        for word in words:
            if contains(q, word):
                return metric

    return None


# ==================================================
# DIMENSION EXTRACTION (FALLBACK)
# ==================================================
def extract_dimension(query: str):
    q = normalize_text(query)

    for dim, words in dimension_keywords.items():
        for word in words:
            if contains(q, word):
                return dim

    return None


# ==================================================
# CHART TYPE EXTRACTION (FALLBACK)
# ==================================================
def extract_chart_type(query: str):
    q = normalize_text(query)

    if any(contains(q, k) for k in ["line", "trend", "time series"]):
        return "LINE"

    if any(contains(q, k) for k in ["pie", "ratio", "share"]):
        return "PIE"

    if any(contains(q, k) for k in ["bar", "compare", "comparison"]):
        return "BAR"

    return "NONE"
