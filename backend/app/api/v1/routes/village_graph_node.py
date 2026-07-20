from app.api.v1.routes.crud import build_crud_router
from app.schemas.village_graph_node import (
    VillageGraphNodeCreate,
    VillageGraphNodeResponse,
    VillageGraphNodeUpdate,
)
from app.services.village_graph_node import VillageGraphNodeService

router = build_crud_router(
    resource_path="village-graph-nodes",
    resource_name="village graph node",
    tag="Village Graph Nodes",
    create_schema=VillageGraphNodeCreate,
    update_schema=VillageGraphNodeUpdate,
    response_schema=VillageGraphNodeResponse,
    service_factory=VillageGraphNodeService,
)
