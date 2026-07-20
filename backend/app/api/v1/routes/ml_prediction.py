from __future__ import annotations

import json
import logging
import time

from fastapi import APIRouter, HTTPException, Request, status

from app.ml.loader import ModelLoadError
from app.ml.predictor import Predictor
from app.ml.schemas import (
    MLBulkPredictionRequest,
    MLHealthResponse,
    MLModelInfoResponse,
    MLPredictionBatchResponse,
    MLPredictionRequest,
    MLPredictionResponse,
)
from app.ml.validator import InputValidationError

router = APIRouter(prefix="/ml", tags=["ml-inference"])
logger = logging.getLogger(__name__)


def _predictor(request: Request) -> Predictor:
    loader = request.app.state.model_loader
    if not loader.loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=loader.error or "ML models are unavailable",
        )
    return Predictor(loader.require_loaded(), loader.config)


@router.post("/predict", response_model=MLPredictionResponse)
def predict(payload: MLPredictionRequest, request: Request) -> MLPredictionResponse:
    predictor = _predictor(request)
    try:
        result = predictor.predict(payload.features, payload.enterprise_id)
        return MLPredictionResponse.model_validate(result)
    except (InputValidationError, ValueError, KeyError) as exc:
        logger.warning("ML validation failure: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ModelLoadError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("ML prediction failure")
        raise HTTPException(status_code=500, detail="Prediction failed") from exc


@router.post("/batch-predict", response_model=MLPredictionBatchResponse)
def batch_predict(
    payload: MLBulkPredictionRequest, request: Request
) -> MLPredictionBatchResponse:
    predictor = _predictor(request)
    if len(payload.items) > predictor.config.max_batch_size:
        raise HTTPException(
            status_code=413,
            detail=f"Batch size cannot exceed {predictor.config.max_batch_size}",
        )
    started = time.perf_counter()
    try:
        predictions = predictor.predict_batch(
            [(item.enterprise_id, item.features) for item in payload.items]
        )
    except (InputValidationError, ValueError, KeyError) as exc:
        logger.warning("ML batch validation failure: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    result = [MLPredictionResponse.model_validate(item) for item in predictions]
    return MLPredictionBatchResponse(
        predictions=result,
        count=len(result),
        average_latency_ms=(time.perf_counter() - started) * 1000 / len(result),
    )


@router.get("/health", response_model=MLHealthResponse)
def ml_health(request: Request) -> MLHealthResponse:
    loader = request.app.state.model_loader
    loaded = loader.loaded
    encoder_loaded = (
        loaded and loader.require_loaded().preprocessing.get("encoder") is not None
    )
    return MLHealthResponse(
        status="ok" if loaded else "degraded",
        models_loaded=loaded,
        encoder_loaded=bool(encoder_loaded),
        inference_ready=loaded,
        detail=loader.error,
    )


@router.get("/model-info", response_model=MLModelInfoResponse)
def model_info(request: Request) -> MLModelInfoResponse:
    loader = request.app.state.model_loader
    if not loader.loaded:
        raise HTTPException(
            status_code=503, detail=loader.error or "ML models are unavailable"
        )
    bundle = loader.require_loaded()
    metrics_path = loader.config.model_dir / "metrics.json"
    metrics = (
        json.loads(metrics_path.read_text(encoding="utf-8"))
        if metrics_path.exists()
        else {}
    )
    return MLModelInfoResponse(
        model_version=str(bundle.model_versions.get("version", "unknown")),
        trained_on=bundle.model_versions.get("created_at"),
        feature_count=len(bundle.feature_names),
        metrics=metrics,
        calibration=bundle.classification.get("calibration"),
    )
