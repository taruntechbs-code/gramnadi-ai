from decimal import Decimal
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.common import RequestModel, TimestampedResponse


class VillageGraphEdgeCreate(RequestModel):
    source_node: UUID
    target_node: UUID
    relationship: str = Field(..., min_length=1, max_length=120, examples=["supplies"])
    weight: Decimal = Field(..., ge=0, decimal_places=4, examples=[0.75])

    @model_validator(mode="after")
    def validate_distinct_nodes(self) -> "VillageGraphEdgeCreate":
        if self.source_node == self.target_node:
            raise ValueError("source_node and target_node must be different")
        return self


class VillageGraphEdgeUpdate(RequestModel):
    source_node: UUID | None = None
    target_node: UUID | None = None
    relationship: str | None = Field(None, min_length=1, max_length=120)
    weight: Decimal | None = Field(None, ge=0, decimal_places=4)


class VillageGraphEdgeResponse(TimestampedResponse):
    source_node: UUID
    target_node: UUID
    relationship: str
    weight: Decimal
