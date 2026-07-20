from __future__ import annotations

from datetime import datetime
from typing import Any

EXPECTED_SECTORS = {
    "Agriculture",
    "Dairy",
    "Poultry",
    "Goat Farming",
    "Fisheries",
    "Handicrafts",
    "Weaving",
    "Rural Retail",
    "Food Processing",
    "Beekeeping",
}
NON_NEGATIVE_FIELDS = {
    "income",
    "expense",
    "savings",
    "cash_balance",
    "inventory_value",
    "upi_transaction_count",
    "upi_inflow",
    "upi_outflow",
    "principal_amount",
    "monthly_installment",
    "outstanding_loan",
    "rainfall",
    "humidity",
    "employees",
    "annual_turnover",
}


class InputValidationError(ValueError):
    """Raised when inference input violates the model contract."""


def validate_features(
    features: dict[str, Any], allowed: set[str], model_features: set[str]
) -> str:
    unknown = sorted(set(features) - allowed)
    if unknown:
        raise InputValidationError(f"Unexpected fields: {', '.join(unknown[:10])}")
    if model_features <= set(features):
        _validate_model_ready(features, model_features)
        return "model_ready"
    _validate_raw(features)
    return "raw"


def _validate_model_ready(features: dict[str, Any], model_features: set[str]) -> None:
    for name in model_features:
        value = features.get(name)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputValidationError(f"Feature '{name}' must be numeric")
        if name in NON_NEGATIVE_FIELDS and float(value) < 0:
            raise InputValidationError(f"{name} cannot be negative")
    if "rainfall" in features and not 0 <= float(features["rainfall"]) <= 5000:
        raise InputValidationError("rainfall must be between 0 and 5000")
    if "temperature" in features and not -50 <= float(features["temperature"]) <= 70:
        raise InputValidationError("temperature must be between -50 and 70 Celsius")


def _validate_raw(features: dict[str, Any]) -> None:
    required = {
        "enterprise_id",
        "month_date",
        "sector",
        "income",
        "expense",
        "profit",
        "net_cash_flow",
    }
    missing = sorted(required - set(features))
    if missing:
        raise InputValidationError(f"Missing required fields: {', '.join(missing)}")
    if features["sector"] not in EXPECTED_SECTORS:
        raise InputValidationError(f"Invalid sector: {features['sector']}")
    try:
        datetime.fromisoformat(str(features["month_date"]).replace("Z", "+00:00"))
    except ValueError as exc:
        raise InputValidationError("month_date must be a valid ISO timestamp") from exc
    for field in NON_NEGATIVE_FIELDS:
        if field in features and float(features[field]) < 0:
            raise InputValidationError(f"{field} cannot be negative")
    if float(features["profit"]) != float(features["income"]) - float(
        features["expense"]
    ):
        raise InputValidationError(
            "Financial consistency error: profit must equal income minus expense"
        )
    if "rainfall" in features and not 0 <= float(features["rainfall"]) <= 5000:
        raise InputValidationError("rainfall must be between 0 and 5000")
    if "temperature" in features and not -50 <= float(features["temperature"]) <= 70:
        raise InputValidationError("temperature must be between -50 and 70 Celsius")
    if (
        "outstanding_loan" in features
        and "principal_amount" in features
        and float(features["outstanding_loan"]) > float(features["principal_amount"])
    ):
        raise InputValidationError("outstanding_loan cannot exceed principal_amount")
