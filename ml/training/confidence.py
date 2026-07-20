from __future__ import annotations

import numpy as np


def regression_confidence(predictions, residuals):
    residual_scale = float(np.std(residuals))
    lower = predictions - 1.96 * residual_scale
    upper = predictions + 1.96 * residual_scale
    width = np.maximum(upper - lower, 1e-9)
    confidence = np.clip(
        1.0
        - np.abs(predictions - np.median(predictions)) / (width + np.abs(predictions)),
        0,
        1,
    )
    return {
        "confidence": confidence,
        "lower": lower,
        "upper": upper,
        "low_confidence": confidence < 0.5,
    }


def classification_confidence(probabilities):
    confidence = np.max(probabilities, axis=1)
    return {"confidence": confidence, "low_confidence": confidence < 0.6}
