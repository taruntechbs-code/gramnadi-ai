from app.api.v1.routes.crud import build_crud_router
from app.schemas.prediction import (
    PredictionCreate,
    PredictionResponse,
    PredictionUpdate,
)
from app.services.prediction import PredictionService

router = build_crud_router(
    resource_path="predictions",
    resource_name="prediction",
    tag="Predictions",
    create_schema=PredictionCreate,
    update_schema=PredictionUpdate,
    response_schema=PredictionResponse,
    service_factory=PredictionService,
)
