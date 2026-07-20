from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.prediction import Prediction


class PredictionExplanation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "prediction_explanations"
    __table_args__ = (
        UniqueConstraint(
            "prediction_id",
            "feature_name",
            name="uq_prediction_explanations_prediction_feature",
        ),
        CheckConstraint(
            "feature_importance >= -1 AND feature_importance <= 1",
            name="ck_prediction_explanations_importance_range",
        ),
    )

    prediction_id: Mapped[UUID] = mapped_column(
        ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False
    )
    feature_name: Mapped[str] = mapped_column(String(160), nullable=False)
    feature_importance: Mapped[Decimal] = mapped_column(Numeric(7, 6), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    prediction: Mapped["Prediction"] = relationship(back_populates="explanations")
