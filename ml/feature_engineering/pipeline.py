from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from ml.feature_engineering.config import IDENTIFIER_COLUMNS, FeatureEngineeringConfig
from ml.feature_engineering.encoder import FeatureEncoder
from ml.feature_engineering.export import export_splits
from ml.feature_engineering.feature_builder import FeatureBuilder
from ml.feature_engineering.loader import DatasetLoader
from ml.feature_engineering.profiler import profile_dataset
from ml.feature_engineering.reports import write_processing_reports
from ml.feature_engineering.scaler import FeatureScaler
from ml.feature_engineering.splitter import TimeAwareSplitter
from ml.feature_engineering.utils import json_safe, write_json
from ml.feature_engineering.validator import (
    assess_feature_quality,
    require_valid,
    validate_dataset,
)


@dataclass(frozen=True)
class PipelineResult:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame
    input_rows: int
    input_columns: int
    added_features: tuple[str, ...]
    feature_columns: tuple[str, ...]
    encoded_feature_columns: tuple[str, ...]
    target_columns: tuple[str, ...]
    artifacts: dict[str, Path]
    runtime_seconds: float


class FeatureEngineeringPipeline:
    """Execute the Phase 3A load-to-export transformation."""

    def __init__(self, config: FeatureEngineeringConfig | None = None) -> None:
        self.config = config or FeatureEngineeringConfig()

    def run(self) -> PipelineResult:
        started = time.perf_counter()
        reports_dir = Path(self.config.reports_dir)
        reports_dir.mkdir(parents=True, exist_ok=True)
        frame = DatasetLoader(self.config.input_path, self.config.source_format).load()
        validation = validate_dataset(frame)
        write_json(reports_dir / "validation_report.json", validation.report)
        require_valid(validation)
        profile_dataset(
            frame,
            reports_dir,
            self.config.target_columns,
            generate_plots=self.config.generate_reports
            and self.config.plot_distributions,
        )

        built = FeatureBuilder(self.config.rolling_windows).build(frame)
        feature_columns = self._select_feature_columns(
            built.frame, built.leakage_columns
        )
        quality_report = assess_feature_quality(
            built.frame, feature_columns, built.leakage_columns
        )
        write_json(reports_dir / "feature_quality_report.json", quality_report)

        time_split = TimeAwareSplitter(
            self.config.train_ratio,
            self.config.validation_ratio,
            self.config.test_ratio,
        ).split(built.frame)
        raw_splits = {
            "train": time_split.train,
            "validation": time_split.validation,
            "test": time_split.test,
        }
        categorical_columns = self._categorical_columns(
            raw_splits["train"], feature_columns
        )
        encoder = FeatureEncoder(categorical_columns)
        encoded_train = encoder.fit_transform(raw_splits["train"][feature_columns])
        encoded_validation = encoder.transform(
            raw_splits["validation"][feature_columns]
        )
        encoded_test = encoder.transform(raw_splits["test"][feature_columns])
        encoder_path = Path(self.config.output_dir) / "encoder.pkl"
        encoder.save(encoder_path)
        write_json(reports_dir / "encoding_metadata.json", encoder.metadata())

        scaler = FeatureScaler(self.config.scaling_method)
        scaled_train = scaler.fit_transform(encoded_train)
        scaled_validation = scaler.transform(encoded_validation)
        scaled_test = scaler.transform(encoded_test)
        scaler_path = Path(self.config.output_dir) / "scaler.pkl"
        scaler.save(scaler_path)
        write_json(reports_dir / "scaler_metadata.json", scaler.metadata())

        output_splits = {
            "train": self._assemble_output(raw_splits["train"], scaled_train),
            "validation": self._assemble_output(
                raw_splits["validation"], scaled_validation
            ),
            "test": self._assemble_output(raw_splits["test"], scaled_test),
        }
        feature_metadata = self._feature_metadata(
            frame,
            built,
            feature_columns,
            encoder,
            scaler,
            time_split.boundaries,
        )
        artifacts = export_splits(output_splits, self.config, feature_metadata)
        artifacts["encoder"] = encoder_path
        if scaler.scaler is not None:
            artifacts["scaler"] = scaler_path
        pipeline_artifact_path = (
            Path(self.config.output_dir) / "pipeline_artifact.joblib"
        )
        pipeline_artifact = {
            "config": json_safe(asdict(self.config)),
            "feature_columns": feature_columns,
            "target_columns": list(self.config.target_columns),
            "categorical_columns": categorical_columns,
            "encoder": encoder,
            "scaler": scaler,
            "split_boundaries": time_split.boundaries,
        }
        pipeline_artifact_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline_artifact, pipeline_artifact_path)
        artifacts["pipeline_artifact"] = pipeline_artifact_path

        runtime = time.perf_counter() - started
        summary = {
            "status": "completed",
            "input_rows": int(len(frame)),
            "input_columns": int(frame.shape[1]),
            "engineered_features_added": len(built.added_features),
            "engineered_feature_names": list(built.added_features),
            "raw_feature_count": len(feature_columns),
            "encoded_feature_count": len(encoder.feature_names),
            "final_feature_count": len(encoder.feature_names),
            "target_columns": list(self.config.target_columns),
            "split_rows": {
                name: int(len(value)) for name, value in output_splits.items()
            },
            "split_boundaries": time_split.boundaries,
            "runtime_seconds": round(runtime, 4),
            "artifacts": {key: str(value) for key, value in artifacts.items()},
        }
        write_processing_reports(
            reports_dir,
            summary=summary,
            config=asdict(self.config),
            feature_metadata=feature_metadata,
            encoding_metadata=encoder.metadata(),
            scaler_metadata=scaler.metadata(),
        )
        return PipelineResult(
            train=output_splits["train"],
            validation=output_splits["validation"],
            test=output_splits["test"],
            input_rows=len(frame),
            input_columns=frame.shape[1],
            added_features=built.added_features,
            feature_columns=tuple(feature_columns),
            encoded_feature_columns=tuple(encoder.feature_names),
            target_columns=self.config.target_columns,
            artifacts=artifacts,
            runtime_seconds=runtime,
        )

    def _select_feature_columns(
        self, frame: pd.DataFrame, leakage_columns: tuple[str, ...]
    ) -> list[str]:
        excluded = set(leakage_columns)
        if self.config.drop_identifier_columns:
            excluded.update(IDENTIFIER_COLUMNS)
        excluded.add("risk_factors")
        return [column for column in frame.columns if column not in excluded]

    def _categorical_columns(
        self, frame: pd.DataFrame, feature_columns: list[str]
    ) -> list[str]:
        configured = set(self.config.categorical_columns)
        automatic = set(
            frame[feature_columns].select_dtypes(include=["object", "category"]).columns
        )
        return sorted((configured | automatic) & set(feature_columns))

    def _assemble_output(
        self, raw_split: pd.DataFrame, transformed_features: pd.DataFrame
    ) -> pd.DataFrame:
        metadata_columns = [
            column
            for column in ("enterprise_id", "month_date", "enterprise_code", "sector")
            if column in raw_split.columns
        ]
        target_columns = [
            column
            for column in self.config.target_columns
            if column in raw_split.columns
        ]
        output = pd.concat(
            [
                raw_split[metadata_columns].reset_index(drop=True),
                transformed_features.reset_index(drop=True),
                raw_split[target_columns].reset_index(drop=True),
            ],
            axis=1,
        )
        return output

    def _feature_metadata(
        self,
        frame: pd.DataFrame,
        built: Any,
        feature_columns: list[str],
        encoder: FeatureEncoder,
        scaler: FeatureScaler,
        boundaries: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "source_columns": list(frame.columns),
            "engineered_features_added": list(built.added_features),
            "excluded_leakage_columns": list(built.leakage_columns),
            "raw_feature_columns": feature_columns,
            "categorical_columns": encoder.categorical_columns,
            "numeric_columns": encoder.numeric_columns,
            "encoded_feature_columns": encoder.feature_names,
            "target_columns": list(self.config.target_columns),
            "scaling": scaler.metadata(),
            "time_split_boundaries": boundaries,
        }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run GramNadi AI Phase 3A feature engineering."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("datasets/synthetic_rural_financial_data.parquet"),
    )
    parser.add_argument(
        "--input-format", choices=("auto", "csv", "parquet"), default="auto"
    )
    parser.add_argument("--output-dir", type=Path, default=Path("ml/processed"))
    parser.add_argument(
        "--reports-dir", type=Path, default=Path("ml/feature_engineering/reports")
    )
    parser.add_argument(
        "--scaling", choices=("none", "standard", "minmax", "robust"), default="none"
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-reports", action="store_true")
    parser.add_argument("--no-plots", action="store_true")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    config = FeatureEngineeringConfig(
        input_path=args.input,
        source_format=args.input_format,
        output_dir=args.output_dir,
        reports_dir=args.reports_dir,
        scaling_method=args.scaling,
        seed=args.seed,
        generate_reports=not args.no_reports,
        plot_distributions=not args.no_plots,
    )
    result = FeatureEngineeringPipeline(config).run()
    print(
        json.dumps(
            {
                "status": "completed",
                "input_rows": result.input_rows,
                "input_columns": result.input_columns,
                "engineered_features_added": len(result.added_features),
                "final_feature_count": len(result.encoded_feature_columns),
                "split_rows": {
                    "train": len(result.train),
                    "validation": len(result.validation),
                    "test": len(result.test),
                },
                "runtime_seconds": round(result.runtime_seconds, 4),
                "artifacts": {
                    key: str(value) for key, value in result.artifacts.items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
