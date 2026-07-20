from __future__ import annotations

import argparse
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import LabelEncoder

from .calibration import calibrate_classifier
from .classification import save_classification_plots, train_classifier
from .confidence import classification_confidence, regression_confidence
from .config import TrainingConfig
from .evaluation import (
    evaluate_classification,
    evaluate_regression,
    save_learning_curve,
)
from .explainability import generate_shap_explanations
from .export import export_confidence_summary, export_predictions
from .loader import TrainingData, TrainingDataLoader
from .registry import save_registry
from .regression import save_regression_plots, train_regressor
from .trainer import tune_classifier, tune_regressor
from .utils import configure_logging, json_safe, seed_everything, write_json

REGRESSION_TARGET = "future_cashflow_3m"
CLASSIFICATION_TARGET = "risk_label"
TARGET_ALIASES = {
    REGRESSION_TARGET: ("future_cashflow_3m", "cash_flow_after_3_month"),
    CLASSIFICATION_TARGET: ("risk_label", "risk_level"),
}
IDENTIFIER_COLUMNS = {
    "enterprise_id",
    "enterprise_code",
    "enterprise_name",
    "owner_name",
    "business_start_date",
    "month_date",
    "sector",
}
LEAKAGE_COLUMNS = {
    "cash_flow_after_1_month",
    "cash_flow_after_3_month",
    "cash_flow_after_6_month",
    "future_cashflow_3m",
    "risk_score",
    "risk_level",
    "risk_label",
    "risk_factors",
}


@dataclass
class TrainingResult:
    regression_metrics: dict
    classification_metrics: dict
    artifacts: dict[str, str]
    runtime_seconds: float


class TrainingPipeline:
    def __init__(self, config: TrainingConfig | None = None) -> None:
        self.config = config or TrainingConfig()

    def run(self) -> TrainingResult:
        started = time.perf_counter()
        config = self.config
        config.output_dir.mkdir(parents=True, exist_ok=True)
        config.reports_dir.mkdir(parents=True, exist_ok=True)
        logger = configure_logging(config.reports_dir / "training_log.txt")
        seed_everything(config.random_seed)
        logger.info("Loading Phase 3A processed datasets")
        data = TrainingDataLoader(config.processed_dir, config.input_format).load()
        targets = self._resolve_targets(data)
        features = self._select_features(data, targets)
        X_train, X_val, X_test = (
            frame.loc[:, features] for frame in (data.train, data.validation, data.test)
        )
        y_train_reg, y_val_reg, y_test_reg = (
            frame[targets[REGRESSION_TARGET]].astype(float)
            for frame in (data.train, data.validation, data.test)
        )
        y_train_cls, y_val_cls, y_test_cls = (
            frame[targets[CLASSIFICATION_TARGET]].astype(str)
            for frame in (data.train, data.validation, data.test)
        )
        logger.info("Training with %d features", len(features))

        reg_params = {
            **tune_regressor(X_train, y_train_reg, X_val, y_val_reg, config, logger),
            **config.regression_params,
        }
        reg_result = train_regressor(
            X_train,
            y_train_reg,
            X_val,
            y_val_reg,
            reg_params,
            config.random_seed,
            config.early_stopping_rounds,
        )
        reg_test_metrics, reg_test_pred = evaluate_regression(
            reg_result.model, X_test, y_test_reg
        )
        save_regression_plots(y_test_reg.to_numpy(), reg_test_pred, config.reports_dir)
        save_learning_curve(reg_result.model, config.reports_dir)
        reg_conf = regression_confidence(
            reg_test_pred, y_test_reg.to_numpy() - reg_test_pred
        )

        tuning_encoder = LabelEncoder().fit(y_train_cls)
        cls_params = {
            **tune_classifier(
                X_train,
                tuning_encoder.transform(y_train_cls),
                X_val,
                tuning_encoder.transform(y_val_cls),
                config,
                logger,
            ),
            **config.classification_params,
        }
        cls_result = train_classifier(
            X_train,
            y_train_cls,
            X_val,
            y_val_cls,
            cls_params,
            config.random_seed,
            config.early_stopping_rounds,
        )
        calibrated, calibration_method = calibrate_classifier(
            cls_result.model,
            X_val,
            y_val_cls,
            cls_result.label_encoder,
            config.calibration,
        )
        cls_test_metrics, cls_test_pred, cls_test_prob, cls_test_actual = (
            evaluate_classification(
                calibrated, cls_result.label_encoder, X_test, y_test_cls
            )
        )
        save_classification_plots(
            cls_test_actual,
            cls_test_pred,
            cls_test_prob,
            cls_result.label_encoder.classes_,
            config.reports_dir,
        )
        cls_conf = classification_confidence(cls_test_prob)

        if config.shap_enabled:
            shap_info = generate_shap_explanations(
                reg_result.model,
                X_test,
                config.reports_dir,
                config.shap_sample_size,
                config.random_seed,
            )
        else:
            shap_info = {"enabled": False}
        regression_model = {
            "model": reg_result.model,
            "target": REGRESSION_TARGET,
            "features": features,
        }
        classification_model = {
            "model": calibrated,
            "label_encoder": cls_result.label_encoder,
            "target": CLASSIFICATION_TARGET,
            "features": features,
            "calibration": calibration_method,
        }
        metrics = {
            "regression_validation": reg_result.metrics,
            "regression_test": reg_test_metrics,
            "classification_validation": cls_result.metrics,
            "classification_test": cls_test_metrics,
        }
        artifacts = save_registry(
            config.output_dir,
            regression_model,
            classification_model,
            {
                "features": features,
                "targets": targets,
                "phase3a_metadata": data.metadata,
            },
            asdict(config),
            metrics,
        )
        predictions = {
            "regression": pd.DataFrame(
                {
                    "actual": y_test_reg.to_numpy(),
                    "prediction": reg_test_pred,
                    "confidence": reg_conf["confidence"],
                    "interval_lower": reg_conf["lower"],
                    "interval_upper": reg_conf["upper"],
                    "low_confidence": reg_conf["low_confidence"],
                }
            ),
            "classification": pd.DataFrame(
                {
                    "actual": cls_result.label_encoder.inverse_transform(
                        cls_test_actual
                    ),
                    "prediction": cls_result.label_encoder.inverse_transform(
                        cls_test_pred
                    ),
                    "confidence": cls_conf["confidence"],
                    "low_confidence": cls_conf["low_confidence"],
                }
            ),
        }
        export_predictions(predictions, config.reports_dir)
        export_confidence_summary(
            {
                "regression_low_confidence": int(reg_conf["low_confidence"].sum()),
                "classification_low_confidence": int(cls_conf["low_confidence"].sum()),
            },
            config.reports_dir,
        )
        runtime = time.perf_counter() - started
        summary = {
            "status": "completed",
            "train_rows": len(data.train),
            "validation_rows": len(data.validation),
            "test_rows": len(data.test),
            "feature_count": len(features),
            "targets": targets,
            "calibration_method": calibration_method,
            "shap": shap_info,
            "regression_metrics": reg_test_metrics,
            "classification_metrics": cls_test_metrics,
            "runtime_seconds": round(runtime, 4),
            "artifacts": artifacts,
        }
        write_json(
            config.reports_dir / "regression_metrics.json",
            {"validation": reg_result.metrics, "test": reg_test_metrics},
        )
        write_json(
            config.reports_dir / "classification_metrics.json",
            {"validation": cls_result.metrics, "test": cls_test_metrics},
        )
        write_json(config.reports_dir / "training_summary.json", summary)
        write_json(config.reports_dir / "training_config.json", asdict(config))
        logger.info("Training complete in %.2f seconds", runtime)
        return TrainingResult(reg_test_metrics, cls_test_metrics, artifacts, runtime)

    @staticmethod
    def _resolve_targets(data: TrainingData) -> dict[str, str]:
        columns = set(data.train.columns)
        resolved = {}
        for requested, aliases in TARGET_ALIASES.items():
            match = next((alias for alias in aliases if alias in columns), None)
            if match is None:
                raise ValueError(f"Cannot resolve target {requested}; tried {aliases}")
            resolved[requested] = match
        return resolved

    @staticmethod
    def _select_features(data: TrainingData, targets: dict[str, str]) -> list[str]:
        target_columns = (
            set(targets.values())
            | set(TARGET_ALIASES[REGRESSION_TARGET])
            | set(TARGET_ALIASES[CLASSIFICATION_TARGET])
        )
        excluded = IDENTIFIER_COLUMNS | LEAKAGE_COLUMNS | target_columns
        features = []
        for column in data.feature_columns:
            if column in excluded:
                continue
            if all(
                pd.api.types.is_numeric_dtype(frame[column])
                for frame in (data.train, data.validation, data.test)
            ):
                features.append(column)
        if not features:
            raise ValueError(
                "No supported numeric features remain after leakage filtering"
            )
        return features


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run GramNadi AI Phase 3B model training"
    )
    parser.add_argument("--processed-dir", default="ml/processed")
    parser.add_argument("--output-dir", default="ml/models")
    parser.add_argument("--reports-dir", default="ml/training/reports")
    parser.add_argument(
        "--input-format", choices=("auto", "csv", "parquet"), default="auto"
    )
    parser.add_argument("--trials", type=int, default=25)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-shap", action="store_true")
    parser.add_argument(
        "--calibration", choices=("auto", "platt", "isotonic"), default="auto"
    )
    args = parser.parse_args()
    result = TrainingPipeline(
        TrainingConfig(
            processed_dir=Path(args.processed_dir),
            output_dir=Path(args.output_dir),
            reports_dir=Path(args.reports_dir),
            input_format=args.input_format,
            n_trials=args.trials,
            random_seed=args.seed,
            shap_enabled=not args.no_shap,
            calibration=args.calibration,
        )
    ).run()
    print(
        json_safe(
            {
                "status": "completed",
                "regression_metrics": result.regression_metrics,
                "classification_metrics": result.classification_metrics,
                "runtime_seconds": result.runtime_seconds,
                "artifacts": result.artifacts,
            }
        )
    )
