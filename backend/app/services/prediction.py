from app.models.prediction import Prediction
from app.schemas.prediction import PredictionCreate, PredictionUpdate
from app.services.base import CRUDService


class PredictionService(CRUDService[Prediction, PredictionCreate, PredictionUpdate]):
    model = Prediction
    resource_name = "prediction"
