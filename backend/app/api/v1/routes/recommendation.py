from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.counterfactual.cache import recommendation_cache
from app.counterfactual.engine import RecommendationEngine
from app.counterfactual.schemas import (
    RecommendationBatchRequest,
    RecommendationBatchResponse,
    RecommendationHealth,
    RecommendationRequest,
    RecommendationResponse,
)

router = APIRouter(prefix="/recommend", tags=["recommendations"])


def _engine(request: Request) -> RecommendationEngine:
    ml_loader = request.app.state.model_loader
    graph_service = request.app.state.graph_service
    if not ml_loader.loaded:
        raise HTTPException(status_code=503, detail="ML models are unavailable")
    if not hasattr(request.app.state, "predictor"):
        raise HTTPException(
            status_code=503, detail="Inference predictor is unavailable"
        )
    return RecommendationEngine(request.app.state.predictor, graph_service)


@router.post("", response_model=RecommendationResponse)
def recommend(
    payload: RecommendationRequest, request: Request
) -> RecommendationResponse:
    try:
        return RecommendationResponse.model_validate(
            _engine(request).recommend(payload.enterprise_id, payload.features)
        )
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/batch", response_model=RecommendationBatchResponse)
def recommend_batch(
    payload: RecommendationBatchRequest, request: Request
) -> RecommendationBatchResponse:
    import time

    started = time.perf_counter()
    engine = _engine(request)
    try:
        results = [
            RecommendationResponse.model_validate(
                engine.recommend(item.enterprise_id, item.features)
            )
            for item in payload.items
        ]
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return RecommendationBatchResponse(
        results=results,
        count=len(results),
        average_latency_ms=(time.perf_counter() - started) * 1000 / len(results),
    )


@router.get("/history/{enterprise_id}")
def history(enterprise_id: str) -> dict:
    return {
        "enterprise_id": enterprise_id,
        "recommendations": recommendation_cache.get(enterprise_id),
    }


@router.get("/health", response_model=RecommendationHealth)
def health(request: Request) -> RecommendationHealth:
    ml_ready = request.app.state.model_loader.loaded
    graph_ready = request.app.state.graph_service.loaded
    return RecommendationHealth(
        status="ok" if ml_ready and graph_ready else "degraded",
        ready=ml_ready and graph_ready,
        ml_ready=ml_ready,
        graph_ready=graph_ready,
    )
