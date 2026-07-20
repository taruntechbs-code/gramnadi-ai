from app.models.counterfactual_simulation import CounterfactualSimulation
from app.schemas.counterfactual_simulation import (
    CounterfactualSimulationCreate,
    CounterfactualSimulationUpdate,
)
from app.services.base import CRUDService


class CounterfactualSimulationService(
    CRUDService[
        CounterfactualSimulation,
        CounterfactualSimulationCreate,
        CounterfactualSimulationUpdate,
    ]
):
    model = CounterfactualSimulation
    resource_name = "counterfactual simulation"
