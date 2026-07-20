from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MLPredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enterprise_id: str | None = None
    features: dict[str, Any] = Field(
        default_factory=dict,
        description="Phase 3A model-ready or raw enterprise feature payload",
    )


class MLBulkPredictionRequest(BaseModel):
    items: list[MLPredictionRequest] = Field(min_length=1)


class MLPredictionResponse(BaseModel):
    enterprise_id: str | None
    cash_flow_prediction: float
    risk_prediction: str
    risk_probability: dict[str, float]
    confidence: dict[str, Any]
    cash_flow_confidence: dict[str, Any]
    prediction_interval: dict[str, float]
    top_factors: list[dict[str, Any]]
    explanation: dict[str, Any]
    model: dict[str, Any]
    inference_timestamp: str
    latency_ms: float


class MLPredictionBatchResponse(BaseModel):
    predictions: list[MLPredictionResponse]
    count: int
    average_latency_ms: float


class MLHealthResponse(BaseModel):
    status: str
    models_loaded: bool
    encoder_loaded: bool
    inference_ready: bool
    detail: str | None = None


class MLModelInfoResponse(BaseModel):
    model_version: str
    trained_on: str | None
    feature_count: int
    metrics: dict[str, Any]
    calibration: str | None
