# ml/interpret.py

import pandas as pd
import joblib

MODEL_PATH = "ml/models/attrition_ensemble.pkl"

FEATURES = [
    "Age",
    "Salary",
    "Experience_Years",
    "Engagement_Score",
    "Performance_Rating"
]


def get_feature_importance():
    model = joblib.load(MODEL_PATH)

    # Extract Random Forest from ensemble
    rf = dict(model.named_estimators_)["rf"]

    importances = rf.feature_importances_

    return (
        pd.Series(importances, index=FEATURES)
        .sort_values(ascending=False)
        .round(4)
    )
