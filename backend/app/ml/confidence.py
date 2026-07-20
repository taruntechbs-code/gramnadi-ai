from __future__ import annotations

import numpy as np


def confidence_level(score: float, medium: float = 0.60, high: float = 0.80) -> str:
    if score >= high:
        return "High"
    if score >= medium:
        return "Medium"
    return "Low"


def classification_confidence(probabilities, medium: float, high: float) -> dict:
    score = float(np.max(probabilities))
    return {
        "score": score,
        "level": confidence_level(score, medium, high),
        "low_confidence": score < medium,
    }


def regression_confidence(
    prediction: float,
    interval_lower: float,
    interval_upper: float,
    medium: float,
    high: float,
) -> dict:
    width = max(interval_upper - interval_lower, 1e-9)
    score = float(np.clip(1.0 - width / (abs(prediction) + width), 0.0, 1.0))
    return {
        "score": score,
        "level": confidence_level(score, medium, high),
        "low_confidence": score < medium,
    }
