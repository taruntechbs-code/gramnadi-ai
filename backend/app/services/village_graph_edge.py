from uuid import UUID

from app.models.village_graph_edge import VillageGraphEdge
from app.schemas.village_graph_edge import (
    VillageGraphEdgeCreate,
    VillageGraphEdgeUpdate,
)
from app.services.base import CRUDService
from app.services.exceptions import DomainValidationError


class VillageGraphEdgeService(
    CRUDService[VillageGraphEdge, VillageGraphEdgeCreate, VillageGraphEdgeUpdate]
):
    model = VillageGraphEdge
    resource_name = "village graph edge"

    def create(self, payload: VillageGraphEdgeCreate) -> VillageGraphEdge:
        self._validate_distinct_nodes(payload.source_node, payload.target_node)
        return super().create(payload)

    def update(
        self, resource_id: UUID, payload: VillageGraphEdgeUpdate
    ) -> VillageGraphEdge:
        resource = self.get(resource_id)
        values = payload.model_dump(exclude_unset=True)
        source_node = values.get("source_node", resource.source_node)
        target_node = values.get("target_node", resource.target_node)
        self._validate_distinct_nodes(source_node, target_node)
        return super().update(resource_id, payload)

    @staticmethod
    def _validate_distinct_nodes(source_node: UUID, target_node: UUID) -> None:
        if source_node == target_node:
            raise DomainValidationError("source_node and target_node must be different")
