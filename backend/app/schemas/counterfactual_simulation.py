from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.common import RequestModel, TimestampedResponse


class CounterfactualSimulationCreate(RequestModel):
    enterprise_id: UUID
    scenario_name: str = Field(
        ..., min_length=1, max_length=200, examples=["Increase stock"]
    )
    modified_variable: str = Field(
        ..., min_length=1, max_length=160, examples=["inventory_value"]
    )
    old_value: Any = Field(..., examples=[90000])
    new_value: Any = Field(..., examples=[120000])
    predicted_cashflow: Decimal = Field(..., decimal_places=2, examples=[52000])
    predicted_risk: Decimal = Field(..., ge=0, le=100, decimal_places=2, examples=[22])


class CounterfactualSimulationUpdate(RequestModel):
    enterprise_id: UUID | None = None
    scenario_name: str | None = Field(None, min_length=1, max_length=200)
    modified_variable: str | None = Field(None, min_length=1, max_length=160)
    old_value: Any | None = None
    new_value: Any | None = None
    predicted_cashflow: Decimal | None = Field(None, decimal_places=2)
    predicted_risk: Decimal | None = Field(None, ge=0, le=100, decimal_places=2)


class CounterfactualSimulationResponse(TimestampedResponse):
    enterprise_id: UUID
    scenario_name: str
    modified_variable: str
    old_value: Any
    new_value: Any
    predicted_cashflow: Decimal
    predicted_risk: Decimal
