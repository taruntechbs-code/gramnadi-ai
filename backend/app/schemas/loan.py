from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from app.models.enums import LoanStatus, LoanType
from app.schemas.common import RequestModel, TimestampedResponse


class LoanCreate(RequestModel):
    enterprise_id: UUID
    loan_type: LoanType = Field(..., examples=[LoanType.WORKING_CAPITAL])
    lender: str = Field(
        ..., min_length=2, max_length=200, examples=["District Cooperative Bank"]
    )
    principal_amount: Decimal = Field(..., ge=0, decimal_places=2, examples=[200000])
    interest_rate: Decimal = Field(..., ge=0, le=100, decimal_places=2, examples=[12.5])
    outstanding_amount: Decimal = Field(..., ge=0, decimal_places=2, examples=[150000])
    monthly_installment: Decimal = Field(..., ge=0, decimal_places=2, examples=[8500])
    next_due_date: date | None = Field(None, examples=["2026-06-15"])
    status: LoanStatus = Field(..., examples=[LoanStatus.ACTIVE])


class LoanUpdate(RequestModel):
    enterprise_id: UUID | None = None
    loan_type: LoanType | None = None
    lender: str | None = Field(None, min_length=2, max_length=200)
    principal_amount: Decimal | None = Field(None, ge=0, decimal_places=2)
    interest_rate: Decimal | None = Field(None, ge=0, le=100, decimal_places=2)
    outstanding_amount: Decimal | None = Field(None, ge=0, decimal_places=2)
    monthly_installment: Decimal | None = Field(None, ge=0, decimal_places=2)
    next_due_date: date | None = None
    status: LoanStatus | None = None


class LoanResponse(TimestampedResponse):
    enterprise_id: UUID
    loan_type: LoanType
    lender: str
    principal_amount: Decimal
    interest_rate: Decimal
    outstanding_amount: Decimal
    monthly_installment: Decimal
    next_due_date: date | None
    status: LoanStatus
