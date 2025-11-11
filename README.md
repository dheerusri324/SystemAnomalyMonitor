# 🧠 System Anomaly Monitor

A hybrid **JavaFX + Python** system that monitors your computer’s CPU, RAM, disk, network and process activity in real time and detects unusual behaviour using an **AI-based anomaly detection model (Isolation Forest)**. Built with a socket bridge so JavaFX UI and Python ML run decoupled for low-latency inference.

---

## 🚀 Highlights / Features

- ✅ Real-time system metrics dashboard (JavaFX)  
- ✅ Hybrid anomaly detection (statistical baseline + Isolation Forest ML)  
- ✅ Socket-based communication between Java (UI) and Python (ML server)  
- ✅ Personalized model training using per-user logs  
- ✅ Graceful fallback when Python ML server is offline  
- ✅ Modular design: easy to extend (auto-trainer, more features, REST API)

---

## 🧰 Tech Stack

| Component     | Technology                                                           |
|---------------|----------------------------------------------------------------------|
| Frontend UI   | JavaFX                                                               |
| Bridge        | Java socket + JSON                                                    |
| ML Engine     | Python (scikit-learn, psutil, numpy, pandas, joblib)                 |
| Anomaly model | Isolation Forest (unsupervised)                                      |
| Build         | Maven (mvnw included)                                                 |
| IDE           | IntelliJ IDEA Ultimate                                                |

---

## 📦 Repository structure

```
SystemAnomalyMonitor/
 ├─ src/
 │  ├─ main/
 │  │  ├─ java/com/dheeraj/systemanomalymonitor/   # JavaFX, bridge, controllers
 │  │  ├─ resources/com/dheeraj/systemanomalymonitor/  # FXML UI
 │  │  └─ python/  # Python scripts (logger, trainer, server, model)
 │  └─ test/
 ├─ pom.xml
 ├─ mvnw / mvnw.cmd
 ├─ .mvn/
 ├─ .gitignore
 └─ README.md
```

> **Note:** Large artifacts (e.g. `iforest_model.joblib`, `system_metrics.csv`) are in `.gitignore` and should not be pushed.

---

## ⚙️ Requirements (dev / run-time)

- Java 17 (or JDK matching `module-info.java`)  
- Maven (or use `./mvnw`)  
- Python 3.8+ (3.11 recommended)  
- Python packages:
```bash
pip install numpy pandas scikit-learn psutil joblib
```

---

## 🧾 Data schema (`system_metrics.csv`)

CSV header used by logger / trainer:

```
timestamp,cpu_percent,ram_percent,disk_read_MBps,disk_write_MBps,net_sent_KBps,net_recv_KBps,process_count
```

- `timestamp` — HH:MM:SS  
- `cpu_percent`, `ram_percent` — floats (0–100)  
- `disk_read_MBps`, `disk_write_MBps` — MB per second  
- `net_sent_KBps`, `net_recv_KBps` — KB per second  
- `process_count` — integer

---

## 🧠 How it works (component overview)

1. **Data Logger (`data_logger.py`)**  
   Samples system metrics every 1 second and appends to `system_metrics.csv`.

2. **Training (`train_model.py`)**  
   Loads `system_metrics.csv`, trains an `IsolationForest` and saves `iforest_model.joblib`.

3. **Real-time server (`anomaly_server.py`)**  
   Loads `iforest_model.joblib`, continuously samples system metrics, runs hybrid detection (rolling statistics + ML) and responds to Java via a local TCP socket (127.0.0.1:5055).

4. **JavaFX Client (Launcher + DashboardController)**  
   Periodically connects to the Python server, reads JSON (anomaly, ml_flag, cpu, ram, etc.), and updates UI (status + alert source). If server unreachable, UI falls back gracefully.

---

## 🔧 Quick start (developer flow)

Open terminal in project root and run these steps:

```bash
# 1) (optional) collect baseline data (do normal work for 20-40 minutes)
python src/main/python/data_logger.py

# 2) train the model
python src/main/python/train_model.py

# 3) start the real-time Python anomaly server (keep this running)
python src/main/python/anomaly_server.py

# 4) run the JavaFX UI (in IntelliJ: run Launcher.java or)
mvn javafx:run
```

---

## ✅ Demo / test utilities

- `anomaly_model.py` — single-run detector (reads stdin JSON or gathers live metrics if no input).  
- `simulate_anomalies()` — helper for producing synthetic spikes (temporarily used to verify detection logic).

---

## 🔁 Auto-trainer & auto-cleanup (v2.0 plan — implementation notes)

**auto_trainer.py** (recommended behavior)
- Runs on schedule (cron or Python loop)  
- Checks `system_metrics.csv` (rolling window: last N days or last M samples)  
- Retrains IsolationForest when enough new data exists  
- Saves `iforest_model.joblib` (atomic replace)  
- Optionally rotates/archives old logs (e.g., keep last 7 days) to prevent unbounded growth

**Auto-delete policy example**
- Keep last 7 days of CSV data; older rows are purged during retrain.  
- Or rotate CSV into `archive/YYYY-MM-DD.csv` nightly and compress.

---

## 🛠 Troubleshooting

- **No anomalies showing**:
  - Ensure Python server is running (`anomaly_server.py`).  
  - Check that `iforest_model.joblib` is present and trained on relevant data.  
  - If model is too tolerant: lower `contamination` or add delta-features.  
  - If spikes are brief, increase sampling resolution or run persistent server.

- **JSON / serialization errors**:
  - Convert NumPy types to Python types before `json.dumps()`.  
  - Already implemented via `to_native()` conversion.

- **Dashboard slow**:
  - Use the socket server (already implemented). Spawning Python each tick is slow.

---

## 🧩 Developer tips & best practices

- Keep `system_metrics.csv` and `iforest_model.joblib` **out of git** (`.gitignore`).  
- For reproducible results, create a small `sample_data/` with sanitized CSV.  
- Branch naming:
  - `main` — stable releases  
  - `v2-auto-train` — retraining & cleanup  
  - `feature/<name>` — experimental features

---

## 🧪 How to test the ML pipeline manually

```python
import joblib, pandas as pd
model = joblib.load("iforest_model.joblib")
X = pd.DataFrame([[90,95,50,40,2000,2000,500]], columns=[
    "cpu_percent","ram_percent","disk_read_MBps","disk_write_MBps",
    "net_sent_KBps","net_recv_KBps","process_count"])
print(model.predict(X))  # -1 => anomaly, 1 => normal
```

---

## 🧑‍💻 Contributing

1. Fork the repo  
2. Create `feature/<name>` branch  
3. Implement and test  
4. Submit PR to `main`

---

## 📜 License

MIT License © 2025 Bala Dheeraj Chennavaram

---

## 👋 Contact / Credits

**Author:** Bala Dheeraj Chennavaram  
Undergraduate @ Vasavi College of Engineering  
If you use this project in assignments or demos, please keep attribution.

---

## 🧾 Changelog (v1.0)

- Initial stable release:  
  - ✅ JavaFX UI  
  - ✅ Python ML pipeline  
  - ✅ Socket bridge integration  
  - ✅ Realtime anomaly monitoring  
  - ✅ Modular architecture for MLOps extensions
