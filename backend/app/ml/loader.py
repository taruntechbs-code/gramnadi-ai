from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib

from .cache import model_cache
from .config import MLConfig

logger = logging.getLogger(__name__)


class ModelLoadError(RuntimeError):
    """Raised when the immutable Phase 3B artifacts cannot be loaded."""


@dataclass(frozen=True)
class ModelBundle:
    regression: dict[str, Any]
    classification: dict[str, Any]
    feature_metadata: dict[str, Any]
    training_config: dict[str, Any]
    model_versions: dict[str, Any]
    preprocessing: dict[str, Any]

    @property
    def feature_names(self) -> tuple[str, ...]:
        return tuple(self.regression["features"])


class ModelLoader:
    """Loads and validates all model artifacts once per application process."""

    def __init__(self, config: MLConfig | None = None) -> None:
        self.config = config or MLConfig.from_environment()
        self._bundle: ModelBundle | None = model_cache.get()
        self._error: str | None = None

    @property
    def loaded(self) -> bool:
        return self._bundle is not None

    @property
    def error(self) -> str | None:
        return self._error

    def load(self) -> ModelBundle:
        if self._bundle is not None:
            return self._bundle
        with model_cache.lock:
            if self._bundle is not None:
                return self._bundle
            try:
                self._bundle = self._load_from_disk()
                model_cache.set(self._bundle)
                logger.info(
                    "Phase 3B models loaded once from %s", self.config.model_dir
                )
                return self._bundle
            except Exception as exc:
                self._error = str(exc)
                logger.exception("Unable to load Phase 3B model artifacts")
                raise ModelLoadError(self._error) from exc

    def require_loaded(self) -> ModelBundle:
        if self._bundle is None:
            raise ModelLoadError(self._error or "Models are not loaded")
        return self._bundle

    def _load_from_disk(self) -> ModelBundle:
        project_root = Path(__file__).resolve().parents[3]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        directory = self.config.model_dir
        required = [
            "regression_model.pkl",
            "classification_model.pkl",
            "feature_metadata.json",
            "training_config.json",
            "model_versions.json",
        ]
        missing = [name for name in required if not (directory / name).exists()]
        if missing:
            raise ModelLoadError(f"Missing model artifacts: {', '.join(missing)}")
        regression = joblib.load(directory / "regression_model.pkl")
        classification = joblib.load(directory / "classification_model.pkl")
        feature_metadata = self._read_json(directory / "feature_metadata.json")
        training_config = self._read_json(directory / "training_config.json")
        model_versions = self._read_json(directory / "model_versions.json")
        preprocessing_path = self.config.processed_dir / "pipeline_artifact.joblib"
        if not preprocessing_path.exists():
            raise ModelLoadError(
                f"Missing Phase 3A preprocessing artifact: {preprocessing_path}"
            )
        preprocessing = joblib.load(preprocessing_path)
        self._validate(regression, classification, feature_metadata, preprocessing)
        return ModelBundle(
            regression,
            classification,
            feature_metadata,
            training_config,
            model_versions,
            preprocessing,
        )

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ModelLoadError(f"Corrupted JSON artifact: {path}: {exc}") from exc

    @staticmethod
    def _validate(regression, classification, feature_metadata, preprocessing) -> None:
        if not isinstance(regression, dict) or not callable(
            getattr(regression.get("model"), "predict", None)
        ):
            raise ModelLoadError("Regression artifact does not contain a usable model")
        if not isinstance(classification, dict) or not callable(
            getattr(classification.get("model"), "predict_proba", None)
        ):
            raise ModelLoadError(
                "Classification artifact does not contain a usable model"
            )
        regression_features = tuple(regression.get("features", ()))
        classification_features = tuple(classification.get("features", ()))
        metadata_features = tuple(feature_metadata.get("features", regression_features))
        if not regression_features or regression_features != classification_features:
            raise ModelLoadError(
                "Regression and classification feature ordering mismatch"
            )
        if metadata_features != regression_features:
            raise ModelLoadError(
                "Model feature metadata does not match model artifacts"
            )
        if tuple(preprocessing.get("encoder").feature_names) != regression_features:
            raise ModelLoadError("Phase 3A encoder feature ordering mismatch")
