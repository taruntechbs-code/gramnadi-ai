from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_type
from app.models.enums import RiskLevel

if TYPE_CHECKING:
    from app.models.enterprise import Enterprise
    from app.models.prediction_explanation import PredictionExplanation


class Prediction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "predictions"
    __table_args__ = (
        Index("ix_predictions_enterprise_date", "enterprise_id", "prediction_date"),
        CheckConstraint(
            "risk_score >= 0 AND risk_score <= 100",
            name="ck_predictions_risk_score_range",
        ),
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="ck_predictions_confidence_score_range",
        ),
    )

    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey("enterprises.id", ondelete="CASCADE"), nullable=False
    )
    prediction_date: Mapped[date] = mapped_column(Date, nullable=False)
    cashflow_prediction: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        enum_type(RiskLevel, "risk_level_enum"), nullable=False
    )
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)

    enterprise: Mapped["Enterprise"] = relationship(back_populates="predictions")
    explanations: Mapped[list["PredictionExplanation"]] = relationship(
        back_populates="prediction", cascade="all, delete-orphan"
    )
