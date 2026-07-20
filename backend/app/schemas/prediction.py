from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.models.enums import RiskLevel
from app.schemas.common import RequestModel, TimestampedResponse


class PredictionCreate(RequestModel):
    enterprise_id: UUID
    prediction_date: date = Field(..., examples=["2026-06-01"])
    cashflow_prediction: Decimal = Field(..., decimal_places=2, examples=[42000])
    risk_score: Decimal = Field(..., ge=0, le=100, decimal_places=2, examples=[28.5])
    risk_level: RiskLevel = Field(..., examples=[RiskLevel.MEDIUM])
    confidence_score: Decimal = Field(
        ..., ge=0, le=1, decimal_places=4, examples=[0.86]
    )
    model_version: str = Field(..., min_length=1, max_length=100, examples=["v0.1.0"])


class PredictionUpdate(RequestModel):
    enterprise_id: UUID | None = None
    prediction_date: date | None = None
    cashflow_prediction: Decimal | None = Field(None, decimal_places=2)
    risk_score: Decimal | None = Field(None, ge=0, le=100, decimal_places=2)
    risk_level: RiskLevel | None = None
    confidence_score: Decimal | None = Field(None, ge=0, le=1, decimal_places=4)
    model_version: str | None = Field(None, min_length=1, max_length=100)


class PredictionResponse(TimestampedResponse):
    enterprise_id: UUID
    prediction_date: date
    cashflow_prediction: Decimal
    risk_score: Decimal
    risk_level: RiskLevel
    confidence_score: Decimal
    model_version: str
