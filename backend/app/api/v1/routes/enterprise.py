from app.api.v1.routes.crud import build_crud_router
from app.schemas.enterprise import (
    EnterpriseCreate,
    EnterpriseResponse,
    EnterpriseUpdate,
)
from app.services.enterprise import EnterpriseService

router = build_crud_router(
    resource_path="enterprises",
    resource_name="enterprise",
    tag="Enterprises",
    create_schema=EnterpriseCreate,
    update_schema=EnterpriseUpdate,
    response_schema=EnterpriseResponse,
    service_factory=EnterpriseService,
)
