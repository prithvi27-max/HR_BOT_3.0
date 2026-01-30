# modules/nlu.py

# ==================================================
# METRIC KEYWORDS
# ==================================================
metric_keywords = {
    "headcount": [
        "headcount", "employee count", "workforce",
        "staff size", "total employees", "manpower"
    ],
    "attrition": [
        "attrition", "turnover", "churn",
        "resignation", "exit rate", "separation"
    ],
    "salary": [
        "salary", "ctc", "compensation",
        "pay", "package", "remuneration"
    ],
    "gender": [
        "gender", "gender mix", "male female",
        "diversity", "dei"
    ],
    "engagement": [
        "engagement", "satisfaction",
        "happiness", "sentiment"
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
    "YEAR": ["year", "yearly", "annual", "over time", "trend"],
    "DEPARTMENT": ["department", "function", "team"],
    "LOCATION": ["location", "region", "country", "city"],
    "GENDER": ["gender", "male", "female"]
}


# ==================================================
# METRIC EXTRACTION
# ==================================================
def extract_metric(query: str):
    q = query.lower()
    for metric, synonyms in metric_keywords.items():
        if any(word in q for word in synonyms):
            return metric
    return None


# ==================================================
# DIMENSION EXTRACTION
# ==================================================
def extract_dimension(query: str):
    q = query.lower()
    for dim, synonyms in dimension_keywords.items():
        if any(word in q for word in synonyms):
            return dim
    return None
# ---------------------------
# CHART TYPE EXTRACTION
# ---------------------------
def extract_chart_type(query):
    q = query.lower()

    if any(k in q for k in ["line", "trend", "over time", "time series"]):
        return "LINE"

    if any(k in q for k in ["pie", "ratio", "share"]):
        return "PIE"

    if any(k in q for k in ["bar", "compare", "comparison"]):
        return "BAR"

    return "BAR"  # default
