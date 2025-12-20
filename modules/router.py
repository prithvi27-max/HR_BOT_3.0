# modules/router.py

from modules.nlu import detect_intent

def route_query(query, language="en"):
    """
    Routes the query into the correct processing bucket
    and prepares a structured prompt for the LLM.
    """

    intent = detect_intent(query)

    # Structured instruction sent to LLM for response generation
    prompt = f"""
    Intent detected: {intent}
    User Query: "{query}"

    Based on the intent:
    - If ATTRITION → talk about attrition analytics & possible modeling
    - If SALARY → discuss salary trends or compensation analytics
    - If ENGAGEMENT → discuss survey sentiment & actions
    - If FORECAST → talk forecasting using ARIMA/LSTM
    - If HIRING → discuss funnel metrics (apps, screening, offer)
    - If POLICY → answer using HR policy knowledge
    - If GLOSSARY → define HR concept clearly
    - If GENERAL → answer naturally

    Always:
    - Keep answer short and analytical
    - Respond in requested language: {language}
    """

    return prompt
