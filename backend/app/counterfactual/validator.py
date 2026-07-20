from __future__ import annotations

from typing import Any

from .constraints import validate_scenario


def validate_request(features: dict[str, Any], model_features: set[str]) -> None:
    missing = sorted(model_features - set(features))
    if missing:
        raise ValueError(f"Missing model features: {', '.join(missing[:10])}")
    invalid = [
        name
        for name in model_features
        if not isinstance(features[name], (int, float))
        or isinstance(features[name], bool)
    ]
    if invalid:
        raise ValueError(f"Features must be numeric: {', '.join(invalid[:10])}")
    result = validate_scenario(features, features)
    if not result.valid:
        raise ValueError("; ".join(result.reasons))
