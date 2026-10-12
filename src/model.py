from typing import Dict, Any, List
from src.features import extract_review_features

class FakeReviewClassifier:
    """
    Forensic Fake Review & Bot Spam Detection Engine.
    Combines rule-based behavioral heuristics with NLP linguistic signals.
    """
    def __init__(self, fake_threshold: float = 0.65, suspicious_threshold: float = 0.45):
        self.fake_threshold = fake_threshold
        self.suspicious_threshold = suspicious_threshold

    def predict_review(self, text: str, rating: int, verified: bool = False, is_duplicate: bool = False) -> Dict[str, Any]:
        features = extract_review_features(text, rating, verified)
        flags = []
        score = 0.0

        # 1. Duplicate / Copy-Paste Spam Flag
        if is_duplicate:
            score += 0.55
            flags.append("Identical / Near-duplicate review detected across multiple accounts")

        # 2. Capitalization & Shouting
        if features["caps_ratio"] > 0.35:
            score += 0.25
            flags.append(f"Excessive capitalization ({int(features['caps_ratio']*100)}% uppercase)")
        elif features["caps_ratio"] > 0.20:
            score += 0.12
            flags.append("Elevated uppercase character frequency")

        # 3. Exclamation and Punctuation Density
        if features["exclamation_count"] >= 3:
            score += 0.20
            flags.append(f"Excessive exclamation marks ({features['exclamation_count']} exclamation points)")

        # 4. Exaggerated Superlatives & Promotional Buzzwords
        if features["superlative_count"] >= 2:
            score += 0.30
            flags.append(f"Multiple promotional buzzwords ({', '.join(features['superlative_matches'])})")
        elif features["superlative_count"] == 1:
            score += 0.15
            flags.append(f"Promotional claim detected ('{features['superlative_matches'][0]}')")

        # 5. Low Word Count / Shallow Reviews
        if features["num_words"] < 12 and (rating == 5 or rating == 1):
            score += 0.15
            flags.append("Extremely short review paired with polarized rating (1 or 5 stars)")

        # 6. Unverified Purchase Penalty
        if not verified:
            score += 0.10
            flags.append("Unverified buyer status")

        # 7. Sentiment vs Rating Mismatch
        if features["sentiment_conflict"]:
            score += 0.25
            flags.append("Sharp conflict between star rating and emotional sentiment")

        # 8. Low Lexical Diversity (Repetitive phrasing)
        if features["lexical_diversity"] < 0.65 and features["num_words"] > 15:
            score += 0.15
            flags.append("Low vocabulary diversity (highly repetitive phrasing)")

        # Normalize score between 0.0 and 1.0
        fake_probability = min(1.0, round(score, 3))
        authenticity_score = round(1.0 - fake_probability, 3)

        if fake_probability >= self.fake_threshold:
            classification = "FAKE_BOT_SPAM"
            severity = "HIGH"
        elif fake_probability >= self.suspicious_threshold:
            classification = "SUSPICIOUS"
            severity = "MEDIUM"
        else:
            classification = "AUTHENTIC"
            severity = "LOW"

        return {
            "classification": classification,
            "severity": severity,
            "fake_probability": fake_probability,
            "authenticity_score": authenticity_score,
            "risk_flags": flags,
            "features": features
        }
