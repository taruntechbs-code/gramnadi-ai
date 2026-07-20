from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import joblib

from .utils import write_json


def save_registry(
    output_dir: Path,
    regression_model,
    classification_model,
    metadata: dict,
    config: dict,
    metrics: dict,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "regression_model": output_dir / "regression_model.pkl",
        "classification_model": output_dir / "classification_model.pkl",
        "regression_model_joblib": output_dir / "regression_model.joblib",
        "classification_model_joblib": output_dir / "classification_model.joblib",
        "feature_metadata": output_dir / "feature_metadata.json",
        "training_config": output_dir / "training_config.json",
        "metrics": output_dir / "metrics.json",
        "model_versions": output_dir / "model_versions.json",
    }
    joblib.dump(regression_model, paths["regression_model"])
    joblib.dump(regression_model, paths["regression_model_joblib"])
    joblib.dump(classification_model, paths["classification_model"])
    joblib.dump(classification_model, paths["classification_model_joblib"])
    write_json(paths["feature_metadata"], metadata)
    write_json(paths["training_config"], config)
    write_json(paths["metrics"], metrics)
    write_json(
        paths["model_versions"],
        {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "format": "joblib/pickle",
            "version": "3B.1",
        },
    )
    return {key: str(path) for key, path in paths.items()}
