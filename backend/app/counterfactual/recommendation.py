from __future__ import annotations

from typing import Any


def format_recommendation(
    candidate, simulation: dict, score: float, explanation: str
) -> dict[str, Any]:
    return {
        "recommendation": candidate.action,
        "changes": candidate.changes,
        "expected_result": {
            "cash_flow_before": simulation["original_prediction"],
            "cash_flow_after": simulation["new_prediction"],
            "cash_flow_improvement": simulation["cash_flow_difference"],
            "risk_before": simulation["risk_before"],
            "risk_after": simulation["risk_after"],
            "risk_reduction": simulation["risk_reduction"],
        },
        "confidence": simulation["confidence"],
        "implementation_difficulty": candidate.difficulty,
        "implementation_cost": candidate.implementation_cost,
        "score": score,
        "why_it_works": explanation,
        "graph_evidence": simulation["graph_evidence"],
    }
