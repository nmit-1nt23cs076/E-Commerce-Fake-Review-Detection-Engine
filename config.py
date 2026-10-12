import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "fake_reviews.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Fake Review Thresholds
FAKE_PROBABILITY_THRESHOLD = float(os.getenv("FAKE_THRESHOLD", "0.65"))
SUSPICIOUS_PROBABILITY_THRESHOLD = float(os.getenv("SUSPICIOUS_THRESHOLD", "0.45"))
BOT_BURST_WINDOW_HOURS = int(os.getenv("BURST_WINDOW_HOURS", "2"))
BOT_SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.75"))

# Server
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "127.0.0.1")
