import re

def extract_comparison(query):
    if " vs " not in query.lower():
        return None

    parts = query.split(" vs ")
    if len(parts) != 2:
        return None

    return {
        "left": parts[0].strip(),
        "right": parts[1].strip()
    }
