import json
from modules.llm_engine import call_llm

def extract_filters(query):
    prompt = f"""
Extract HR filters from the query.

Allowed columns:
Department, Location, Region, Gender,
Job_Level, Employment_Type, Status

Return JSON only.

Format:
{{
  "filters": [
    {{ "column": "Region", "op": "=", "value": "India" }}
  ]
}}

If none:
{{ "filters": [] }}

Query:
\"\"\"{query}\"\"\"
"""
    try:
        response = call_llm(prompt, "en")
        return json.loads(response)["filters"]
    except:
        return []
