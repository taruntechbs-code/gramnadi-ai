from datetime import date as Date
from uuid import UUID

from pydantic import Field

from app.models.enums import InterventionStatus, InterventionType
from app.schemas.common import RequestModel, TimestampedResponse


class InterventionCreate(RequestModel):
    enterprise_id: UUID
    intervention_type: InterventionType = Field(
        ..., examples=[InterventionType.FINANCIAL_COUNSELLING]
    )
    description: str = Field(
        ..., min_length=1, examples=["Review monthly cash commitments."]
    )
    created_by: str = Field(..., min_length=1, max_length=200, examples=["system"])
    status: InterventionStatus = Field(..., examples=[InterventionStatus.PLANNED])
    date: Date = Field(..., examples=["2026-06-01"])


class InterventionUpdate(RequestModel):
    enterprise_id: UUID | None = None
    intervention_type: InterventionType | None = None
    description: str | None = Field(None, min_length=1)
    created_by: str | None = Field(None, min_length=1, max_length=200)
    status: InterventionStatus | None = None
    date: Date | None = None


class InterventionResponse(TimestampedResponse):
    enterprise_id: UUID
    intervention_type: InterventionType
    description: str
    created_by: str
    status: InterventionStatus
    date: Date
