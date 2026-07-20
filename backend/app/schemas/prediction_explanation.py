from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.schemas.common import RequestModel, TimestampedResponse


class PredictionExplanationCreate(RequestModel):
    prediction_id: UUID
    feature_name: str = Field(
        ..., min_length=1, max_length=160, examples=["cash_balance"]
    )
    feature_importance: Decimal = Field(
        ..., ge=-1, le=1, decimal_places=6, examples=[0.42]
    )
    explanation: str = Field(
        ...,
        min_length=1,
        examples=["Recent cash balance increased the predicted resilience score."],
    )


class PredictionExplanationUpdate(RequestModel):
    prediction_id: UUID | None = None
    feature_name: str | None = Field(None, min_length=1, max_length=160)
    feature_importance: Decimal | None = Field(None, ge=-1, le=1, decimal_places=6)
    explanation: str | None = Field(None, min_length=1)


class PredictionExplanationResponse(TimestampedResponse):
    prediction_id: UUID
    feature_name: str
    feature_importance: Decimal
    explanation: str
