from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock


@dataclass
class InferenceCache:
    """Process-local cache ensuring model artifacts are loaded once."""

    bundle: object | None = None
    lock: Lock = field(default_factory=Lock)

    def get(self):
        return self.bundle

    def set(self, bundle: object) -> None:
        self.bundle = bundle


model_cache = InferenceCache()
