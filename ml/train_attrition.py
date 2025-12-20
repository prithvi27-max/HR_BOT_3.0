# ml/train_attrition.py

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from ml.preprocess import load_base, preprocess_for_attrition

# Load raw dataset
df = load_base()

# Prepare training data
X, y = preprocess_for_attrition(df)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Evaluate baseline
accuracy = model.score(X_test, y_test)
print("\n🚀 Attrition Model Training Complete")
print("📊 Accuracy:", round(accuracy * 100, 2), "%")

# Save model
os.makedirs("models", exist_ok=True)
pickle.dump(model, open("models/attrition.pkl", "wb"))
print("💾 Model saved at models/attrition.pkl\n")
