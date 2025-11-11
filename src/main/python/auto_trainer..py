import os
import time
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

CSV_PATH = "system_metrics.csv"
MODEL_PATH = "iforest_model.joblib"
TRAIN_INTERVAL = 3600  # seconds (1 hour)
MIN_NEW_SAMPLES = 300  # retrain only if new rows added

def retrain_model():
    if not os.path.exists(CSV_PATH):
        print("⚠️ No system_metrics.csv found. Skipping retrain.")
        return

    df = pd.read_csv(CSV_PATH)
    if len(df) < 100:
        print("⚠️ Not enough data to retrain yet.")
        return

    print(f"📊 Retraining model with {len(df)} samples...")
    X = df[["cpu_percent","ram_percent","disk_read_MBps","disk_write_MBps",
            "net_sent_KBps","net_recv_KBps","process_count"]]

    model = IsolationForest(contamination=0.10, random_state=42)
    model.fit(X)
    joblib.dump(model, MODEL_PATH)
    print("✅ Model retrained and saved successfully!")

def monitor_and_retrain():
    last_size = os.path.getsize(CSV_PATH) if os.path.exists(CSV_PATH) else 0
    while True:
        time.sleep(TRAIN_INTERVAL)
        if not os.path.exists(CSV_PATH):
            continue
        current_size = os.path.getsize(CSV_PATH)
        if current_size > last_size + 1024:  # file grew
            print("🔁 Change detected in dataset. Retraining model...")
            retrain_model()
            last_size = current_size
        else:
            print("⏳ No significant data growth — skipping retrain.")

if __name__ == "__main__":
    print("🚀 Auto-trainer started. Monitoring dataset growth...")
    monitor_and_retrain()
