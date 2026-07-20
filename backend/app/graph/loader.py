from __future__ import annotations

from pathlib import Path

import pandas as pd


class GraphDataError(RuntimeError):
    """Raised when graph source data is unavailable or malformed."""


def load_latest_enterprise_snapshot(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise GraphDataError(f"Graph source dataset does not exist: {path}")
    frame = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
    required = {
        "enterprise_id",
        "sector",
        "village",
        "district",
        "month_date",
        "risk_score",
        "risk_level",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise GraphDataError(f"Graph source is missing columns: {', '.join(missing)}")
    frame["month_date"] = pd.to_datetime(frame["month_date"])
    return (
        frame.sort_values("month_date")
        .groupby("enterprise_id", as_index=False)
        .tail(1)
        .reset_index(drop=True)
    )
