from modules.llm_engine import call_llm
import json


def classify_domain(query):
    """
    LLM-based domain classifier.
    Returns:
    {
        "domain": "HR" | "NON_HR",
        "confidence": 0-1
    }
    """

    prompt = f"""
You are a strict domain classifier.

Decide whether the user's query belongs to the HR / Workforce / People Analytics domain.

HR domain includes:
- Headcount, attrition, hiring, salary, compensation
- Performance, engagement, promotion, tenure
- HR dashboards, workforce trends, analytics, charts
- Predictive HR models

Non-HR domain includes:
- Weather, news, sports, politics
- Movies, general knowledge, travel, finance unrelated to HR
- Coding questions not related to HR analytics

Respond ONLY in valid JSON.

Format:
{{
  "domain": "HR" or "NON_HR",
  "confidence": 0.0 to 1.0
}}

User query:
\"\"\"{query}\"\"\"
"""

    try:
        response = call_llm(prompt, language="en")
        result = json.loads(response)

        if "domain" not in result:
            return {"domain": "HR", "confidence": 0.5}  # SAFE DEFAULT

        return result

    except Exception:
        # Fail-open for HR analytics (industry practice)
        return {"domain": "HR", "confidence": 0.4}
