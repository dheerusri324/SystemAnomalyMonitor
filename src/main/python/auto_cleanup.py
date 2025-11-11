import os
import pandas as pd
from datetime import datetime, timedelta

CSV_PATH = "system_metrics.csv"
MAX_DAYS = 7

def cleanup():
    if not os.path.exists(CSV_PATH):
        print("⚠️ No dataset found.")
        return

    df = pd.read_csv(CSV_PATH)
    if "timestamp" not in df.columns:
        print("⚠️ No timestamp column found — skipping cleanup.")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    cutoff = datetime.now() - timedelta(days=MAX_DAYS)
    new_df = df[df["timestamp"] > cutoff]

    removed = len(df) - len(new_df)
    new_df.to_csv(CSV_PATH, index=False)

    print(f"🧹 Cleanup complete. Removed {removed} old rows.")

if __name__ == "__main__":
    cleanup()
