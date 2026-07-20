from __future__ import annotations

from typing import Any

import numpy as np
import shap


def explain_prediction(
    model, vector, feature_names: list[str], prediction: float
) -> dict[str, Any]:
    """Return compact SHAP factors suitable for an API response."""
    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(vector)
    if isinstance(values, list):
        values = values[0]
    values = np.asarray(values)[0]
    return _explanation_from_values(
        values, vector, feature_names, prediction, explainer.expected_value
    )


def explain_batch(
    model, vectors, feature_names: list[str], predictions
) -> list[dict[str, Any]]:
    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(vectors)
    if isinstance(values, list):
        values = values[0]
    return [
        _explanation_from_values(
            values[index],
            vectors.iloc[[index]],
            feature_names,
            predictions[index],
            explainer.expected_value,
        )
        for index in range(len(vectors))
    ]


def _explanation_from_values(values, vector, feature_names, prediction, expected_value):
    values = np.asarray(values)
    if values.ndim > 1:
        values = values[0]
    if isinstance(expected_value, (list, np.ndarray)):
        expected_value = expected_value[0]
    ranked = np.argsort(np.abs(values))[::-1][:10]
    factors = [
        {
            "feature": feature_names[index],
            "shap_value": float(values[index]),
            "value": float(vector.iloc[0, index]),
        }
        for index in ranked
    ]
    positive = [item for item in factors if item["shap_value"] > 0]
    negative = [item for item in factors if item["shap_value"] < 0]
    return {
        "top_factors": factors,
        "top_positive_factors": positive[:5],
        "top_negative_factors": negative[:5],
        "summary": _summary(positive, negative, prediction),
    }


def _summary(positive: list[dict], negative: list[dict], prediction: float) -> str:
    if not positive and not negative:
        return (
            f"The model predicts cash flow of {prediction:.2f}; no dominant "
            "contributing factor was identified."
        )
    positive_text = ", ".join(item["feature"] for item in positive[:3]) or "none"
    negative_text = ", ".join(item["feature"] for item in negative[:3]) or "none"
    return (
        f"Cash flow is supported mainly by {positive_text} and reduced mainly "
        f"by {negative_text}."
    )
