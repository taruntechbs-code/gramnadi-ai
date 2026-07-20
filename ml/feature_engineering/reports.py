from __future__ import annotations

from pathlib import Path
from typing import Any

from ml.feature_engineering.utils import write_json


def write_processing_reports(
    reports_dir: Path,
    *,
    summary: dict[str, Any],
    config: dict[str, Any],
    feature_metadata: dict[str, Any],
    encoding_metadata: dict[str, Any],
    scaler_metadata: dict[str, Any],
) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    write_json(reports_dir / "processing_summary.json", summary)
    write_json(reports_dir / "pipeline_configuration.json", config)
    write_json(reports_dir / "feature_metadata.json", feature_metadata)
    write_json(reports_dir / "encoding_metadata.json", encoding_metadata)
    write_json(reports_dir / "scaler_metadata.json", scaler_metadata)
    log_lines = [
        "GramNadi AI Phase 3A feature engineering pipeline",
        f"Input: {config.get('input_path')}",
        f"Rows processed: {summary.get('input_rows')}",
        f"Final encoded features: {summary.get('encoded_feature_count')}",
        f"Scaling: {scaler_metadata.get('method')}",
        f"Runtime seconds: {summary.get('runtime_seconds')}",
        "Status: completed",
    ]
    (reports_dir / "processing_log.txt").write_text(
        "\n".join(log_lines) + "\n", encoding="utf-8"
    )
