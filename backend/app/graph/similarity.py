from __future__ import annotations

import networkx as nx


def similar_enterprises(
    graph: nx.Graph, enterprise_id: str, top_k: int = 10
) -> list[dict]:
    node = (
        enterprise_id
        if enterprise_id.startswith("enterprise:")
        else f"enterprise:{enterprise_id}"
    )
    if node not in graph:
        return []
    candidates = []
    source = graph.nodes[node]
    for other, attrs in graph.nodes(data=True):
        if other == node or attrs.get("node_type") != "Enterprise":
            continue
        score = 0.0
        if attrs.get("sector") == source.get("sector"):
            score += 0.35
        if attrs.get("village") == source.get("village"):
            score += 0.25
        score += max(
            0.0,
            0.4
            - abs(
                float(attrs.get("risk_score", 0)) - float(source.get("risk_score", 0))
            )
            / 250,
        )
        candidates.append(
            {
                "enterprise_id": other.split(":", 1)[1],
                "similarity": min(score, 1.0),
                "sector": attrs.get("sector"),
                "village": attrs.get("village"),
            }
        )
    return sorted(candidates, key=lambda item: item["similarity"], reverse=True)[:top_k]
