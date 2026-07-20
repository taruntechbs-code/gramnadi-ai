from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


class TrainingDataError(ValueError):
    """Raised when Phase 3A outputs cannot be loaded consistently."""


@dataclass(frozen=True)
class TrainingData:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame
    feature_columns: tuple[str, ...]
    metadata: dict


class TrainingDataLoader:
    def __init__(self, processed_dir: Path, input_format: str = "auto") -> None:
        self.processed_dir = Path(processed_dir)
        self.input_format = input_format

    def load(self) -> TrainingData:
        metadata_path = self.processed_dir / "feature_metadata.json"
        if not metadata_path.exists():
            raise TrainingDataError(f"Missing Phase 3A metadata: {metadata_path}")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        feature_columns = tuple(metadata.get("encoded_feature_columns", []))
        if not feature_columns:
            raise TrainingDataError("Phase 3A metadata contains no feature columns")
        frames = {
            split: self._read_split(split) for split in ("train", "validation", "test")
        }
        missing = {
            split: sorted(set(feature_columns) - set(frame.columns))
            for split, frame in frames.items()
        }
        if any(missing.values()):
            raise TrainingDataError(f"Feature mismatch in Phase 3A outputs: {missing}")
        signatures = [
            tuple(frame.loc[:, feature_columns].columns) for frame in frames.values()
        ]
        if len(set(signatures)) != 1:
            raise TrainingDataError("Train, validation, and test feature order differs")
        return TrainingData(
            frames["train"],
            frames["validation"],
            frames["test"],
            feature_columns,
            metadata,
        )

    def _read_split(self, split: str) -> pd.DataFrame:
        candidates = (
            (self.processed_dir / f"{split}.parquet", "parquet"),
            (self.processed_dir / f"{split}.csv", "csv"),
        )
        if self.input_format == "csv":
            candidates = (candidates[1],)
        elif self.input_format == "parquet":
            candidates = (candidates[0],)
        for path, fmt in candidates:
            if path.exists():
                return pd.read_parquet(path) if fmt == "parquet" else pd.read_csv(path)
        raise TrainingDataError(f"Missing {split} split in {self.processed_dir}")
