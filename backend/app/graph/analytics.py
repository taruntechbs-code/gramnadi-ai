from __future__ import annotations

import networkx as nx


def graph_statistics(graph: nx.Graph) -> dict:
    degrees = [degree for _, degree in graph.degree()]
    supported_nodes = {
        "Enterprise",
        "Village",
        "Commodity",
        "Weather Region",
        "Loan Cluster",
        "Intervention",
        "Risk Cluster",
    }
    supported_relationships = {
        "Located In",
        "Trades",
        "Depends On",
        "Affected By",
        "Similar To",
        "Shares Commodity",
        "Shares Weather",
        "Financial Dependency",
        "Received Intervention",
    }
    node_counts = dict(_counts(graph, "node_type"))
    relationship_counts = dict(_edge_counts(graph))
    for _, _, attrs in graph.edges(data=True):
        for relationship in attrs.get("relationship_types", []):
            relationship_counts[relationship] = (
                relationship_counts.get(relationship, 0) + 1
            )
    node_counts.update({name: node_counts.get(name, 0) for name in supported_nodes})
    relationship_counts.update(
        {name: relationship_counts.get(name, 0) for name in supported_relationships}
    )
    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "density": nx.density(graph),
        "average_clustering_coefficient": nx.average_clustering(graph, weight="weight"),
        "average_degree": sum(degrees) / len(degrees) if degrees else 0.0,
        "connected_components": nx.number_connected_components(graph),
        "node_types": node_counts,
        "relationship_types": relationship_counts,
    }


def _counts(graph, field):
    counts = {}
    for _, attrs in graph.nodes(data=True):
        counts[attrs.get(field, "unknown")] = (
            counts.get(attrs.get(field, "unknown"), 0) + 1
        )
    return counts.items()


def _edge_counts(graph):
    counts = {}
    for _, _, attrs in graph.edges(data=True):
        counts[attrs.get("relationship_type", "unknown")] = (
            counts.get(attrs.get("relationship_type", "unknown"), 0) + 1
        )
    return counts


def analytics_summary(graph: nx.Graph, centrality: dict[str, dict[str, float]]) -> dict:
    enterprises = [
        (node, attrs)
        for node, attrs in graph.nodes(data=True)
        if attrs.get("node_type") == "Enterprise"
    ]
    villages = [
        (node, attrs)
        for node, attrs in graph.nodes(data=True)
        if attrs.get("node_type") == "Village"
    ]
    influential = sorted(
        enterprises,
        key=lambda item: centrality.get(item[0], {}).get("pagerank", 0),
        reverse=True,
    )[:10]
    risky_villages = sorted(
        villages, key=lambda item: item[1].get("average_risk", 0), reverse=True
    )[:10]
    return {
        "most_influential_enterprises": [
            {"node_id": node, "pagerank": centrality.get(node, {}).get("pagerank", 0)}
            for node, _ in influential
        ],
        "highest_risk_villages": [
            {"node_id": node, "average_risk": attrs.get("average_risk", 0)}
            for node, attrs in risky_villages
        ],
    }
