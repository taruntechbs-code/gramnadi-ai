from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import RecommendationConfig


@dataclass(frozen=True)
class Candidate:
    action: str
    changes: dict[str, float]
    implementation_cost: float
    difficulty: str


class CandidateGenerator:
    """Creates bounded, interpretable scenarios from available features."""

    def __init__(self, config: RecommendationConfig | None = None) -> None:
        self.config = config or RecommendationConfig.from_environment()

    def generate(self, features: dict[str, Any]) -> list[Candidate]:
        candidates: list[Candidate] = []
        if "expense" in features:
            for reduction in (0.05, 0.10, self.config.max_expense_reduction):
                delta = float(features["expense"]) * reduction
                expense = float(features["expense"]) - delta
                changes = {"expense": expense}
                if "income" in features:
                    changes.update(
                        {
                            "profit": float(features.get("profit", 0)) + delta,
                            "net_cash_flow": float(features.get("net_cash_flow", 0))
                            + delta,
                            "savings": float(features.get("savings", 0)) + delta,
                            "cash_balance": float(features.get("cash_balance", 0))
                            + delta,
                            "expense_ratio": expense
                            / max(float(features["income"]), 1),
                            "profit_margin": (float(features.get("profit", 0)) + delta)
                            / max(float(features["income"]), 1),
                        }
                    )
                candidates.append(
                    Candidate(
                        f"Reduce monthly expenses by {reduction:.0%}",
                        changes,
                        delta,
                        "Low",
                    )
                )
        if "inventory_value" in features:
            for reduction in (0.10, 0.20, self.config.max_inventory_reduction):
                inventory = float(features["inventory_value"]) * (1 - reduction)
                changes = {"inventory_value": inventory}
                if "expense" in features:
                    changes["inventory_turnover_proxy"] = float(
                        features["expense"]
                    ) / max(inventory, 1)
                candidates.append(
                    Candidate(
                        f"Reduce inventory holding by {reduction:.0%}",
                        changes,
                        float(features["inventory_value"]) * reduction * 0.05,
                        "Low",
                    )
                )
        if "outstanding_loan" in features:
            for reduction in (0.05, 0.10, self.config.max_loan_reduction):
                loan = float(features["outstanding_loan"]) * (1 - reduction)
                changes = {"outstanding_loan": loan}
                if "income" in features:
                    changes["loan_to_income_ratio"] = loan / max(
                        float(features["income"]), 1
                    )
                if "principal_amount" in features:
                    changes["credit_utilization_proxy"] = loan / max(
                        float(features["principal_amount"]), 1
                    )
                candidates.append(
                    Candidate(
                        f"Reduce outstanding loan burden by {reduction:.0%}",
                        changes,
                        float(features["outstanding_loan"]) * reduction,
                        "Medium",
                    )
                )
        if "commodity_price_pressure" in features:
            candidates.append(
                Candidate(
                    "Diversify commodity sourcing to reduce price pressure",
                    {
                        "commodity_price_pressure": float(
                            features["commodity_price_pressure"]
                        )
                        * 0.90
                    },
                    float(features["commodity_price_pressure"]) * 0.10,
                    "Medium",
                )
            )
        if "savings" in features:
            candidates.append(
                Candidate(
                    "Build a 10% emergency reserve from savings",
                    {
                        "savings": float(features["savings"]) * 0.90,
                        "cash_balance": float(features.get("cash_balance", 0))
                        + float(features["savings"]) * 0.10,
                    },
                    float(features["savings"]) * 0.10,
                    "Low",
                )
            )
        return candidates[: self.config.max_candidates]
