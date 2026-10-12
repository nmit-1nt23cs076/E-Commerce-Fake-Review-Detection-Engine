"""
Apache Airflow DAG: E-Commerce Fake Review & Bot Spam Detection Pipeline
Orchestrates batch ingestion, feature extraction, bot network detection,
ML forensic classification, quarantine, and audit summary generation.
"""

from datetime import datetime, timedelta
import json
from pathlib import Path

# Airflow imports with graceful standalone fallback for local execution
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    DAG = None
    PythonOperator = None

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.features import extract_review_features
from src.model import FakeReviewClassifier
from src.bot_detector import BotCampaignDetector
from src.db import init_db, insert_review, get_metrics_summary

default_args = {
    "owner": "fraud_detection_team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define task methods callable both in Airflow and in standalone Python runner
def task_ingest_raw_batch(**kwargs):
    """Task 1: Ingests incoming raw customer reviews batch."""
    print("▶ Starting Task 1: Ingesting raw reviews batch...")
    data_path = BASE_DIR / "data" / "sample_reviews.json"
    with open(data_path, "r", encoding="utf-8") as f:
        reviews = json.load(f)
    print(f"✔ Successfully loaded {len(reviews)} raw reviews.")
    return reviews

def task_extract_bot_signals(reviews=None, **kwargs):
    """Task 2: Detects coordinated duplicate reviews and temporal burst anomalies."""
    print("▶ Starting Task 2: Analyzing bot clusters & burst signals...")
    if reviews is None and kwargs.get("ti"):
        reviews = kwargs["ti"].xcom_pull(task_ids="ingest_raw_batch")

    detector = BotCampaignDetector(similarity_threshold=0.80)
    cluster_results = detector.detect_duplicate_clusters(reviews)
    burst_results = detector.detect_burst_anomalies(reviews)

    print(f"✔ Bot clusters detected: {len(cluster_results['duplicate_clusters'])}")
    print(f"✔ Burst anomalies identified: {len(burst_results)}")

    return {
        "reviews": reviews,
        "duplicate_review_ids": list(cluster_results["duplicate_review_ids"]),
        "duplicate_clusters": cluster_results["duplicate_clusters"],
        "burst_anomalies": burst_results
    }

def task_run_ml_classification(data=None, **kwargs):
    """Task 3: Executes ML model to compute fake probabilities and risk flags."""
    print("▶ Starting Task 3: Running ML forensic review classification...")
    if data is None and kwargs.get("ti"):
        data = kwargs["ti"].xcom_pull(task_ids="extract_bot_signals")

    reviews = data["reviews"]
    dup_ids = set(data["duplicate_review_ids"])

    classifier = FakeReviewClassifier()
    analyzed_reviews = []

    for r in reviews:
        is_dup = r.get("review_id") in dup_ids
        pred = classifier.predict_review(
            text=r.get("review_text", ""),
            rating=r.get("rating", 5),
            verified=r.get("verified_purchase", False),
            is_duplicate=is_dup
        )
        analyzed_reviews.append({
            "review": r,
            "detection": pred
        })

    print(f"✔ Classified {len(analyzed_reviews)} reviews.")
    return analyzed_reviews

def task_quarantine_and_persist(analyzed_reviews=None, **kwargs):
    """Task 4: Quarantines fake/bot reviews and persists records to the database."""
    print("▶ Starting Task 4: Quarantining suspicious reviews & updating database...")
    if analyzed_reviews is None and kwargs.get("ti"):
        analyzed_reviews = kwargs["ti"].xcom_pull(task_ids="run_ml_classification")

    init_db()
    quarantined_count = 0

    for item in analyzed_reviews:
        insert_review(item["review"], item["detection"])
        if item["detection"]["classification"] == "FAKE_BOT_SPAM":
            quarantined_count += 1

    print(f"✔ Updated database. Quarantined {quarantined_count} spam reviews.")
    return quarantined_count

def task_generate_audit_report(**kwargs):
    """Task 5: Generates daily fraud statistics and audit log."""
    print("▶ Starting Task 5: Generating executive fraud audit report...")
    metrics = get_metrics_summary()
    print("=" * 50)
    print("📊 FRAUD DETECTION PIPELINE AUDIT REPORT")
    print("=" * 50)
    print(f" Total Reviews Scanned : {metrics['total_reviews']}")
    print(f" Fake / Bot Spam Found : {metrics['fake_reviews']}")
    print(f" Suspicious Reviews    : {metrics['suspicious_reviews']}")
    print(f" Authentic Reviews     : {metrics['authentic_reviews']}")
    print(f" Quarantined Reviews   : {metrics['quarantined_reviews']}")
    print(f" Overall Fraud Rate    : {metrics['fraud_rate_pct']}%")
    print("=" * 50)
    return metrics

# Define Airflow DAG if running inside an Airflow environment
if AIRFLOW_AVAILABLE:
    with DAG(
        dag_id="ecommerce_fake_review_detection_pipeline",
        default_args=default_args,
        description="Daily automated ETL for E-Commerce fake review & bot spam detection",
        schedule_interval=timedelta(hours=6),
        start_date=datetime(2026, 1, 1),
        catchup=False,
        tags=["fraud-detection", "ecommerce", "nlp", "airflow"],
    ) as dag:

        t1 = PythonOperator(
            task_id="ingest_raw_batch",
            python_callable=task_ingest_raw_batch
        )

        t2 = PythonOperator(
            task_id="extract_bot_signals",
            python_callable=task_extract_bot_signals
        )

        t3 = PythonOperator(
            task_id="run_ml_classification",
            python_callable=task_run_ml_classification
        )

        t4 = PythonOperator(
            task_id="quarantine_and_persist",
            python_callable=task_quarantine_and_persist
        )

        t5 = PythonOperator(
            task_id="generate_audit_report",
            python_callable=task_generate_audit_report
        )

        # DAG Pipeline Flow
        t1 >> t2 >> t3 >> t4 >> t5

# Standalone execution helper
def run_pipeline_standalone():
    """Runs the 5-stage pipeline directly in Python without Airflow server."""
    print("🚀 Running E-Commerce Fake Review Pipeline in Standalone Mode...")
    reviews = task_ingest_raw_batch()
    bot_data = task_extract_bot_signals(reviews=reviews)
    analyzed = task_run_ml_classification(data=bot_data)
    task_quarantine_and_persist(analyzed_reviews=analyzed)
    report = task_generate_audit_report()
    return report

if __name__ == "__main__":
    run_pipeline_standalone()
