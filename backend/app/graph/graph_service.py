from __future__ import annotations

import logging
from time import perf_counter

import networkx as nx

from .analytics import analytics_summary, graph_statistics
from .builder import GraphBuilder
from .cache import graph_cache
from .centrality import compute_centrality
from .community import detect_communities
from .config import GraphConfig
from .risk_propagation import propagate_risk
from .similarity import similar_enterprises
from .utils import write_json

logger = logging.getLogger(__name__)


class GraphService:
    """Owns the in-memory graph and all read-only graph analytics."""

    def __init__(self, config: GraphConfig | None = None) -> None:
        self.config = config or GraphConfig.from_environment()
        self.graph: nx.Graph | None = graph_cache.graph
        self.centrality: dict = self._cached_centrality()
        self.communities: dict = self._cached_communities()

    @property
    def loaded(self) -> bool:
        return self.graph is not None

    def load(self) -> nx.Graph:
        if self.graph is not None:
            return self.graph
        with graph_cache.lock:
            if self.graph is None:
                started = perf_counter()
                self.graph = GraphBuilder(self.config).build()
                build_seconds = perf_counter() - started
                self.communities = detect_communities(self.graph)
                self.centrality = compute_centrality(self.graph)
                graph_cache.graph = self.graph
                self.graph.graph["build_seconds"] = build_seconds
                self._write_reports()
                logger.info(
                    "Village graph loaded: %d nodes, %d edges",
                    self.graph.number_of_nodes(),
                    self.graph.number_of_edges(),
                )
        return self.graph

    def require_graph(self) -> nx.Graph:
        return self.graph if self.graph is not None else self.load()

    def _cached_communities(self) -> dict:
        if self.graph is None:
            return {}
        return {
            node: attrs["community_id"]
            for node, attrs in self.graph.nodes(data=True)
            if "community_id" in attrs
        }

    def _cached_centrality(self) -> dict:
        if self.graph is None:
            return {}
        names = ("degree", "betweenness", "closeness", "eigenvector", "pagerank")
        return {
            node: {name: float(attrs.get(name, 0)) for name in names}
            for node, attrs in self.graph.nodes(data=True)
            if any(name in attrs for name in names)
        }

    def summary(self) -> dict:
        graph = self.require_graph()
        return {
            "statistics": graph_statistics(graph),
            "analytics": analytics_summary(graph, self.centrality),
            "community_count": len(set(self.communities.values())),
        }

    def _write_reports(self) -> None:
        graph = self.require_graph()
        self.config.reports_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            self.config.reports_dir / "graph_statistics.json", graph_statistics(graph)
        )
        write_json(self.config.reports_dir / "graph_summary.json", self.summary())
        write_json(
            self.config.reports_dir / "community_report.json",
            {
                "community_count": len(set(self.communities.values())),
                "communities": {
                    str(key): list(value)
                    for key, value in self._community_members().items()
                },
            },
        )
        write_json(
            self.config.reports_dir / "centrality_report.json",
            {"centrality": self.centrality},
        )
        enterprise_nodes = [
            node
            for node, attrs in graph.nodes(data=True)
            if attrs.get("node_type") == "Enterprise"
        ]
        sample = enterprise_nodes[0].split(":", 1)[1] if enterprise_nodes else ""
        write_json(
            self.config.reports_dir / "similarity_report.json",
            (
                {
                    "enterprise_id": sample,
                    "similar_enterprises": similar_enterprises(
                        graph, sample, self.config.top_k
                    ),
                }
                if sample
                else {}
            ),
        )
        write_json(
            self.config.reports_dir / "risk_propagation_report.json",
            propagate_risk(graph, sample) if sample else {},
        )
        (self.config.reports_dir / "graph_build_log.txt").write_text(
            f"Graph built in {graph.graph.get('build_seconds', 0):.4f} seconds\n"
            f"Nodes: {graph.number_of_nodes()}\nEdges: {graph.number_of_edges()}\n",
            encoding="utf-8",
        )
        self._write_visualizations()

    def _community_members(self) -> dict[int, list[str]]:
        members: dict[int, list[str]] = {}
        for node, community_id in self.communities.items():
            members.setdefault(community_id, []).append(node)
        return members

    def _write_visualizations(self) -> None:
        """Write small diagnostic plots without affecting inference behavior."""
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            graph = self.require_graph()
            layout = nx.spring_layout(graph, seed=42, k=0.25, iterations=20)
            plt.figure(figsize=(12, 8))
            nx.draw_networkx(
                graph, pos=layout, node_size=8, width=0.15, with_labels=False
            )
            plt.savefig(
                self.config.reports_dir / "graph_visualization.png",
                dpi=120,
                bbox_inches="tight",
            )
            plt.close()
            colors = [self.communities.get(node, -1) for node in graph]
            plt.figure(figsize=(12, 8))
            nx.draw_networkx(
                graph,
                pos=layout,
                node_size=8,
                node_color=colors,
                cmap="tab20",
                width=0.1,
                with_labels=False,
            )
            plt.savefig(
                self.config.reports_dir / "community_visualization.png",
                dpi=120,
                bbox_inches="tight",
            )
            plt.close()
            risk_nodes = [
                node
                for node, attrs in graph.nodes(data=True)
                if attrs.get("node_type") == "Village"
            ]
            plt.figure(figsize=(10, 5))
            plt.bar(
                [graph.nodes[node].get("name", node) for node in risk_nodes],
                [graph.nodes[node].get("average_risk", 0) for node in risk_nodes],
            )
            plt.xticks(rotation=60, ha="right")
            plt.ylabel("Average risk score")
            plt.tight_layout()
            plt.savefig(self.config.reports_dir / "risk_visualization.png", dpi=120)
            plt.close()
            top = sorted(
                self.centrality.items(),
                key=lambda item: item[1].get("pagerank", 0),
                reverse=True,
            )[:10]
            plt.figure(figsize=(10, 5))
            plt.bar(
                [node for node, _ in top],
                [metrics["pagerank"] for _, metrics in top],
            )
            plt.xticks(rotation=60, ha="right")
            plt.ylabel("PageRank")
            plt.tight_layout()
            plt.savefig(
                self.config.reports_dir / "centrality_visualization.png", dpi=120
            )
            plt.close()
        except Exception as exc:  # pragma: no cover
            logger.warning("Graph visualization generation skipped: %s", exc)
