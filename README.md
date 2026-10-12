# 🛡️ E-Commerce Fake Review & Bot Spam Detection Engine

A production-grade **Forensic NLP & Behavioral Machine Learning Engine** designed to detect incentivized fake reviews, coordinated bot spam campaigns, and review manipulation on e-commerce platforms.

Orchestrated with **Apache Airflow 2.x** and accompanied by an interactive **Real-Time Forensic Web Dashboard**.

---

## 🏛️ System Architecture

```
                       ┌────────────────────────────────────────┐
                       │     Incoming Product Reviews Batch     │
                       └───────────────────┬────────────────────┘
                                           │
                                           ▼
                       ┌────────────────────────────────────────┐
                       │       Apache Airflow 2.x Pipeline      │
                       │   (5-Stage Automated Batch Workflow)   │
                       └───────────────────┬────────────────────┘
                                           │
         ┌─────────────────────────────────┼────────────────────────────────┐
         │                                 │                                │
         ▼                                 ▼                                ▼
┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
│  Duplicate & Bot │             │ Forensic Feature │             │  ML Probability  │
│  Cluster Engine  │             │   Engineering    │             │    Ensemble      │
│  (MinHash/Text)  │             │  (Caps, Lexical) │             │  (Scoring Model) │
└────────┬─────────┘             └─────────┬────────┘             └─────────┬────────┘
         │                                 │                                │
         └─────────────────────────────────┼────────────────────────────────┘
                                           │
                                           ▼
                       ┌────────────────────────────────────────┐
                       │        Quarantine & Store Sync         │
                       │       (SQLite Forensic Storage)        │
                       └───────────────────┬────────────────────┘
                                           │
                                           ▼
                       ┌────────────────────────────────────────┐
                       │   Interactive Forensic Web Dashboard   │
                       │    (FastAPI + Real-Time NLP UI)        │
                       └────────────────────────────────────────┘
```

---

## ✨ Key Capabilities

1. **Forensic Feature Engineering**:
   - **Linguistic Signals**: Uppercase shout ratio, exclamation density, punctuation anomalies.
   - **Lexical Diversity**: Type-Token Ratio (TTR) to spot repetitive promotional syntax.
   - **Superlative Extraction**: High-density promotional buzzwords (*"miracle"*, *"changed my life"*, *"100% recommend"*, *"best in universe"*).
   - **Sentiment Discrepancy**: Flags sharp conflicts between 5-star ratings and negative text (or vice versa).

2. **Bot Network & Astroturf Detection**:
   - **Near-Duplicate Grouping**: Identifies copy-paste bot reviews posted across disparate user accounts.
   - **Temporal Burst Analysis**: Detects sudden unnatural velocity spikes of unverified 5-star reviews (astroturfing) or 1-star reviews (competitor sabotage).

3. **Apache Airflow Orchestration**:
   - `task_ingest_raw_batch`: Ingests raw reviews feed.
   - `task_extract_bot_signals`: Analyzes copy-paste clusters and velocity bursts.
   - `task_run_ml_classification`: Applies multi-signal forensic classifier.
   - `task_quarantine_and_persist`: Isolates high-risk reviews and writes to SQLite database.
   - `task_generate_audit_report`: Produces daily fraud rate reports and executive metrics.



## 📂 Project Structure

```
E-Commerce-Fake-Review-Detection-Engine/
├── app/
│   ├── main.py                     # FastAPI REST API endpoints
│   └── static/
│       ├── index.html              # Modern forensic web dashboard
│       ├── style.css               # Responsive dark theme
│       └── app.js                  # Dynamic client-side logic
├── dags/
│   └── fake_review_detection_dag.py # Production Apache Airflow 2.x DAG
├── data/
│   └── sample_reviews.json         # Curated realistic review benchmark dataset
├── src/
│   ├── bot_detector.py             # Duplicate cluster & burst velocity detector
│   ├── db.py                       # SQLite persistence & audit query layer
│   ├── features.py                 # Forensic linguistic feature extractor
│   └── model.py                    # Multi-signal fake review classifier
├── config.py                       # Thresholds and configuration
├── requirements.txt                # Python dependencies
├── run.py                          # Application launcher
└── README.md                       # Documentation
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/detect` | Analyze a live review and return risk classification and flags |
| `POST` | `/api/run-pipeline` | Trigger the 5-stage batch Airflow detection pipeline |
| `GET` | `/api/metrics` | Retrieve store-wide fraud rate, quarantined, and authentic counts |
| `GET` | `/api/reviews` | List recently audited reviews with their risk scores |
| `GET` | `/api/health` | Health check endpoint |

---

## 📄 License
MIT License. Free for academic and commercial use.
