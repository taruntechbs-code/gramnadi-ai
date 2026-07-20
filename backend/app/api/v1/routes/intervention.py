from app.api.v1.routes.crud import build_crud_router
from app.schemas.intervention import (
    InterventionCreate,
    InterventionResponse,
    InterventionUpdate,
)
from app.services.intervention import InterventionService

router = build_crud_router(
    resource_path="interventions",
    resource_name="intervention",
    tag="Interventions",
    create_schema=InterventionCreate,
    update_schema=InterventionUpdate,
    response_schema=InterventionResponse,
    service_factory=InterventionService,
)
