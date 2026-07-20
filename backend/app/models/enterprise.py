from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_type
from app.models.enums import EnterpriseType, Sector

if TYPE_CHECKING:
    from app.models.counterfactual_simulation import CounterfactualSimulation
    from app.models.financial_record import FinancialRecord
    from app.models.intervention import Intervention
    from app.models.loan import Loan
    from app.models.prediction import Prediction
    from app.models.village_graph_node import VillageGraphNode


class Enterprise(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "enterprises"
    __table_args__ = (
        UniqueConstraint("enterprise_code", name="uq_enterprises_enterprise_code"),
        Index("ix_enterprises_location", "state", "district", "village"),
        Index("ix_enterprises_sector", "sector"),
        CheckConstraint("employees >= 0", name="ck_enterprises_employees_non_negative"),
        CheckConstraint(
            "annual_turnover >= 0",
            name="ck_enterprises_annual_turnover_non_negative",
        ),
    )

    enterprise_code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    owner_name: Mapped[str] = mapped_column(String(200), nullable=False)
    enterprise_type: Mapped[EnterpriseType] = mapped_column(
        enum_type(EnterpriseType, "enterprise_type_enum"),
        nullable=False,
    )
    district: Mapped[str] = mapped_column(String(120), nullable=False)
    state: Mapped[str] = mapped_column(String(120), nullable=False)
    village: Mapped[str] = mapped_column(String(120), nullable=False)
    sector: Mapped[Sector] = mapped_column(
        enum_type(Sector, "sector_enum"), nullable=False
    )
    business_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    employees: Mapped[int] = mapped_column(nullable=False, default=0)
    annual_turnover: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )

    financial_records: Mapped[list["FinancialRecord"]] = relationship(
        back_populates="enterprise", cascade="all, delete-orphan"
    )
    loans: Mapped[list["Loan"]] = relationship(
        back_populates="enterprise", cascade="all, delete-orphan"
    )
    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="enterprise", cascade="all, delete-orphan"
    )
    interventions: Mapped[list["Intervention"]] = relationship(
        back_populates="enterprise", cascade="all, delete-orphan"
    )
    simulations: Mapped[list["CounterfactualSimulation"]] = relationship(
        back_populates="enterprise", cascade="all, delete-orphan"
    )
    graph_nodes: Mapped[list["VillageGraphNode"]] = relationship(
        back_populates="enterprise", cascade="all, delete-orphan"
    )
