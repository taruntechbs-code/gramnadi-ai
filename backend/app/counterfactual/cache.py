from __future__ import annotations

from threading import Lock


class RecommendationCache:
    def __init__(self) -> None:
        self.history: dict[str, list[dict]] = {}
        self.lock = Lock()

    def add(self, enterprise_id: str, recommendation: dict) -> None:
        with self.lock:
            self.history.setdefault(enterprise_id, []).append(recommendation)

    def get(self, enterprise_id: str) -> list[dict]:
        with self.lock:
            return list(self.history.get(enterprise_id, []))


recommendation_cache = RecommendationCache()
