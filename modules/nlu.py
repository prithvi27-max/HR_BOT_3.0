import re

# ---------------------------
# MASTER METRIC DICTIONARIES
# ---------------------------
metric_keywords = {
    "headcount": [
        "headcount", "employee count", "workforce", "staff size",
        "total employees", "number of employees", "manpower"
    ],
    "attrition": [
        "attrition", "turnover", "churn", "exit rate",
        "resignation rate", "separation rate", "quit rate"
    ],
    "salary": [
        "salary", "compensation", "ctc", "pay", "wage",
        "package", "remuneration", "income"
    ],
    "gender": [
        "gender", "gender ratio", "gender mix", "female ratio",
        "male female ratio", "dei", "diversity"
    ],
    "performance": [
        "performance", "rating", "score", "kpi", "okr"
    ],
    "promotion": [
        "promotion", "career growth", "progression", "level change"
    ],
    "tenure": [
        "tenure", "experience", "duration", "years worked"
    ],
    "engagement": [
        "engagement", "happiness", "satisfaction", "sentiment"
    ],
    "forecast": [
        "forecast", "predict", "projection", "future"
    ]
}

# ---------------------------
# DIMENSION EXTRACTION (BY WHAT?)
# ---------------------------
dimension_keywords = {
    "YEAR": ["year", "annual", "per year", "trend", "over time", "timeline", "yearly"],
    "MONTH": ["month", "monthly"],
    "QUARTER": ["quarter", "q1", "q2", "q3", "q4"],
    "DEPARTMENT": ["department", "function", "team"],
    "LOCATION": ["location", "region", "country", "city", "branch"],
    "GENDER": ["male", "female", "gender"],
}

# ---------------------------
# CHART TYPES
# ---------------------------
def extract_chart_type(q):
    q = q.lower()
    
    if any(k in q for k in ["line", "trend", "over time", "time series", "timeline", "year"]):
        return "LINE"
    if any(k in q for k in ["pie", "ratio", "share", "gender mix"]):
        return "PIE"
    if any(k in q for k in ["histogram", "distribution", "range"]):
        return "HIST"
    if any(k in q for k in ["box", "median", "spread"]):
        return "BOX"
    if any(k in q for k in ["bar", "compare", "comparison"]):
        return "BAR"
    
    return "BAR"  # default fallback

# ---------------------------
# METRIC INTENT DETECTION
# ---------------------------
def extract_metric(query):
    q = query.lower()
    for metric, synonyms in metric_keywords.items():
        if any(word in q for word in synonyms):
            return metric
    return None

# ---------------------------
# DIMENSION DETECTION
# ---------------------------
def extract_dimension(query):
    q = query.lower()
    for dim, synonyms in dimension_keywords.items():
        if any(word in q for word in synonyms):
            return dim
    return None

# ---------------------------
# MAIN INTENT DETECTION
# ---------------------------
def detect_intent(query):
    q = query.lower()

    # Chart request?
    if any(k in q for k in ["chart", "plot", "graph", "visualize", "show", "distribution"]):
        return {"intent": "CHART"}

    # Forecast request
    if "forecast" in q or "predict" in q or "projection" in q:
        return {"intent": "FORECAST"}

    # Metric request
    metric = extract_metric(query)
    if metric:
        return {"intent": "METRIC", "metric": metric}

    # HR concept – definition
    if any(k in q for k in ["what is", "meaning", "define", "explain"]):
        return {"intent": "DEFINITION"}

    # Fallback to LLM
    return {"intent": "GENERAL"}
