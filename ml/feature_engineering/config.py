from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal

ScalingMethod = Literal["none", "standard", "minmax", "robust"]

TARGET_COLUMNS: Final[tuple[str, ...]] = (
    "cash_flow_after_1_month",
    "cash_flow_after_3_month",
    "cash_flow_after_6_month",
    "risk_score",
    "risk_level",
)

IDENTIFIER_COLUMNS: Final[tuple[str, ...]] = (
    "enterprise_id",
    "enterprise_code",
    "enterprise_name",
    "owner_name",
    "business_start_date",
    "month_date",
)

NON_FEATURE_COLUMNS: Final[tuple[str, ...]] = (
    *IDENTIFIER_COLUMNS,
    "risk_factors",
    *TARGET_COLUMNS,
)

EXPECTED_SECTORS: Final[frozenset[str]] = frozenset(
    {
        "Dairy",
        "Poultry",
        "Handicrafts",
        "Food Processing",
        "Rural Retail",
        "Fisheries",
        "Agriculture",
        "Weaving",
        "Goat Farming",
        "Beekeeping",
    }
)


@dataclass(frozen=True)
class FeatureEngineeringConfig:
    input_path: Path = Path("datasets/synthetic_rural_financial_data.parquet")
    output_dir: Path = Path("ml/processed")
    reports_dir: Path = Path("ml/feature_engineering/reports")
    source_format: Literal["auto", "csv", "parquet"] = "auto"
    scaling_method: ScalingMethod = "none"
    train_ratio: float = 0.70
    validation_ratio: float = 0.15
    test_ratio: float = 0.15
    seed: int = 42
    generate_reports: bool = True
    plot_distributions: bool = True
    rolling_windows: tuple[int, ...] = (3, 6, 12)
    drop_identifier_columns: bool = True
    target_columns: tuple[str, ...] = TARGET_COLUMNS
    categorical_columns: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not 0 < self.train_ratio < 1:
            raise ValueError("train_ratio must be between 0 and 1")
        if not 0 < self.validation_ratio < 1:
            raise ValueError("validation_ratio must be between 0 and 1")
        if not 0 < self.test_ratio < 1:
            raise ValueError("test_ratio must be between 0 and 1")
        if abs(self.train_ratio + self.validation_ratio + self.test_ratio - 1.0) > 1e-9:
            raise ValueError(
                "train_ratio, validation_ratio, and test_ratio must sum to 1"
            )
        if self.scaling_method not in {"none", "standard", "minmax", "robust"}:
            raise ValueError(f"unsupported scaling_method: {self.scaling_method}")
        if not self.rolling_windows or any(
            window <= 0 for window in self.rolling_windows
        ):
            raise ValueError("rolling_windows must contain positive integers")
        if not self.target_columns:
            raise ValueError("at least one target column is required")
