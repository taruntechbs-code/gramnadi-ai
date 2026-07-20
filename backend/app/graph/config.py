from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GraphConfig:
    data_path: Path
    processed_path: Path
    reports_dir: Path
    max_pair_edges: int = 8
    top_k: int = 10

    @classmethod
    def from_environment(cls) -> "GraphConfig":
        root = Path(__file__).resolve().parents[3]
        return cls(
            data_path=Path(
                os.getenv(
                    "GRAMNADI_GRAPH_DATA",
                    root / "datasets/synthetic_rural_financial_data.parquet",
                )
            ),
            processed_path=Path(
                os.getenv("GRAMNADI_GRAPH_PROCESSED", root / "ml/processed")
            ),
            reports_dir=Path(
                os.getenv("GRAMNADI_GRAPH_REPORTS", root / "backend/app/graph/reports")
            ),
            max_pair_edges=int(os.getenv("GRAMNADI_GRAPH_MAX_PAIR_EDGES", "8")),
            top_k=int(os.getenv("GRAMNADI_GRAPH_TOP_K", "10")),
        )
