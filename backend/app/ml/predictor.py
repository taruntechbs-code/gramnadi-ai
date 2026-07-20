from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

from .confidence import classification_confidence, regression_confidence
from .config import MLConfig
from .explain import explain_batch, explain_prediction
from .loader import ModelBundle
from .preprocess import InferencePreprocessor

logger = logging.getLogger(__name__)


class Predictor:
    def __init__(self, bundle: ModelBundle, config: MLConfig | None = None) -> None:
        self.bundle = bundle
        self.config = config or MLConfig.from_environment()
        self.preprocessor = InferencePreprocessor(bundle)
        self.feature_names = list(bundle.feature_names)

    def predict(
        self, features: dict[str, Any], enterprise_id: str | None = None
    ) -> dict[str, Any]:
        started = time.perf_counter()
        vector = self.preprocessor.transform(features)
        regression = self.bundle.regression["model"]
        classification = self.bundle.classification["model"]
        cash_flow = float(regression.predict(vector)[0])
        probabilities = classification.predict_proba(vector)[0]
        class_index = int(np.argmax(probabilities))
        encoder = self.bundle.classification["label_encoder"]
        risk_label = str(encoder.inverse_transform([class_index])[0])
        residual_scale = float(
            self.bundle.regression["model"].get_booster().feature_names is not None
        ) * max(abs(cash_flow) * 0.25, 1.0)
        interval_lower, interval_upper = (
            cash_flow - residual_scale,
            cash_flow + residual_scale,
        )
        risk_confidence = classification_confidence(
            probabilities, self.config.confidence_medium, self.config.confidence_high
        )
        cash_confidence = regression_confidence(
            cash_flow,
            interval_lower,
            interval_upper,
            self.config.confidence_medium,
            self.config.confidence_high,
        )
        explanation = (
            explain_prediction(regression, vector, self.feature_names, cash_flow)
            if self.config.shap_enabled
            else {
                "top_factors": [],
                "top_positive_factors": [],
                "top_negative_factors": [],
                "summary": "Explainability is disabled.",
            }
        )
        latency_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "Inference completed enterprise_id=%s latency_ms=%.2f",
            enterprise_id,
            latency_ms,
        )
        return {
            "enterprise_id": enterprise_id,
            "cash_flow_prediction": cash_flow,
            "risk_prediction": risk_label,
            "risk_probability": {
                str(label): float(probabilities[index])
                for index, label in enumerate(encoder.classes_)
            },
            "confidence": {
                "score": risk_confidence["score"],
                "level": risk_confidence["level"],
                "low_confidence": risk_confidence["low_confidence"],
            },
            "cash_flow_confidence": cash_confidence,
            "prediction_interval": {"lower": interval_lower, "upper": interval_upper},
            "top_factors": explanation["top_factors"],
            "explanation": explanation,
            "model": {
                "version": self.bundle.model_versions.get("version", "unknown"),
                "trained_on": self.bundle.model_versions.get("created_at"),
                "feature_count": len(self.feature_names),
            },
            "inference_timestamp": datetime.now(timezone.utc).isoformat(),
            "latency_ms": latency_ms,
        }

    def predict_batch(
        self, items: list[tuple[str | None, dict[str, Any]]]
    ) -> list[dict[str, Any]]:
        started = time.perf_counter()
        vectors = [self.preprocessor.transform(features) for _, features in items]
        matrix = pd.concat(vectors, ignore_index=True)
        regression = self.bundle.regression["model"]
        classification = self.bundle.classification["model"]
        cash_flows = regression.predict(matrix)
        probabilities = classification.predict_proba(matrix)
        encoder = self.bundle.classification["label_encoder"]
        explanations = (
            explain_batch(regression, matrix, self.feature_names, cash_flows)
            if self.config.shap_enabled
            else [
                {
                    "top_factors": [],
                    "top_positive_factors": [],
                    "top_negative_factors": [],
                    "summary": "Explainability is disabled.",
                }
            ]
            * len(items)
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        results = []
        for index, (enterprise_id, _) in enumerate(items):
            cash_flow = float(cash_flows[index])
            class_index = int(np.argmax(probabilities[index]))
            risk_label = str(encoder.inverse_transform([class_index])[0])
            interval = max(abs(cash_flow) * 0.25, 1.0)
            risk_confidence = classification_confidence(
                probabilities[index],
                self.config.confidence_medium,
                self.config.confidence_high,
            )
            cash_confidence = regression_confidence(
                cash_flow,
                cash_flow - interval,
                cash_flow + interval,
                self.config.confidence_medium,
                self.config.confidence_high,
            )
            results.append(
                {
                    "enterprise_id": enterprise_id,
                    "cash_flow_prediction": cash_flow,
                    "risk_prediction": risk_label,
                    "risk_probability": {
                        str(label): float(probabilities[index, label_index])
                        for label_index, label in enumerate(encoder.classes_)
                    },
                    "confidence": risk_confidence,
                    "cash_flow_confidence": cash_confidence,
                    "prediction_interval": {
                        "lower": cash_flow - interval,
                        "upper": cash_flow + interval,
                    },
                    "top_factors": explanations[index]["top_factors"],
                    "explanation": explanations[index],
                    "model": {
                        "version": self.bundle.model_versions.get("version", "unknown"),
                        "trained_on": self.bundle.model_versions.get("created_at"),
                        "feature_count": len(self.feature_names),
                    },
                    "inference_timestamp": datetime.now(timezone.utc).isoformat(),
                    "latency_ms": elapsed_ms / len(items),
                }
            )
        logger.info(
            "Batch inference completed count=%d latency_ms=%.2f", len(items), elapsed_ms
        )
        return results
