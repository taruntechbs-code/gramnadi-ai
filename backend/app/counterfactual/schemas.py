from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    enterprise_id: str | None = None
    features: dict[str, Any]


class RecommendationBatchRequest(BaseModel):
    items: list[RecommendationRequest] = Field(min_length=1, max_length=50)


class RecommendationResponse(BaseModel):
    enterprise_id: str | None
    current_prediction: dict[str, Any]
    recommendations: list[dict[str, Any]]
    generated_at: str
    latency_ms: float


class RecommendationBatchResponse(BaseModel):
    results: list[RecommendationResponse]
    count: int
    average_latency_ms: float


class RecommendationHealth(BaseModel):
    status: str
    ready: bool
    ml_ready: bool
    graph_ready: bool
