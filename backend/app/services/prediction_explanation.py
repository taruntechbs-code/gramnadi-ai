from app.models.prediction_explanation import PredictionExplanation
from app.schemas.prediction_explanation import (
    PredictionExplanationCreate,
    PredictionExplanationUpdate,
)
from app.services.base import CRUDService


class PredictionExplanationService(
    CRUDService[
        PredictionExplanation,
        PredictionExplanationCreate,
        PredictionExplanationUpdate,
    ]
):
    model = PredictionExplanation
    resource_name = "prediction explanation"
