import streamlit as st
import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    roc_curve,
    roc_auc_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    classification_report
)

# -----------------------------------------
# IMPORTANT: Use SAME FEATURES as training
# -----------------------------------------
FEATURES = [
    "Age",
    "Salary",
    "Experience_Years",
    "Engagement_Score",
    "Performance_Rating"
]

# -----------------------------------------
# Streamlit Page Config
# -----------------------------------------
st.set_page_config(
    page_title="Attrition Model Evaluation",
    layout="wide"
)

st.title("📊 HR-GPT 3.0 — Attrition Model Evaluation Dashboard")

# -----------------------------------------
# Load Data
# -----------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/hr_master_10000.csv")
    df["Attrition"] = (df["Status"] == "Resigned").astype(int)
    return df

df = load_data()

# Ensure correct feature order and presence
missing = [f for f in FEATURES if f not in df.columns]
if missing:
    st.error(f"Missing features in dataset: {missing}")
    st.stop()

X = df[FEATURES].fillna(df[FEATURES].mean())
y = df["Attrition"]

# -----------------------------------------
# Load Trained Model
# -----------------------------------------
model = joblib.load("ml/models/attrition_ensemble.pkl")

# Probability predictions
y_prob = model.predict_proba(X)[:, 1]

# -----------------------------------------
# Threshold Slider
# -----------------------------------------
threshold = st.slider(
    "Select Decision Threshold",
    min_value=0.1,
    max_value=0.9,
    value=0.3,
    step=0.05
)

y_pred = (y_prob > threshold).astype(int)

# -----------------------------------------
# Metrics Calculation
# -----------------------------------------
auc_score = roc_auc_score(y, y_prob)
report = classification_report(y, y_pred, output_dict=True)
report_df = pd.DataFrame(report).transpose()

# -----------------------------------------
# Top Metrics Section
# -----------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔹 Key Performance Metrics")
    st.metric("AUC Score", round(auc_score, 3))
    st.metric("Accuracy", round(report["accuracy"], 3))
    st.metric("Recall (Attrition)", round(report["1"]["recall"], 3))
    st.metric("Precision (Attrition)", round(report["1"]["precision"], 3))
    st.metric("F1 Score (Attrition)", round(report["1"]["f1-score"], 3))

with col2:
    st.subheader("🔹 Classification Report")
    st.dataframe(report_df.round(3), use_container_width=True)

# -----------------------------------------
# ROC + Confusion Matrix Side by Side
# -----------------------------------------
col3, col4 = st.columns(2)

# ROC Curve
with col3:
    st.subheader("📈 ROC Curve")

    fpr, tpr, _ = roc_curve(y, y_prob)

    fig1, ax1 = plt.subplots(figsize=(5, 4))
    ax1.plot(fpr, tpr, label="ROC Curve")
    ax1.plot([0, 1], [0, 1], linestyle="--")
    ax1.set_xlabel("False Positive Rate")
    ax1.set_ylabel("True Positive Rate")
    ax1.set_title(f"AUC = {round(auc_score, 3)}")
    ax1.legend()

    plt.tight_layout()
    st.pyplot(fig1)


# Confusion Matrix
with col4:
    st.subheader("📊 Confusion Matrix")

    cm = confusion_matrix(y, y_pred)

    fig2, ax2 = plt.subplots(figsize=(5, 4))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(ax=ax2)

    plt.tight_layout()
    st.pyplot(fig2)


# -----------------------------------------
# Feature Importance (Optional Insight)
# -----------------------------------------
st.subheader("🔎 Model Feature Insights")

st.info(
    "This ensemble model uses Age, Salary, Experience, Engagement Score, "
    "and Performance Rating as predictive drivers of attrition."
)

st.success(
    "✅ This dashboard demonstrates enterprise-grade model evaluation, "
    "threshold tuning, ROC analysis, and performance monitoring."
)
