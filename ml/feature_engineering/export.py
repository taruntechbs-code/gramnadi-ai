from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from ml.feature_engineering.config import FeatureEngineeringConfig
from ml.feature_engineering.utils import write_json


def export_splits(
    splits: dict[str, pd.DataFrame],
    config: FeatureEngineeringConfig,
    feature_metadata: dict[str, Any],
) -> dict[str, Path]:
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, Path] = {}
    for split_name, frame in splits.items():
        csv_path = output_dir / f"{split_name}.csv"
        parquet_path = output_dir / f"{split_name}.parquet"
        frame.to_csv(csv_path, index=False)
        frame.to_parquet(parquet_path, index=False)
        artifacts[f"{split_name}_csv"] = csv_path
        artifacts[f"{split_name}_parquet"] = parquet_path
    feature_metadata_path = output_dir / "feature_metadata.json"
    write_json(feature_metadata_path, feature_metadata)
    artifacts["feature_metadata"] = feature_metadata_path
    return artifacts
