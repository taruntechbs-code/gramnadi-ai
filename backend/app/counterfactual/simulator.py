from __future__ import annotations

from typing import Any


def simulate(
    original: dict[str, Any],
    counterfactual: dict[str, Any],
    original_prediction: dict,
    new_prediction: dict,
    graph_evidence: dict,
) -> dict:
    original_cash = float(original_prediction["cash_flow_prediction"])
    new_cash = float(new_prediction["cash_flow_prediction"])
    old_risk = original_prediction["risk_prediction"]
    new_risk = new_prediction["risk_prediction"]
    risk_order = {"high": 2, "medium": 1, "low": 0}
    return {
        "original_prediction": original_cash,
        "new_prediction": new_cash,
        "cash_flow_difference": new_cash - original_cash,
        "risk_before": old_risk,
        "risk_after": new_risk,
        "risk_reduction": max(
            0, risk_order.get(old_risk, 0) - risk_order.get(new_risk, 0)
        ),
        "confidence": new_prediction["confidence"],
        "graph_evidence": graph_evidence,
    }
