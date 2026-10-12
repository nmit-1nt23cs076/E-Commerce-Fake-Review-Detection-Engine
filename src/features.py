import re
from typing import Dict, Any, List

SUPERLATIVES = {
    "miracle", "changed my life", "best ever", "must buy", "100%", "a+++++", 
    "life changing", "overnight", "unbelievable", "best product", "scam", 
    "terrible", "worst ever", "fake", "refund", "in the universe"
}

POSITIVE_LEXICON = {
    "good", "great", "excellent", "amazing", "love", "wonderful", "fantastic",
    "awesome", "best", "perfect", "crisp", "solid", "comfortable", "effective"
}

NEGATIVE_LEXICON = {
    "bad", "terrible", "awful", "worst", "broken", "scam", "cheap", "hate",
    "useless", "broke", "defective", "leaky", "horrible", "refund"
}

def extract_review_features(text: str, rating: int, verified: bool = False) -> Dict[str, Any]:
    text_clean = text.strip()
    words = re.findall(r'\b\w+\b', text_clean.lower())
    num_words = max(1, len(words))
    num_chars = max(1, len(text_clean))

    # Linguistic & Stylistic Features
    caps_count = sum(1 for c in text_clean if c.isupper())
    caps_ratio = round(caps_count / num_chars, 4)
    
    exclamation_count = text_clean.count("!")
    question_count = text_clean.count("?")
    punct_density = round((exclamation_count + question_count) / num_words, 4)

    # Lexical Diversity (Type-Token Ratio)
    unique_words = len(set(words))
    lexical_diversity = round(unique_words / num_words, 4)

    # Superlatives / Promotional Language Count
    text_lower = text_clean.lower()
    superlative_matches = [s for s in SUPERLATIVES if s in text_lower]

    # Heuristic Sentiment Scoring
    pos_count = sum(1 for w in words if w in POSITIVE_LEXICON)
    neg_count = sum(1 for w in words if w in NEGATIVE_LEXICON)
    sentiment_score = (pos_count - neg_count) / max(1, (pos_count + neg_count))

    # Rating vs Sentiment Inconsistency
    sentiment_conflict = False
    if rating >= 4 and neg_count > pos_count * 2:
        sentiment_conflict = True
    elif rating <= 2 and pos_count > neg_count * 2:
        sentiment_conflict = True

    return {
        "num_words": num_words,
        "num_chars": num_chars,
        "caps_ratio": caps_ratio,
        "exclamation_count": exclamation_count,
        "punct_density": punct_density,
        "lexical_diversity": lexical_diversity,
        "superlative_count": len(superlative_matches),
        "superlative_matches": superlative_matches,
        "sentiment_score": round(sentiment_score, 3),
        "sentiment_conflict": sentiment_conflict,
        "verified_purchase": verified
    }
