import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

# ============================
# Load Data
# ============================
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

# 🔥 SAME SPLIT AS TRAINING
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

# ============================
# Load Model
# ============================
model = joblib.load("ml/models/attrition_ensemble.pkl")

# ============================
# Predict on TEST DATA ONLY
# ============================
y_prob = model.predict_proba(X_test)[:, 1]

THRESHOLD = 0.30
y_pred = (y_prob >= THRESHOLD).astype(int)

print(f"\nUsing Threshold = {THRESHOLD} (TEST SET)")
print(classification_report(y_test, y_pred))
print("AUC:", roc_auc_score(y_test, y_prob))
