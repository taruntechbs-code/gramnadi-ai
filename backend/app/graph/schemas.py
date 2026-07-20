from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class GraphHealth(BaseModel):
    status: str
    loaded: bool
    nodes: int
    edges: int


class GraphResponse(BaseModel):
    result: dict[str, Any]
