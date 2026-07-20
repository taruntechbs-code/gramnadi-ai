from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import Field, model_validator

from app.schemas.common import RequestModel, TimestampedResponse


def validate_financial_period(month: int, year: int) -> None:
    current = date.today()
    if (year, month) > (current.year, current.month):
        raise ValueError("financial records cannot be created for a future month")


class FinancialRecordCreate(RequestModel):
    enterprise_id: UUID
    month: int = Field(..., ge=1, le=12, examples=[4])
    year: int = Field(..., ge=1900, le=2100, examples=[2026])
    income: Decimal = Field(..., ge=0, decimal_places=2, examples=[125000])
    expense: Decimal = Field(..., ge=0, decimal_places=2, examples=[80000])
    profit: Decimal = Field(..., decimal_places=2, examples=[45000])
    savings: Decimal = Field(..., ge=0, decimal_places=2, examples=[25000])
    cash_balance: Decimal = Field(..., ge=0, decimal_places=2, examples=[150000])
    inventory_value: Decimal = Field(..., ge=0, decimal_places=2, examples=[90000])
    upi_transaction_count: int = Field(..., ge=0, examples=[140])
    upi_inflow: Decimal = Field(..., ge=0, decimal_places=2, examples=[90000])
    upi_outflow: Decimal = Field(..., ge=0, decimal_places=2, examples=[60000])

    @model_validator(mode="after")
    def validate_period(self) -> "FinancialRecordCreate":
        validate_financial_period(self.month, self.year)
        return self


class FinancialRecordUpdate(RequestModel):
    enterprise_id: UUID | None = None
    month: int | None = Field(None, ge=1, le=12)
    year: int | None = Field(None, ge=1900, le=2100)
    income: Decimal | None = Field(None, ge=0, decimal_places=2)
    expense: Decimal | None = Field(None, ge=0, decimal_places=2)
    profit: Decimal | None = Field(None, decimal_places=2)
    savings: Decimal | None = Field(None, ge=0, decimal_places=2)
    cash_balance: Decimal | None = Field(None, ge=0, decimal_places=2)
    inventory_value: Decimal | None = Field(None, ge=0, decimal_places=2)
    upi_transaction_count: int | None = Field(None, ge=0)
    upi_inflow: Decimal | None = Field(None, ge=0, decimal_places=2)
    upi_outflow: Decimal | None = Field(None, ge=0, decimal_places=2)

    @model_validator(mode="after")
    def validate_period_if_complete(self) -> "FinancialRecordUpdate":
        if self.month is not None and self.year is not None:
            validate_financial_period(self.month, self.year)
        return self


class FinancialRecordResponse(TimestampedResponse):
    enterprise_id: UUID
    month: int
    year: int
    income: Decimal
    expense: Decimal
    profit: Decimal
    savings: Decimal
    cash_balance: Decimal
    inventory_value: Decimal
    upi_transaction_count: int
    upi_inflow: Decimal
    upi_outflow: Decimal
