def classify_question(query: str) -> str:
    q = query.lower()

    # ==================================================
    # 1️⃣ HR DEFINITIONS / CONCEPTS
    # ==================================================
    definition_triggers = [
        "what is", "define", "definition of", "meaning of",
        "explain", "difference between", "how do you define",
        "what does", "what do you mean by"
    ]

    hr_concepts = [
        # Core HR
        "headcount", "attrition", "turnover", "retention",
        "engagement", "performance", "promotion",
        "tenure", "experience", "salary", "compensation",
        "ctc", "bonus", "incentive",

        # Talent & hiring
        "time to hire", "time to fill", "hiring", "recruitment",
        "offer acceptance", "funnel",

        # DEI
        "gender ratio", "diversity", "inclusion", "pay gap",

        # Org
        "span of control", "org structure", "job level",
        "grade", "band", "fte",

        # Attrition concepts
        "regretted attrition", "voluntary attrition",
        "involuntary attrition", "early attrition"
    ]

    if any(t in q for t in definition_triggers) and any(c in q for c in hr_concepts):
        return "DEFINITION"

    # ==================================================
    # 2️⃣ ML / PREDICTIVE QUESTIONS
    # ==================================================
    ml_triggers = [
        "predict", "prediction", "risk", "likelihood",
        "chance of leaving", "who will leave",
        "flight risk", "high risk employees",
        "attrition risk", "resignation risk"
    ]

    if any(k in q for k in ml_triggers):
        return "ML"

    # ==================================================
    # 3️⃣ METRIC / ANALYTICS QUESTIONS
    # ==================================================
    metric_triggers = [
        # Core metrics
        "headcount", "attrition", "turnover",
        "salary", "compensation", "ctc",
        "engagement", "performance", "rating",

        # Hiring
        "hires", "joined", "new joiners",
        "open positions",

        # DEI
        "gender", "female", "male", "diversity",

        # Time-based
        "by department", "by team", "by location",
        "by year", "by month", "trend", "over time",

        # Output
        "table", "chart", "graph", "excel", "csv"
    ]

    if any(k in q for k in metric_triggers):
        return "METRIC"

    # ==================================================
    # 4️⃣ EXPLANATION / WHY QUESTIONS
    # ==================================================
    explanation_triggers = [
        "why", "reason", "cause", "drivers",
        "what is causing", "how to reduce",
        "how can we improve", "insights",
        "recommendations", "suggest"
    ]

    if any(k in q for k in explanation_triggers):
        return "EXPLANATION"

    # ==================================================
    # 5️⃣ GENERAL HR QUESTIONS
    # ==================================================
    return "GENERAL"
