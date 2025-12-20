def detect_intent(query: str):
    q = query.lower()

    # --- BASIC METRICS ---
    if "headcount" in q:
        if any(k in q for k in ["trend", "over", "year", "month", "history", "timeline", "time"]):
            return "HEADCOUNT_TREND"
        return "HEADCOUNT"

    if "attrition" in q:
        if any(k in q for k in ["trend", "year", "month", "over"]):
            return "ATTRITION_TREND"
        return "ATTRITION"

    if any(k in q for k in ["salary", "pay", "compensation", "wage"]):
        if any(k in q for k in ["by", "department", "role", "job"]):
            return "SALARY_GROUP"
        if any(k in q for k in ["trend", "over", "year"]):
            return "SALARY_TREND"
        return "SALARY"

    if any(k in q for k in ["gender mix", "gender ratio", "diversity", "male", "female"]):
        return "GENDER"

    if "engagement" in q:
        return "ENGAGEMENT"

    if "performance" in q:
        if any(k in q for k in ["by", "department"]):
            return "PERFORMANCE_GROUP"
        return "PERFORMANCE"

    if "promotion" in q:
        return "PROMOTION"

    if "hire" in q or "new join" in q or "joined" in q:
        return "HIRING"

    # --- CHART REQUESTS ---
    if any(k in q for k in ["chart", "plot", "graph", "visual"]):
        return "CHART"

    # --- ML Prediction ---
    if "predict attrition" in q:
        return "PREDICT_ATTRITION"

    # --- STATS ---
    if any(k in q for k in ["mean", "average"]):
        return "STATS_MEAN"
    if any(k in q for k in ["median"]):
        return "STATS_MEDIAN"
    if any(k in q for k in ["mode"]):
        return "STATS_MODE"
    if any(k in q for k in ["std", "standard deviation"]):
        return "STATS_STD"
    if any(k in q for k in ["percentile", "quartile"]):
        return "STATS_PERCENTILE"

    # default
    return "PURE_CHAT"
