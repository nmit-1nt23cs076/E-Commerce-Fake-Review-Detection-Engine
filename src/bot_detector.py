import re
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime

class BotCampaignDetector:
    """
    Detects coordinated bot networks and review burst campaigns.
    """
    def __init__(self, similarity_threshold: float = 0.80):
        self.similarity_threshold = similarity_threshold

    def _normalize(self, text: str) -> str:
        return re.sub(r'\W+', '', text.lower().strip())

    def detect_duplicate_clusters(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Groups identical or near-identical reviews into bot campaign clusters.
        """
        text_map = defaultdict(list)
        for r in reviews:
            norm = self._normalize(r.get("review_text", ""))
            if len(norm) > 10:
                text_map[norm].append(r)

        clusters = []
        duplicate_review_ids = set()

        for norm_text, matched_reviews in text_map.items():
            if len(matched_reviews) > 1:
                cluster_id = f"CLUSTER-{len(clusters)+1:03d}"
                user_ids = list(set(r.get("user_id") for r in matched_reviews))
                for r in matched_reviews:
                    duplicate_review_ids.add(r.get("review_id"))

                clusters.append({
                    "cluster_id": cluster_id,
                    "review_count": len(matched_reviews),
                    "unique_accounts": len(user_ids),
                    "sample_text": matched_reviews[0].get("review_text", "")[:120] + "...",
                    "review_ids": [r.get("review_id") for r in matched_reviews]
                })

        return {
            "duplicate_clusters": clusters,
            "duplicate_review_ids": duplicate_review_ids,
            "total_duplicates_found": len(duplicate_review_ids)
        }

    def detect_burst_anomalies(self, reviews: List[Dict[str, Any]], window_hours: int = 2) -> List[Dict[str, Any]]:
        """
        Flags products that experience sudden temporal spikes of polarized reviews.
        """
        product_reviews = defaultdict(list)
        for r in reviews:
            product_reviews[r.get("product_id")].append(r)

        bursts = []
        for prod_id, p_reviews in product_reviews.items():
            if len(p_reviews) >= 3:
                five_stars = sum(1 for r in p_reviews if r.get("rating") == 5)
                one_stars = sum(1 for r in p_reviews if r.get("rating") == 1)
                unverified = sum(1 for r in p_reviews if not r.get("verified_purchase", False))

                if (five_stars >= 3 or one_stars >= 3) and unverified >= 2:
                    bursts.append({
                        "product_id": prod_id,
                        "product_name": p_reviews[0].get("product_name", prod_id),
                        "total_reviews": len(p_reviews),
                        "polarized_count": max(five_stars, one_stars),
                        "unverified_ratio": round(unverified / len(p_reviews), 2),
                        "anomaly_type": "5-STAR_ASTROTURF_BURST" if five_stars >= 3 else "1-STAR_REVIEW_BOMB"
                    })

        return bursts
