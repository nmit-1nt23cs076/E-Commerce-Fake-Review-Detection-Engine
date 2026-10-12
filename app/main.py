import sys
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.model import FakeReviewClassifier
from src.db import init_db, get_all_reviews, get_metrics_summary
from dags.fake_review_detection_dag import run_pipeline_standalone

app = FastAPI(
    title="E-Commerce Fake Review & Bot Spam Detection API",
    description="Production-grade Forensic NLP and Behavioral Fraud Engine for Product Reviews",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier = FakeReviewClassifier()
init_db()

class SingleReviewRequest(BaseModel):
    review_text: str
    rating: int = 5
    verified_purchase: bool = False
    is_duplicate: bool = False

@app.get("/api/health")
def health():
    return {"status": "online", "model": "NLP-Forensic-Ensemble-v1"}

@app.get("/api/metrics")
def get_metrics():
    return get_metrics_summary()

@app.get("/api/reviews")
def list_reviews(limit: int = 50):
    return {"reviews": get_all_reviews(limit=limit)}

@app.post("/api/detect")
def detect_single_review(req: SingleReviewRequest):
    if not req.review_text.strip():
        raise HTTPException(status_code=400, detail="Review text cannot be empty.")

    result = classifier.predict_review(
        text=req.review_text,
        rating=req.rating,
        verified=req.verified_purchase,
        is_duplicate=req.is_duplicate
    )
    return result

@app.post("/api/run-pipeline")
def trigger_pipeline():
    report = run_pipeline_standalone()
    return {
        "message": "Airflow batch detection pipeline executed successfully.",
        "audit_report": report
    }

# Mount static frontend
static_dir = BASE_DIR / "app" / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
