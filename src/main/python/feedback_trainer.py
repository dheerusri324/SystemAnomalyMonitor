import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
import os

CSV_METRICS = "system_metrics.csv"
CSV_FEEDBACK = "feedback_log.csv"
MODEL_PATH = "iforest_model.joblib"

BASE_CONTAMINATION = 0.10
MIN_CONTAMINATION = 0.02
MAX_CONTAMINATION = 0.20


def compute_contamination():
    if not os.path.exists(CSV_FEEDBACK):
        return BASE_CONTAMINATION

    df = pd.read_csv(CSV_FEEDBACK)
    if len(df) < 10:
        return BASE_CONTAMINATION

    false_count = len(df[df["user_label"] == "FALSE"])
    total = len(df)

    false_rate = false_count / total
    contamination = BASE_CONTAMINATION - (false_rate * 0.08)

    contamination = max(MIN_CONTAMINATION, min(MAX_CONTAMINATION, contamination))
    return round(contamination, 3)


def retrain_with_feedback():
    if not os.path.exists(CSV_METRICS):
        print("⚠️ No metrics data found")
        return

    df = pd.read_csv(CSV_METRICS)
    if len(df) < 200:
        print("⚠️ Not enough data for retraining")
        return

    X = df[
        [
            "cpu_percent",
            "ram_percent",
            "disk_read_MBps",
            "disk_write_MBps",
            "net_sent_KBps",
            "net_recv_KBps",
            "process_count",
        ]
    ]

    contamination = compute_contamination()
    print(f"🧠 Feedback-aware contamination = {contamination}")

    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=150
    )
    model.fit(X)

    joblib.dump(model, MODEL_PATH)
    print("✅ Model retrained using user feedback")


if __name__ == "__main__":
    retrain_with_feedback()
