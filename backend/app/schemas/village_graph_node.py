from uuid import UUID

from pydantic import Field

from app.models.enums import GraphNodeType
from app.schemas.common import RequestModel, TimestampedResponse


class VillageGraphNodeCreate(RequestModel):
    enterprise_id: UUID
    node_type: GraphNodeType = Field(..., examples=[GraphNodeType.SUPPLIER])


class VillageGraphNodeUpdate(RequestModel):
    enterprise_id: UUID | None = None
    node_type: GraphNodeType | None = None


class VillageGraphNodeResponse(TimestampedResponse):
    enterprise_id: UUID
    node_type: GraphNodeType
