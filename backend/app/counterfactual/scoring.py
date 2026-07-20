from __future__ import annotations


def score_candidate(
    simulation: dict, changes: dict, implementation_cost: float, difficulty: str
) -> float:
    improvement = max(float(simulation["cash_flow_difference"]), 0.0)
    risk_reduction = float(simulation["risk_reduction"]) * 10000
    complexity_penalty = len(changes) * 100
    difficulty_penalty = {"Low": 0, "Medium": 250, "High": 500}.get(difficulty, 500)
    return (
        improvement
        + risk_reduction
        - implementation_cost * 0.01
        - complexity_penalty
        - difficulty_penalty
    )
