from app.api.v1.routes.crud import build_crud_router
from app.schemas.prediction_explanation import (
    PredictionExplanationCreate,
    PredictionExplanationResponse,
    PredictionExplanationUpdate,
)
from app.services.prediction_explanation import PredictionExplanationService

router = build_crud_router(
    resource_path="prediction-explanations",
    resource_name="prediction explanation",
    tag="Prediction Explanations",
    create_schema=PredictionExplanationCreate,
    update_schema=PredictionExplanationUpdate,
    response_schema=PredictionExplanationResponse,
    service_factory=PredictionExplanationService,
)
