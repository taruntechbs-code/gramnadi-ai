from app.models.village_graph_node import VillageGraphNode
from app.schemas.village_graph_node import (
    VillageGraphNodeCreate,
    VillageGraphNodeUpdate,
)
from app.services.base import CRUDService


class VillageGraphNodeService(
    CRUDService[VillageGraphNode, VillageGraphNodeCreate, VillageGraphNodeUpdate]
):
    model = VillageGraphNode
    resource_name = "village graph node"
