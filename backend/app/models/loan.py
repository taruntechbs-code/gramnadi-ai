from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_type
from app.models.enums import LoanStatus, LoanType

if TYPE_CHECKING:
    from app.models.enterprise import Enterprise


class Loan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "loans"
    __table_args__ = (
        Index("ix_loans_enterprise_status", "enterprise_id", "status"),
        CheckConstraint(
            "principal_amount >= 0", name="ck_loans_principal_amount_non_negative"
        ),
        CheckConstraint(
            "interest_rate >= 0 AND interest_rate <= 100",
            name="ck_loans_interest_rate_range",
        ),
        CheckConstraint(
            "outstanding_amount >= 0",
            name="ck_loans_outstanding_amount_non_negative",
        ),
        CheckConstraint(
            "monthly_installment >= 0",
            name="ck_loans_monthly_installment_non_negative",
        ),
    )

    enterprise_id: Mapped[UUID] = mapped_column(
        ForeignKey("enterprises.id", ondelete="CASCADE"), nullable=False
    )
    loan_type: Mapped[LoanType] = mapped_column(
        enum_type(LoanType, "loan_type_enum"), nullable=False
    )
    lender: Mapped[str] = mapped_column(String(200), nullable=False)
    principal_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    outstanding_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    monthly_installment: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    next_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[LoanStatus] = mapped_column(
        enum_type(LoanStatus, "loan_status_enum"), nullable=False
    )

    enterprise: Mapped["Enterprise"] = relationship(back_populates="loans")
