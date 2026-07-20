from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_type
from app.models.enums import InterventionStatus, InterventionType

if TYPE_CHECKING:
    from app.models.enterprise import Enterprise


class Intervention(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "interventions"
    __table_args__ = (
        Index("ix_interventions_enterprise_status", "enterprise_id", "status"),
    )

    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey("enterprises.id", ondelete="CASCADE"), nullable=False
    )
    intervention_type: Mapped[InterventionType] = mapped_column(
        enum_type(InterventionType, "intervention_type_enum"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[InterventionStatus] = mapped_column(
        enum_type(InterventionStatus, "intervention_status_enum"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)

    enterprise: Mapped["Enterprise"] = relationship(back_populates="interventions")
