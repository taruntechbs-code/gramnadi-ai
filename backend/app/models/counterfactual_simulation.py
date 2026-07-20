from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import JSON, CheckConstraint, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.enterprise import Enterprise


class CounterfactualSimulation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "counterfactual_simulations"
    __table_args__ = (
        Index("ix_counterfactual_simulations_enterprise", "enterprise_id"),
        CheckConstraint(
            "predicted_risk >= 0 AND predicted_risk <= 100",
            name="ck_counterfactual_simulations_predicted_risk_range",
        ),
    )

    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey("enterprises.id", ondelete="CASCADE"), nullable=False
    )
    scenario_name: Mapped[str] = mapped_column(String(200), nullable=False)
    modified_variable: Mapped[str] = mapped_column(String(160), nullable=False)
    old_value: Mapped[Any] = mapped_column(JSON, nullable=False)
    new_value: Mapped[Any] = mapped_column(JSON, nullable=False)
    predicted_cashflow: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    predicted_risk: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    enterprise: Mapped["Enterprise"] = relationship(back_populates="simulations")
