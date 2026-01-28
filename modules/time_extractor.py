import re

def extract_time_window(query):
    q = query.lower()

    if "last year" in q:
        return {"type": "YEAR", "value": -1}
    if "last 3 years" in q:
        return {"type": "YEAR", "value": -3}
    if "last 6 months" in q:
        return {"type": "MONTH", "value": -6}

    return None
