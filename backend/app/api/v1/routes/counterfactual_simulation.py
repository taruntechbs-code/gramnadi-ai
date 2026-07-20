from app.api.v1.routes.crud import build_crud_router
from app.schemas.counterfactual_simulation import (
    CounterfactualSimulationCreate,
    CounterfactualSimulationResponse,
    CounterfactualSimulationUpdate,
)
from app.services.counterfactual_simulation import CounterfactualSimulationService

router = build_crud_router(
    resource_path="counterfactual-simulations",
    resource_name="counterfactual simulation",
    tag="Counterfactual Simulations",
    create_schema=CounterfactualSimulationCreate,
    update_schema=CounterfactualSimulationUpdate,
    response_schema=CounterfactualSimulationResponse,
    service_factory=CounterfactualSimulationService,
)
