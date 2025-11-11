import socket
import json
import time
import threading
import psutil
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os
from datetime import datetime, timedelta
from collections import deque

HOST = "127.0.0.1"
PORT = 5055

CSV_PATH = "system_metrics.csv"
MODEL_PATH = "iforest_model.joblib"

cpu_hist = deque(maxlen=30)
ram_hist = deque(maxlen=30)
lock = threading.Lock()

# --- Anomaly detection core -------------------------------------------------
def detect_anomaly(model):
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_io_counters()
    net = psutil.net_io_counters()
    proc = len(psutil.pids())

    cpu_hist.append(cpu)
    ram_hist.append(ram)

    X = np.array([[cpu, ram,
                   disk.read_bytes/(1024*1024),
                   disk.write_bytes/(1024*1024),
                   net.bytes_sent/1024,
                   net.bytes_recv/1024,
                   proc]])

    ml_flag = False
    try:
        pred = model.predict(X)[0]
        ml_flag = pred == -1
    except Exception as e:
        print("⚠️ Prediction error:", e)

    # Statistical spike detection
    cpu_spike = False
    ram_spike = False
    if len(cpu_hist) > 10:
        cpu_mean, cpu_std = np.mean(cpu_hist), np.std(cpu_hist)
        ram_mean, ram_std = np.mean(ram_hist), np.std(ram_hist)
        cpu_spike = abs(cpu - cpu_mean) > 1.2 * cpu_std
        ram_spike = abs(ram - ram_mean) > 1.2 * ram_std

    anomaly = ml_flag or cpu_spike or ram_spike

    # --- Log current reading to CSV for self-learning ---
    try:
        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_percent": cpu,
            "ram_percent": ram,
            "disk_read_MBps": disk.read_bytes/(1024*1024),
            "disk_write_MBps": disk.write_bytes/(1024*1024),
            "net_sent_KBps": net.bytes_sent/1024,
            "net_recv_KBps": net.bytes_recv/1024,
            "process_count": proc
        }
        df = pd.DataFrame([row])
        header = not os.path.exists(CSV_PATH)
        df.to_csv(CSV_PATH, mode="a", header=header, index=False)
    except Exception as e:
        print("⚠️ Logging error:", e)


    return {
        "anomaly": anomaly,
        "ml_flag": ml_flag,
        "cpu": round(cpu, 2),
        "ram": round(ram, 2),
        "proc": proc
    }

# --- Background cleanup thread ----------------------------------------------
def cleanup_old_data():
    while True:
        try:
            if os.path.exists(CSV_PATH):
                df = pd.read_csv(CSV_PATH)
                if "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
                    cutoff = datetime.now() - timedelta(days=7)
                    new_df = df[df["timestamp"] > cutoff]
                    removed = len(df) - len(new_df)
                    if removed > 0:
                        new_df.to_csv(CSV_PATH, index=False)
                        print(f"🧹 Cleanup: removed {removed} rows older than 7 days.")
            time.sleep(21600)  # run every 6 hours
        except Exception as e:
            print("⚠️ Cleanup thread error:", e)
            time.sleep(3600)

# --- Background retrain thread ---------------------------------------------
def auto_retrain():
    last_size = os.path.getsize(CSV_PATH) if os.path.exists(CSV_PATH) else 0
    while True:
        try:
            time.sleep(3600)  # check every hour
            if not os.path.exists(CSV_PATH):
                continue
            current_size = os.path.getsize(CSV_PATH)
            if current_size > last_size + 1024:  # file grew by >1KB
                print("🔁 Retraining IsolationForest with new data...")
                df = pd.read_csv(CSV_PATH)
                if len(df) > 100:
                    X = df[["cpu_percent","ram_percent","disk_read_MBps",
                            "disk_write_MBps","net_sent_KBps","net_recv_KBps",
                            "process_count"]]
                    model = IsolationForest(contamination=0.10, random_state=42)
                    model.fit(X)
                    with lock:
                        joblib.dump(model, MODEL_PATH)
                    print("✅ Model retrained and saved.")
                    last_size = current_size
                else:
                    print("⚠️ Not enough new data for retrain.")
        except Exception as e:
            print("⚠️ Retrain thread error:", e)
            time.sleep(3600)

# --- Server main loop -------------------------------------------------------
def run_server():
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("✅ Loaded existing model.")
    else:
        print("⚠️ No model found. Using default empty IsolationForest.")
        model = IsolationForest()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"🚀 Anomaly server running on {HOST}:{PORT}")

        while True:
            conn, _ = s.accept()
            with conn:
                try:
                    _ = conn.recv(16)
                    result = detect_anomaly(model)

                    def to_native(val):
                        if isinstance(val, np.bool_): return bool(val)
                        if isinstance(val, (np.integer,)): return int(val)
                        if isinstance(val, (np.floating,)): return float(val)
                        return val

                    result = {k: to_native(v) for k, v in result.items()}
                    conn.sendall(json.dumps(result).encode("utf-8"))

                except Exception as e:
                    print("⚠️ Connection error:", e)

# --- Entry point ------------------------------------------------------------
if __name__ == "__main__":
    threading.Thread(target=cleanup_old_data, daemon=True).start()
    threading.Thread(target=auto_retrain, daemon=True).start()
    run_server()
