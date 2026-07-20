from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

Scaling = Literal["none"]
Calibration = Literal["auto", "platt", "isotonic"]


@dataclass
class TrainingConfig:
    processed_dir: Path = Path("ml/processed")
    output_dir: Path = Path("ml/models")
    reports_dir: Path = Path("ml/training/reports")
    input_format: Literal["auto", "csv", "parquet"] = "auto"
    random_seed: int = 42
    n_trials: int = 25
    early_stopping_rounds: int = 50
    shap_enabled: bool = True
    shap_sample_size: int = 1000
    calibration: Calibration = "auto"
    n_jobs: int = 4
    regression_params: dict = field(default_factory=dict)
    classification_params: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.n_trials < 0:
            raise ValueError("n_trials must be non-negative")
        if self.shap_sample_size < 1:
            raise ValueError("shap_sample_size must be positive")
