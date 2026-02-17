# ml/train_attrition.py

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import classification_report, roc_auc_score, precision_score, recall_score

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
df = pd.read_csv("data/hr_master_10000.csv")

df["Attrition"] = (df["Status"] == "Resigned").astype(int)

FEATURES = [
    "Age",
    "Salary",
    "Experience_Years",
    "Engagement_Score",
    "Performance_Rating"
]

X = df[FEATURES].fillna(df[FEATURES].mean())
y = df["Attrition"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# --------------------------------------------------
# MODELS
# --------------------------------------------------
lr = Pipeline([
    ("scaler", StandardScaler()),
    ("lr", LogisticRegression(max_iter=1000, class_weight="balanced"))
])

rf = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

gb = GradientBoostingClassifier(random_state=42)

ensemble = VotingClassifier(
    estimators=[
        ("lr", lr),
        ("rf", rf),
        ("gb", gb)
    ],
    voting="soft"
)

# --------------------------------------------------
# TRAIN
# --------------------------------------------------
ensemble.fit(X_train, y_train)

y_prob = ensemble.predict_proba(X_test)[:, 1]
y_pred = (y_prob >= 0.35).astype(int)
y_prob = ensemble.predict_proba(X_test)[:, 1]

print("\nClassification Report")
print(classification_report(y_test, y_pred, zero_division=0))

# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------
joblib.dump(ensemble, "ml/models/attrition_ensemble.pkl")

# --------------------------------------------------
# SAVE METRICS (FOR DASHBOARD)
# --------------------------------------------------
metrics = {
    "AUC": roc_auc_score(y_test, y_prob),
    "Precision": precision_score(y_test, y_pred, zero_division=0),
    "Recall": recall_score(y_test, y_pred, zero_division=0),
}

joblib.dump(metrics, "ml/models/attrition_metrics.pkl")

print("✅ Model & metrics saved successfully")
