from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RecommendationConfig:
    reports_dir: Path
    max_candidates: int = 18
    top_k: int = 5
    max_batch_size: int = 50
    max_expense_reduction: float = 0.20
    max_inventory_reduction: float = 0.25
    max_loan_reduction: float = 0.15

    @classmethod
    def from_environment(cls) -> "RecommendationConfig":
        root = Path(__file__).resolve().parents[3]
        return cls(
            reports_dir=Path(
                os.getenv(
                    "GRAMNADI_RECOMMENDATION_REPORTS",
                    root / "backend/app/counterfactual/reports",
                )
            ),
            max_candidates=int(os.getenv("RECOMMENDATION_MAX_CANDIDATES", "18")),
            top_k=int(os.getenv("RECOMMENDATION_TOP_K", "5")),
            max_batch_size=int(os.getenv("RECOMMENDATION_MAX_BATCH_SIZE", "50")),
        )
