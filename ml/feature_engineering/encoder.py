from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder


class FeatureEncoder:
    """Fits nominal-category encoding on training data only."""

    def __init__(self, categorical_columns: list[str]) -> None:
        self.categorical_columns = categorical_columns
        self.numeric_columns: list[str] = []
        self.numeric_imputer = SimpleImputer(strategy="median")
        self.categorical_imputer = SimpleImputer(strategy="most_frequent")
        try:
            self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        except TypeError:
            self.encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)
        self.feature_names: list[str] = []

    def fit(self, frame: pd.DataFrame) -> "FeatureEncoder":
        self.numeric_columns = [
            column for column in frame.columns if column not in self.categorical_columns
        ]
        if self.numeric_columns:
            self.numeric_imputer.fit(frame[self.numeric_columns])
        if self.categorical_columns:
            categories = self.categorical_imputer.fit_transform(
                frame[self.categorical_columns]
            )
            self.encoder.fit(categories)
        self.feature_names = self._feature_names()
        return self

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        parts: list[pd.DataFrame] = []
        if self.numeric_columns:
            numeric = self.numeric_imputer.transform(frame[self.numeric_columns])
            parts.append(
                pd.DataFrame(numeric, index=frame.index, columns=self.numeric_columns)
            )
        if self.categorical_columns:
            categorical = self.categorical_imputer.transform(
                frame[self.categorical_columns]
            )
            encoded = self.encoder.transform(categorical)
            names = list(self.encoder.get_feature_names_out(self.categorical_columns))
            parts.append(pd.DataFrame(encoded, index=frame.index, columns=names))
        if not parts:
            raise ValueError("No feature columns available for encoding")
        return pd.concat(parts, axis=1).astype(float)

    def fit_transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        return self.fit(frame).transform(frame)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    def metadata(self) -> dict[str, Any]:
        return {
            "categorical_columns": self.categorical_columns,
            "numeric_columns": self.numeric_columns,
            "encoded_feature_count": len(self.feature_names),
            "encoded_feature_names": self.feature_names,
            "handle_unknown": "ignore",
            "fit_scope": "chronological training split only",
        }

    def _feature_names(self) -> list[str]:
        if not self.categorical_columns:
            return list(self.numeric_columns)
        return self.numeric_columns + list(
            self.encoder.get_feature_names_out(self.categorical_columns)
        )
