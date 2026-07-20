from __future__ import annotations

import networkx as nx


def node_details(graph: nx.Graph, node_id: str) -> dict:
    node = node_id if node_id in graph else f"enterprise:{node_id}"
    if node not in graph:
        raise KeyError(node_id)
    return {
        "node_id": node,
        "attributes": dict(graph.nodes[node]),
        "neighbors": [
            {
                "node_id": neighbor,
                "attributes": dict(graph.nodes[neighbor]),
                "edge": dict(graph.edges[node, neighbor]),
            }
            for neighbor in graph.neighbors(node)
        ],
    }


def community_details(graph: nx.Graph, community_id: int) -> dict:
    members = [
        node
        for node, attrs in graph.nodes(data=True)
        if attrs.get("community_id") == community_id
    ]
    return {
        "community_id": community_id,
        "size": len(members),
        "members": [
            {"node_id": node, "attributes": dict(graph.nodes[node])} for node in members
        ],
    }


def shortest_path(graph: nx.Graph, source: str, target: str) -> list[str]:
    return nx.shortest_path(graph, source, target)
