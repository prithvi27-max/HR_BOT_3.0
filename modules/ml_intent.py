def is_ml_query(query: str) -> bool:
    q = query.lower()

    ml_triggers = [
        "attrition risk",
        "predict attrition",
        "attrition prediction",
        "who will leave",
        "likelihood of leaving",
        "high risk employees",
        "flight risk"
    ]

    return any(k in q for k in ml_triggers)
