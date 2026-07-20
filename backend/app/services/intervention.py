from app.models.intervention import Intervention
from app.schemas.intervention import InterventionCreate, InterventionUpdate
from app.services.base import CRUDService


class InterventionService(
    CRUDService[Intervention, InterventionCreate, InterventionUpdate]
):
    model = Intervention
    resource_name = "intervention"
