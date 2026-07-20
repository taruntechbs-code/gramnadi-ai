from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConstraintResult:
    valid: bool
    reasons: tuple[str, ...] = ()


NON_NEGATIVE = {
    "expense",
    "inventory_value",
    "outstanding_loan",
    "savings",
    "cash_balance",
    "monthly_installment",
    "principal_amount",
    "income",
    "annual_turnover",
}


def validate_scenario(
    original: dict[str, Any], scenario: dict[str, Any]
) -> ConstraintResult:
    reasons = []
    for field in NON_NEGATIVE:
        if field in scenario and float(scenario[field]) < 0:
            reasons.append(f"{field} cannot be negative")
    if "temperature" in scenario and not -50 <= float(scenario["temperature"]) <= 70:
        reasons.append("temperature is outside the physical range")
    if "rainfall" in scenario and not 0 <= float(scenario["rainfall"]) <= 5000:
        reasons.append("rainfall is outside the physical range")
    if {"outstanding_loan", "principal_amount"} <= set(scenario) and scenario[
        "outstanding_loan"
    ] > scenario["principal_amount"]:
        reasons.append("outstanding loan exceeds principal")
    if "income" in original and "income" in scenario:
        baseline = max(abs(float(original["income"])), 1.0)
        if abs(float(scenario["income"]) - float(original["income"])) / baseline > 0.20:
            reasons.append("income change exceeds the realism limit")
    return ConstraintResult(not reasons, tuple(reasons))
