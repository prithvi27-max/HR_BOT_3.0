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
