def auto_chart(metric, dimension):
    if not dimension:
        return "KPI"

    if metric in ["gender", "attrition"]:
        return "PIE"

    return "BAR"
