from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd


class DatasetLoadError(RuntimeError):
    """Raised when the Phase 2 dataset cannot be loaded."""


class DatasetLoader:
    def __init__(
        self,
        input_path: Path,
        source_format: Literal["auto", "csv", "parquet"] = "auto",
    ) -> None:
        self.input_path = Path(input_path)
        self.source_format = source_format

    def load(self) -> pd.DataFrame:
        path = self._resolve_path()
        try:
            if path.suffix.lower() == ".csv":
                frame = pd.read_csv(path)
            elif path.suffix.lower() in {".parquet", ".pq"}:
                frame = pd.read_parquet(path)
            else:
                raise DatasetLoadError(
                    f"Unsupported dataset format '{path.suffix}' for {path}"
                )
        except DatasetLoadError:
            raise
        except Exception as exc:
            raise DatasetLoadError(
                f"Failed to load dataset from {path}: {exc}"
            ) from exc
        if frame.empty:
            raise DatasetLoadError(f"Dataset is empty: {path}")
        return self._normalize(frame)

    def _resolve_path(self) -> Path:
        if self.input_path.is_file():
            path = self.input_path
        elif self.input_path.is_dir():
            candidates = (
                ("parquet", self.input_path / "synthetic_rural_financial_data.parquet"),
                ("csv", self.input_path / "synthetic_rural_financial_data.csv"),
            )
            path = next(
                (
                    candidate
                    for format_name, candidate in candidates
                    if candidate.exists()
                    and (
                        self.source_format == "auto"
                        or self.source_format == format_name
                    )
                ),
                None,
            )
            if path is None:
                raise DatasetLoadError(
                    f"No compatible CSV or Parquet dataset found in {self.input_path}"
                )
        else:
            raise DatasetLoadError(f"Dataset path does not exist: {self.input_path}")
        if self.source_format != "auto":
            expected_suffix = f".{self.source_format}"
            if path.suffix.lower() != expected_suffix:
                raise DatasetLoadError(
                    f"Expected {self.source_format} input, received "
                    f"{path.suffix}: {path}"
                )
        return path

    @staticmethod
    def _normalize(frame: pd.DataFrame) -> pd.DataFrame:
        normalized = frame.copy()
        for column in ("month_date", "business_start_date"):
            if column in normalized.columns:
                normalized[column] = pd.to_datetime(normalized[column], errors="coerce")
        return normalized
