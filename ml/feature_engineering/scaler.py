from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

from ml.feature_engineering.config import ScalingMethod


class FeatureScaler:
    """Optional numeric scaler fitted only on the chronological train split."""

    def __init__(self, method: ScalingMethod) -> None:
        self.method = method
        self.scaler = self._make_scaler(method)
        self.feature_names: list[str] = []

    @staticmethod
    def _make_scaler(method: ScalingMethod) -> Any:
        if method == "standard":
            return StandardScaler()
        if method == "minmax":
            return MinMaxScaler()
        if method == "robust":
            return RobustScaler()
        return None

    def fit(self, frame: pd.DataFrame) -> "FeatureScaler":
        self.feature_names = list(frame.columns)
        if self.scaler is not None:
            self.scaler.fit(frame[self.feature_names])
        return self

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        if self.scaler is None:
            return frame.copy()
        transformed = self.scaler.transform(frame[self.feature_names])
        return pd.DataFrame(transformed, index=frame.index, columns=self.feature_names)

    def fit_transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        return self.fit(frame).transform(frame)

    def save(self, path: Path) -> None:
        if self.scaler is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    def metadata(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "enabled": self.scaler is not None,
            "feature_count": len(self.feature_names),
            "fit_scope": "chronological training split only",
        }
