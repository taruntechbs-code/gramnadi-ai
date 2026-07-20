from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.enterprise import Enterprise


class FinancialRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "financial_records"
    __table_args__ = (
        UniqueConstraint(
            "enterprise_id",
            "month",
            "year",
            name="uq_financial_records_enterprise_month_year",
        ),
        Index(
            "ix_financial_records_enterprise_period", "enterprise_id", "year", "month"
        ),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_financial_records_month"),
        CheckConstraint("year BETWEEN 1900 AND 2100", name="ck_financial_records_year"),
        CheckConstraint("income >= 0", name="ck_financial_records_income_non_negative"),
        CheckConstraint(
            "expense >= 0", name="ck_financial_records_expense_non_negative"
        ),
        CheckConstraint(
            "savings >= 0", name="ck_financial_records_savings_non_negative"
        ),
        CheckConstraint(
            "cash_balance >= 0", name="ck_financial_records_cash_balance_non_negative"
        ),
        CheckConstraint(
            "inventory_value >= 0",
            name="ck_financial_records_inventory_value_non_negative",
        ),
        CheckConstraint(
            "upi_transaction_count >= 0",
            name="ck_financial_records_upi_transaction_count_non_negative",
        ),
        CheckConstraint(
            "upi_inflow >= 0", name="ck_financial_records_upi_inflow_non_negative"
        ),
        CheckConstraint(
            "upi_outflow >= 0", name="ck_financial_records_upi_outflow_non_negative"
        ),
    )

    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey("enterprises.id", ondelete="CASCADE"), nullable=False
    )
    month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    income: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    expense: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    profit: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    savings: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    inventory_value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    upi_transaction_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    upi_inflow: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    upi_outflow: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    enterprise: Mapped["Enterprise"] = relationship(back_populates="financial_records")

    @property
    def period_start(self) -> date:
        return date(self.year, self.month, 1)
