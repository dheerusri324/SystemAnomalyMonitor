import sys
import json
import numpy as np
import psutil
from collections import deque
from sklearn.ensemble import IsolationForest
import joblib

# Load trained ML model
model = joblib.load("iforest_model.joblib")

# Rolling history for adaptive stats
cpu_history = deque(maxlen=30)
ram_history = deque(maxlen=30)

def gather_live_metrics():
    disk = psutil.disk_io_counters()
    net = psutil.net_io_counters()
    process_count = len(psutil.pids())

    # Just one-second snapshot
    metrics = {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk_read_MBps": disk.read_bytes / (1024 * 1024),
        "disk_write_MBps": disk.write_bytes / (1024 * 1024),
        "net_sent_KBps": net.bytes_sent / 1024,
        "net_recv_KBps": net.bytes_recv / 1024,
        "process_count": process_count
    }
    return metrics

def detect_anomaly(metrics):
    cpu = metrics["cpu"]
    ram = metrics["ram"]
    cpu_history.append(cpu)
    ram_history.append(ram)

    if len(cpu_history) > 10:
        cpu_mean = np.mean(cpu_history)
        cpu_std = np.std(cpu_history)
        ram_mean = np.mean(ram_history)
        ram_std = np.std(ram_history)
        cpu_anomaly = abs(cpu - cpu_mean) > 2 * cpu_std
        ram_anomaly = abs(ram - ram_mean) > 2 * ram_std
    else:
        cpu_anomaly = ram_anomaly = False

    # ML-based anomaly detection
    X = np.array([[metrics["cpu"], metrics["ram"], metrics["disk_read_MBps"],
                   metrics["disk_write_MBps"], metrics["net_sent_KBps"],
                   metrics["net_recv_KBps"], metrics["process_count"]]])
    pred = model.predict(X)[0] == -1

    # Hybrid final decision
    anomaly = cpu_anomaly or ram_anomaly or pred

    return {
        "anomaly": bool(anomaly),
        "cpu": float(round(cpu, 2)),
        "ram": float(round(ram, 2)),
        "ml_flag": bool(pred),
        "cpu_avg": float(round(np.mean(cpu_history), 2)),
        "ram_avg": float(round(np.mean(ram_history), 2))
    }

def main():
    try:
        # If Java sends input via stdin
        data = sys.stdin.read().strip()
        if data:
            metrics = json.loads(data)
        else:
            metrics = gather_live_metrics()

        result = detect_anomaly(metrics)
        print("DEBUG:", metrics, flush=True)

        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
