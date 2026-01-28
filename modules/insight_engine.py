from modules.llm_engine import call_llm

def explain_insight(data, metric, dimension):
    summary = data.describe().to_string()

    prompt = f"""
You are an HR analyst.

Explain the insight from this data
in 3 business lines.

Metric: {metric}
Dimension: {dimension}

Data:
{summary}
"""
    return call_llm(prompt, "en")
