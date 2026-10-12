import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        review_id TEXT PRIMARY KEY,
        product_id TEXT,
        product_name TEXT,
        user_id TEXT,
        rating INTEGER,
        review_text TEXT,
        verified_purchase BOOLEAN,
        timestamp TEXT,
        classification TEXT,
        severity TEXT,
        fake_probability REAL,
        authenticity_score REAL,
        risk_flags TEXT,
        is_quarantined BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_runs (
        run_id TEXT PRIMARY KEY,
        timestamp TEXT,
        total_scanned INTEGER,
        flagged_fake INTEGER,
        flagged_suspicious INTEGER,
        bot_clusters_detected INTEGER,
        quarantine_action_count INTEGER
    );
    """)

    conn.commit()
    conn.close()

def insert_review(review_data: Dict[str, Any], detection: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO reviews (
        review_id, product_id, product_name, user_id, rating,
        review_text, verified_purchase, timestamp, classification,
        severity, fake_probability, authenticity_score, risk_flags,
        is_quarantined
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        review_data.get("review_id"),
        review_data.get("product_id"),
        review_data.get("product_name"),
        review_data.get("user_id"),
        review_data.get("rating"),
        review_data.get("review_text"),
        review_data.get("verified_purchase", False),
        review_data.get("timestamp"),
        detection.get("classification"),
        detection.get("severity"),
        detection.get("fake_probability"),
        detection.get("authenticity_score"),
        json.dumps(detection.get("risk_flags", [])),
        1 if detection.get("classification") == "FAKE_BOT_SPAM" else 0
    ))

    conn.commit()
    conn.close()

def get_all_reviews(limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reviews ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    results = []
    for r in rows:
        d = dict(r)
        d["risk_flags"] = json.loads(d["risk_flags"]) if d["risk_flags"] else []
        results.append(d)
    conn.close()
    return results

def get_metrics_summary() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM reviews")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reviews WHERE classification = 'FAKE_BOT_SPAM'")
    fake = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reviews WHERE classification = 'SUSPICIOUS'")
    suspicious = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reviews WHERE classification = 'AUTHENTIC'")
    authentic = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reviews WHERE is_quarantined = 1")
    quarantined = cursor.fetchone()[0]

    conn.close()
    return {
        "total_reviews": total,
        "fake_reviews": fake,
        "suspicious_reviews": suspicious,
        "authentic_reviews": authentic,
        "quarantined_reviews": quarantined,
        "fraud_rate_pct": round((fake / max(1, total)) * 100, 1)
    }
