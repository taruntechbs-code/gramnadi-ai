from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd

from .loader import ModelBundle
from .validator import validate_features


class PreprocessingError(ValueError):
    """Raised when input cannot be transformed using Phase 3A artifacts."""


class InferencePreprocessor:
    def __init__(self, bundle: ModelBundle) -> None:
        self.bundle = bundle
        self.raw_feature_names = set(bundle.preprocessing["feature_columns"])
        self.model_feature_names = set(bundle.feature_names)
        self.encoder = bundle.preprocessing["encoder"]
        self.scaler = bundle.preprocessing["scaler"]
        self.allowed_fields = (
            self.raw_feature_names
            | self.model_feature_names
            | {
                "enterprise_id",
                "enterprise_code",
                "enterprise_name",
                "owner_name",
                "business_start_date",
                "month_date",
                "sector",
                "risk_score",
            }
        )

    def transform(self, features: dict[str, Any]) -> pd.DataFrame:
        mode = validate_features(
            features, self.allowed_fields, self.model_feature_names
        )
        if mode == "model_ready":
            frame = pd.DataFrame([features], columns=list(self.bundle.feature_names))
            return frame.astype(float)
        raw = pd.DataFrame([features])
        project_root = Path(__file__).resolve().parents[3]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from ml.feature_engineering.feature_builder import FeatureBuilder

        raw["month_date"] = pd.to_datetime(raw["month_date"])
        if "business_start_date" in raw:
            raw["business_start_date"] = pd.to_datetime(raw["business_start_date"])
        try:
            built = FeatureBuilder().build(raw).frame
            encoded = self.encoder.transform(
                built.loc[:, list(self.bundle.preprocessing["feature_columns"])]
            )
            transformed = self.scaler.transform(encoded)
            return transformed.loc[:, list(self.bundle.feature_names)].astype(float)
        except (KeyError, ValueError, TypeError) as exc:
            raise PreprocessingError(
                f"Unable to apply Phase 3A preprocessing: {exc}"
            ) from exc
