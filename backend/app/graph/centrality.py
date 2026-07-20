from __future__ import annotations

import networkx as nx


def compute_centrality(graph: nx.Graph) -> dict[str, dict[str, float]]:
    try:
        eigenvector = nx.eigenvector_centrality(graph, max_iter=500, weight="weight")
    except nx.PowerIterationFailedConvergence:
        # Keep startup resilient for disconnected or numerically skewed graphs.
        eigenvector = nx.eigenvector_centrality_numpy(graph, weight="weight")
    metrics = {
        "degree": nx.degree_centrality(graph),
        "betweenness": nx.betweenness_centrality(
            graph, weight="weight", normalized=True
        ),
        "closeness": nx.closeness_centrality(graph, distance=None),
        "eigenvector": eigenvector,
        "pagerank": nx.pagerank(graph, weight="weight"),
    }
    for name, values in metrics.items():
        nx.set_node_attributes(graph, values, name)
    return {
        node: {name: float(values.get(node, 0)) for name, values in metrics.items()}
        for node in graph
    }
