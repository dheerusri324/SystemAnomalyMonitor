import socket
import json
import time
import psutil
import numpy as np
from collections import deque
from sklearn.ensemble import IsolationForest
import joblib
import pandas as pd

# Load trained model
model = joblib.load("iforest_model.joblib")

HOST = "127.0.0.1"
PORT = 5055

cpu_hist = deque(maxlen=30)
ram_hist = deque(maxlen=30)

def detect_anomaly():
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_io_counters()
    net = psutil.net_io_counters()
    proc = len(psutil.pids())

    cpu_hist.append(cpu)
    ram_hist.append(ram)

    if len(cpu_hist) > 10:
        cpu_mean, cpu_std = np.mean(cpu_hist), np.std(cpu_hist)
        ram_mean, ram_std = np.mean(ram_hist), np.std(ram_hist)
        cpu_spike = abs(cpu - cpu_mean) > 1.2 * cpu_std
        ram_spike = abs(ram - ram_mean) > 1.2 * ram_std
    else:
        cpu_spike = ram_spike = False

    columns = [
        "cpu_percent",
        "ram_percent",
        "disk_read_MBps",
        "disk_write_MBps",
        "net_sent_KBps",
        "net_recv_KBps",
        "process_count"
    ]

    X= pd.DataFrame([[
        cpu,
        ram,
        disk.read_bytes / (1024 * 1024),
        disk.write_bytes / (1024 * 1024),
        net.bytes_sent / 1024,
        net.bytes_recv / 1024,
        proc
    ]], columns=columns)

    pred = model.predict(X)[0] == -1

    anomaly = cpu_spike or ram_spike or pred

    return {
        "anomaly": bool(anomaly),
        "ml_flag": bool(pred),
        "cpu": float(round(cpu, 2)),
        "ram": float(round(ram, 2)),
        "proc": int(proc)
    }

# --- helper to convert any NumPy types safely ---
def to_native(val):
    if isinstance(val, (np.bool_,)):
        return bool(val)
    elif isinstance(val, (np.integer,)):
        return int(val)
    elif isinstance(val, (np.floating,)):
        return float(val)
    elif isinstance(val, dict):
        return {k: to_native(v) for k, v in val.items()}
    elif isinstance(val, (list, tuple)):
        return [to_native(v) for v in val]
    else:
        return val

# --- main server loop ---
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"🚀 Anomaly server running on {HOST}:{PORT}")
    while True:
        conn, _ = s.accept()
        with conn:
            data = conn.recv(16)
            if not data:
                continue
            result = detect_anomaly()
            result = to_native(result)
            conn.sendall(json.dumps(result).encode("utf-8"))
