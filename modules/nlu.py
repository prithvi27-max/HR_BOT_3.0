# modules/nlu.py

import re

METRICS = {
    "headcount": ["headcount", "employees", "workforce", "people"],
    "salary": ["salary", "pay", "comp", "wage"],
    "attrition": ["attrition", "turnover", "resign", "exit"],
}

DIMENSIONS = {
    "Gender": ["gender", "male", "female"],
    "Department": ["department", "dept"],
    "Location": ["location", "city", "region"],
    "Job_Level": ["job level", "level", "grade", "band"],
}

CHART_TYPES = {
    "pie": ["pie"],
    "bar": ["bar", "column"],
    "line": ["trend", "line", "time"],
    "hist": ["hist", "distribution"],
}


def detect_intent(query: str):
    q = query.lower()

    # Detect Chart Request
    if any(k in q for k in ["chart", "plot", "visual", "show", "graph", "pie", "bar", "line", "trend", "distribution"]):
        return {"intent": "CHART"}

    # Definition request
    if any(k in q for k in ["what is", "define", "explain", "meaning"]):
        return {"intent": "DEFINITION"}

    # Forecast or predict
    if any(k in q for k in ["predict", "forecast", "future", "probability"]):
        return {"intent": "ML_PREDICT"}

    # Otherwise general LLM
    return {"intent": "GENERAL"}


def extract_metric(query):
    q = query.lower()
    for metric, keys in METRICS.items():
        if any(k in q for k in keys):
            return metric
    return None


def extract_dimension(query):
    q = query.lower()
    for dim, keys in DIMENSIONS.items():
        if any(k in q for k in keys):
            return dim
    return None


def extract_chart_type(query):
    q = query.lower()
    for ctype, keys in CHART_TYPES.items():
        if any(k in q for k in keys):
            return ctype
    return "bar"   # default bar chart
