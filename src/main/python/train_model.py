import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# Load logged system metrics
df = pd.read_csv("system_metrics.csv")

# Drop non-numeric columns
df = df.drop(columns=["timestamp"])

# Train Isolation Forest on all numeric features
model = IsolationForest(
    contamination=0.10,   # roughly 5% expected anomalies
    n_estimators=200,
    random_state=42
)
model.fit(df)

# Save model
joblib.dump(model, "iforest_model.joblib")
print("✅ Trained model saved as iforest_model.joblib")
