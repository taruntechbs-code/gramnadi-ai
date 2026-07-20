from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MLConfig:
    """Runtime configuration for model inference."""

    model_dir: Path
    processed_dir: Path
    confidence_medium: float = 0.60
    confidence_high: float = 0.80
    max_batch_size: int = 1000
    shap_enabled: bool = True

    @classmethod
    def from_environment(cls) -> "MLConfig":
        root = Path(__file__).resolve().parents[3]
        model_dir = Path(os.getenv("GRAMNADI_MODEL_DIR", str(root / "ml/models")))
        processed_dir = Path(
            os.getenv("GRAMNADI_PROCESSED_DIR", str(root / "ml/processed"))
        )
        return cls(
            model_dir=model_dir,
            processed_dir=processed_dir,
            confidence_medium=float(os.getenv("ML_CONFIDENCE_MEDIUM", "0.60")),
            confidence_high=float(os.getenv("ML_CONFIDENCE_HIGH", "0.80")),
            max_batch_size=int(os.getenv("ML_MAX_BATCH_SIZE", "1000")),
            shap_enabled=os.getenv("ML_SHAP_ENABLED", "true").lower() == "true",
        )
