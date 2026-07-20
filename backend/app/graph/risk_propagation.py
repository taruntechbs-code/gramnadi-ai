from __future__ import annotations

import networkx as nx


def propagate_risk(
    graph: nx.Graph, enterprise_id: str, shock: float = 0.2, max_hops: int = 3
) -> dict:
    node = (
        enterprise_id
        if enterprise_id.startswith("enterprise:")
        else f"enterprise:{enterprise_id}"
    )
    if node not in graph:
        return {
            "enterprise_id": enterprise_id,
            "affected_nodes": [],
            "propagated_risk": 0.0,
        }
    affected = []
    for target, distance in nx.single_source_shortest_path_length(
        graph, node, cutoff=max_hops
    ).items():
        if target == node:
            continue
        risk = float(shock / max(distance, 1))
        attrs = graph.nodes[target]
        affected.append(
            {
                "node_id": target,
                "node_type": attrs.get("node_type"),
                "risk_delta": risk,
                "distance": distance,
                "explanation": (
                    "Risk propagates through shared village, commodity, weather, "
                    "or financial relationships."
                ),
            }
        )
    return {
        "enterprise_id": enterprise_id,
        "shock": shock,
        "max_hops": max_hops,
        "affected_nodes": sorted(
            affected, key=lambda item: item["risk_delta"], reverse=True
        ),
        "propagated_risk": sum(item["risk_delta"] for item in affected),
    }
