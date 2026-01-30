# ml/train_attrition.py

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    precision_score,
    recall_score
)

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv("data/hr_master_10000.csv")
df["Attrition"] = (df["Status"] == "Resigned").astype(int)

features = [
    "Age",
    "Salary",
    "Experience_Years",
    "Engagement_Score",
    "Performance_Rating"
]

X = df[features]
y = df["Attrition"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

# ===============================
# MODELS
# ===============================
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

# ===============================
# TRAIN
# ===============================
ensemble.fit(X_train, y_train)

# ===============================
# EVALUATE
# ===============================
y_pred = ensemble.predict(X_test)
y_prob = ensemble.predict_proba(X_test)[:, 1]

print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

metrics = {
    "AUC": roc_auc_score(y_test, y_prob),
    "Precision": precision_score(y_test, y_pred),
    "Recall": recall_score(y_test, y_pred)
}

# ===============================
# SAVE
# ===============================
joblib.dump(ensemble, "ml/models/attrition_ensemble.pkl")
joblib.dump(metrics, "ml/models/attrition_metrics.pkl")

print("✅ Attrition model & metrics saved")
