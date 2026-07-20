from __future__ import annotations

from pathlib import Path

import pandas as pd

from .utils import write_json


def export_predictions(predictions: dict[str, pd.DataFrame], reports_dir: Path) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in predictions.items():
        frame.to_csv(reports_dir / f"{name}_predictions.csv", index=False)


def export_confidence_summary(summary: dict, reports_dir: Path) -> None:
    write_json(reports_dir / "confidence_summary.json", summary)
