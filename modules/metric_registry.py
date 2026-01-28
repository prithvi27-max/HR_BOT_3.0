HR_METRICS = {
    "headcount": {
        "type": "count",
        "column": "Employee_ID",
        "filter": {"Status": ["Active"]}
    },
    "attrition": {
        "type": "ratio",
        "column": "Status",
        "positive": "Resigned"
    },
    "salary": {
        "type": "avg",
        "column": "Salary"
    },
    "gender": {
        "type": "distribution",
        "column": "Gender"
    },
    "tenure": {
        "type": "avg",
        "column": "Experience_Years"
    },
    "engagement": {
        "type": "avg",
        "column": "Engagement_Score"
    }
}
