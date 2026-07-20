from app.api.v1.routes.crud import build_crud_router
from app.schemas.village_graph_edge import (
    VillageGraphEdgeCreate,
    VillageGraphEdgeResponse,
    VillageGraphEdgeUpdate,
)
from app.services.village_graph_edge import VillageGraphEdgeService

router = build_crud_router(
    resource_path="village-graph-edges",
    resource_name="village graph edge",
    tag="Village Graph Edges",
    create_schema=VillageGraphEdgeCreate,
    update_schema=VillageGraphEdgeUpdate,
    response_schema=VillageGraphEdgeResponse,
    service_factory=VillageGraphEdgeService,
)
