from __future__ import annotations

import logging
from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from app.graph.risk_propagation import propagate_risk
from app.graph.similarity import similar_enterprises
from app.ml.predictor import Predictor

from .cache import recommendation_cache
from .candidate_generator import CandidateGenerator
from .config import RecommendationConfig
from .constraints import validate_scenario
from .recommendation import format_recommendation
from .scoring import score_candidate
from .simulator import simulate
from .utils import write_json
from .validator import validate_request

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Searches bounded scenarios using the existing inference and graph services."""

    def __init__(
        self,
        predictor: Predictor,
        graph_service,
        config: RecommendationConfig | None = None,
    ) -> None:
        self.predictor = predictor
        self.graph_service = graph_service
        self.config = config or RecommendationConfig.from_environment()
        self.generator = CandidateGenerator(self.config)

    def recommend(
        self, enterprise_id: str | None, features: dict[str, Any]
    ) -> dict[str, Any]:
        started = perf_counter()
        validate_request(features, set(self.predictor.feature_names))
        current = self.predictor.predict(features, enterprise_id)
        graph_evidence = self._graph_evidence(enterprise_id)
        recommendations = []
        for candidate in self.generator.generate(features):
            scenario = dict(features)
            scenario.update(candidate.changes)
            constraint = validate_scenario(features, scenario)
            if not constraint.valid:
                continue
            prediction = self._predict_fast(scenario)
            simulation = simulate(
                features, scenario, current, prediction, graph_evidence
            )
            if (
                simulation["cash_flow_difference"] <= 0
                and simulation["risk_reduction"] <= 0
            ):
                continue
            explanation = self._explanation(
                candidate.action, simulation, graph_evidence
            )
            score = score_candidate(
                simulation,
                candidate.changes,
                candidate.implementation_cost,
                candidate.difficulty,
            )
            recommendations.append(
                format_recommendation(candidate, simulation, score, explanation)
            )
        recommendations.sort(key=lambda item: item["score"], reverse=True)
        result = {
            "enterprise_id": enterprise_id,
            "current_prediction": current,
            "recommendations": recommendations[: self.config.top_k],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "latency_ms": (perf_counter() - started) * 1000,
        }
        if enterprise_id:
            for item in result["recommendations"]:
                recommendation_cache.add(enterprise_id, item)
        self._write_reports(result)
        return result

    def _predict_fast(self, features: dict[str, Any]) -> dict[str, Any]:
        """Evaluate candidates without repeating SHAP computation."""
        vector = self.predictor.preprocessor.transform(features)
        regression = self.predictor.bundle.regression["model"]
        classification = self.predictor.bundle.classification["model"]
        cash_flow = float(regression.predict(vector)[0])
        probabilities = classification.predict_proba(vector)[0]
        class_index = int(probabilities.argmax())
        encoder = self.predictor.bundle.classification["label_encoder"]
        risk_label = str(encoder.inverse_transform([class_index])[0])
        confidence = float(probabilities.max())
        return {
            "cash_flow_prediction": cash_flow,
            "risk_prediction": risk_label,
            "confidence": {
                "score": confidence,
                "level": (
                    "High"
                    if confidence >= 0.8
                    else "Medium" if confidence >= 0.6 else "Low"
                ),
                "low_confidence": confidence < 0.6,
            },
        }

    def _graph_evidence(self, enterprise_id: str | None) -> dict:
        if not enterprise_id or not self.graph_service.loaded:
            return {"available": False}
        graph = self.graph_service.require_graph()
        node = f"enterprise:{enterprise_id}"
        attrs = dict(graph.nodes[node]) if node in graph else {}
        return {
            "available": bool(attrs),
            "neighbor_risk": (
                propagate_risk(graph, enterprise_id, 0.1, 2) if attrs else {}
            ),
            "similar_enterprises": (
                similar_enterprises(graph, enterprise_id, 3) if attrs else []
            ),
            "community_id": attrs.get("community_id"),
            "village": attrs.get("village"),
        }

    @staticmethod
    def _explanation(action: str, simulation: dict, evidence: dict) -> str:
        graph_text = (
            " Similar enterprises and the surrounding risk neighborhood were "
            "included in the confidence assessment."
            if evidence.get("available")
            else " Graph evidence was unavailable for this enterprise."
        )
        return (
            f"{action} changes the modeled financial inputs and improves "
            f"projected cash flow by {simulation['cash_flow_difference']:.2f}."
            + graph_text
        )

    def _write_reports(self, result: dict) -> None:
        self.config.reports_dir.mkdir(parents=True, exist_ok=True)
        write_json(self.config.reports_dir / "recommendation_summary.json", result)
        write_json(
            self.config.reports_dir / "recommendation_metrics.json",
            {
                "recommendations_generated": len(result["recommendations"]),
                "average_cash_flow_improvement": sum(
                    item["expected_result"]["cash_flow_improvement"]
                    for item in result["recommendations"]
                )
                / max(len(result["recommendations"]), 1),
                "average_risk_reduction": sum(
                    item["expected_result"]["risk_reduction"]
                    for item in result["recommendations"]
                )
                / max(len(result["recommendations"]), 1),
            },
        )
        import csv

        with (self.config.reports_dir / "simulation_results.csv").open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            fields = [
                "recommendation",
                "cash_flow_improvement",
                "risk_reduction",
                "score",
            ]
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(
                {
                    field: (
                        item["recommendation"]
                        if field == "recommendation"
                        else item["expected_result"].get(field, item.get(field))
                    )
                    for field in fields
                }
                for item in result["recommendations"]
            )
        (self.config.reports_dir / "recommendation_log.txt").write_text(
            f"Generated {len(result['recommendations'])} recommendations in "
            f"{result['latency_ms']:.2f} ms\n",
            encoding="utf-8",
        )
