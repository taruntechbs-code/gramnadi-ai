from __future__ import annotations

from datetime import datetime, timezone
from itertools import combinations
from typing import Any

import networkx as nx
import pandas as pd

from .config import GraphConfig
from .loader import load_latest_enterprise_snapshot

COMMODITY_COLUMNS = (
    "milk_price",
    "feed_price",
    "grains_price",
    "vegetables_price",
    "fish_feed_price",
    "fuel_price",
    "electricity_price",
)


class GraphBuilder:
    """Build a weighted property graph from the existing Phase 2 panel."""

    def __init__(self, config: GraphConfig | None = None) -> None:
        self.config = config or GraphConfig.from_environment()

    def build(self) -> nx.Graph:
        snapshot = load_latest_enterprise_snapshot(self.config.data_path)
        graph = nx.Graph(name="GramNadi Village Economic Knowledge Graph")
        self._add_reference_nodes(graph, snapshot)
        self._add_enterprises(graph, snapshot)
        self._add_relationships(graph, snapshot)
        graph.graph.update(
            {
                "built_at": datetime.now(timezone.utc).isoformat(),
                "source_rows": int(len(snapshot)),
                "source_path": str(self.config.data_path),
            }
        )
        return graph

    @staticmethod
    def _add_reference_nodes(graph: nx.Graph, frame: pd.DataFrame) -> None:
        for village, group in frame.groupby("village"):
            node = f"village:{village}"
            graph.add_node(
                node,
                node_type="Village",
                name=village,
                district=str(group.iloc[0]["district"]),
                state=str(group.iloc[0]["state"]),
                enterprise_count=int(len(group)),
                average_risk=float(group["risk_score"].mean()),
            )
        for district, group in frame.groupby("district"):
            graph.add_node(
                f"weather:{district}",
                node_type="Weather Region",
                name=district,
                rainfall=float(group["rainfall"].mean()),
                temperature=float(group["temperature"].mean()),
                anomaly=float(group.get("rainfall_anomaly", pd.Series([0])).mean()),
            )
        for column in COMMODITY_COLUMNS:
            if column in frame:
                graph.add_node(
                    f"commodity:{column}",
                    node_type="Commodity",
                    name=column,
                    price=float(frame[column].mean()),
                    volatility=float(frame[column].std() or 0),
                )
        for loan_type, group in frame.groupby("loan_type"):
            graph.add_node(
                f"loan:{loan_type}",
                node_type="Loan Cluster",
                name=loan_type,
                enterprise_count=int(len(group)),
                average_outstanding_loan=float(group["outstanding_loan"].mean()),
            )
        for risk_level, group in frame.groupby("risk_level"):
            graph.add_node(
                f"risk:{risk_level}",
                node_type="Risk Cluster",
                name=risk_level,
                average_risk=float(group["risk_score"].mean()),
                severity=str(risk_level),
            )

    @staticmethod
    def _add_enterprises(graph: nx.Graph, frame: pd.DataFrame) -> None:
        for row in frame.to_dict("records"):
            enterprise = f"enterprise:{row['enterprise_id']}"
            graph.add_node(
                enterprise,
                node_type="Enterprise",
                enterprise_id=str(row["enterprise_id"]),
                sector=str(row["sector"]),
                village=str(row["village"]),
                revenue=float(row["income"]),
                expenses=float(row["expense"]),
                cash_flow=float(row["net_cash_flow"]),
                risk_score=float(row["risk_score"]),
                risk_label=str(row["risk_level"]),
                loan_amount=float(row["outstanding_loan"]),
                inventory=float(row["inventory_value"]),
                commodity_pressure=float(row["commodity_price_pressure"]),
                rainfall=float(row["rainfall"]),
                temperature=float(row["temperature"]),
                month_date=row["month_date"],
            )

    def _add_relationships(self, graph: nx.Graph, frame: pd.DataFrame) -> None:
        for row in frame.to_dict("records"):
            enterprise = f"enterprise:{row['enterprise_id']}"
            village = f"village:{row['village']}"
            weather = f"weather:{row['district']}"
            risk = f"risk:{row['risk_level']}"
            graph.add_edge(
                enterprise,
                village,
                relationship_type="Located In",
                relationship_types=["Located In"],
                direction="undirected",
                weight=1.0,
                confidence=1.0,
                timestamp=row["month_date"],
            )
            graph.add_edge(
                enterprise,
                weather,
                relationship_type="Affected By",
                relationship_types=["Affected By", "Shares Weather"],
                direction="undirected",
                weight=float(abs(row["weather_shock_index"]) + 1),
                confidence=0.9,
                timestamp=row["month_date"],
            )
            graph.add_edge(
                enterprise,
                risk,
                relationship_type="Risk Cluster",
                relationship_types=["Risk Cluster"],
                direction="undirected",
                weight=float(row["risk_score"] / 100),
                confidence=1.0,
                timestamp=row["month_date"],
            )
            loan = f"loan:{row['loan_type']}"
            if loan in graph:
                graph.add_edge(
                    enterprise,
                    loan,
                    relationship_type="Financial Dependency",
                    relationship_types=["Financial Dependency"],
                    direction="undirected",
                    weight=float(row["outstanding_loan"] / max(row["income"], 1)),
                    confidence=0.95,
                    timestamp=row["month_date"],
                )
            for column in COMMODITY_COLUMNS:
                commodity_node = f"commodity:{column}"
                if commodity_node in graph and float(row[column]) > 0:
                    graph.add_edge(
                        enterprise,
                        commodity_node,
                        relationship_type="Depends On",
                        relationship_types=[
                            "Depends On",
                            "Trades",
                            "Shares Commodity",
                        ],
                        direction="undirected",
                        weight=float(
                            row[column]
                            / max(graph.nodes[commodity_node].get("price", 1), 1)
                        ),
                        confidence=0.8,
                        timestamp=row["month_date"],
                    )
        self._add_enterprise_edges(graph, frame)

    def _add_enterprise_edges(self, graph: nx.Graph, frame: pd.DataFrame) -> None:
        for _, group in frame.groupby(["village", "sector"]):
            rows = list(group.to_dict("records"))[: self.config.max_pair_edges + 1]
            for left, right in combinations(rows, 2):
                correlation = self._similarity(left, right)
                graph.add_edge(
                    f"enterprise:{left['enterprise_id']}",
                    f"enterprise:{right['enterprise_id']}",
                    relationship_type="Similar To",
                    relationship_types=["Similar To"],
                    direction="undirected",
                    weight=correlation,
                    confidence=correlation,
                    correlation=correlation,
                    timestamp=max(left["month_date"], right["month_date"]),
                )

    @staticmethod
    def _similarity(left: dict[str, Any], right: dict[str, Any]) -> float:
        values = (
            "income",
            "expense",
            "net_cash_flow",
            "risk_score",
            "outstanding_loan",
        )
        a = pd.Series([float(left[key]) for key in values])
        b = pd.Series([float(right[key]) for key in values])
        denominator = float(a.abs().sum() + b.abs().sum()) or 1.0
        return max(0.0, min(1.0, 1.0 - float((a - b).abs().sum()) / denominator))
