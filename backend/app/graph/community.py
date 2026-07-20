from __future__ import annotations

import networkx as nx


def detect_communities(graph: nx.Graph) -> dict[str, int]:
    try:
        from networkx.algorithms.community import louvain_communities

        groups = louvain_communities(graph, weight="weight", seed=42)
    except (ImportError, AttributeError):
        groups = nx.algorithms.community.greedy_modularity_communities(
            graph, weight="weight"
        )
    communities = {node: index for index, group in enumerate(groups) for node in group}
    nx.set_node_attributes(graph, communities, "community_id")
    return communities
