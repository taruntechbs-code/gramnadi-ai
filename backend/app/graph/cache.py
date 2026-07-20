from __future__ import annotations

from threading import Lock


class GraphCache:
    """Thread-safe process cache for the immutable startup graph."""

    def __init__(self) -> None:
        self.graph = None
        self.lock = Lock()


graph_cache = GraphCache()
