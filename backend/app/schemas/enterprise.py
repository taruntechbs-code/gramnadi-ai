from datetime import date
from decimal import Decimal

from pydantic import Field, field_validator

from app.models.enums import EnterpriseType, Sector
from app.schemas.common import RequestModel, TimestampedResponse


class EnterpriseCreate(RequestModel):
    enterprise_code: str = Field(
        ..., min_length=2, max_length=50, examples=["ENT-MH-0001"]
    )
    name: str = Field(..., min_length=2, max_length=200, examples=["Shakti Foods"])
    owner_name: str = Field(..., min_length=2, max_length=200, examples=["Asha Patil"])
    enterprise_type: EnterpriseType = Field(
        ..., examples=[EnterpriseType.FOOD_PROCESSING]
    )
    district: str = Field(..., min_length=2, max_length=120, examples=["Pune"])
    state: str = Field(..., min_length=2, max_length=120, examples=["Maharashtra"])
    village: str = Field(..., min_length=2, max_length=120, examples=["Khed"])
    sector: Sector = Field(..., examples=[Sector.FOOD_AND_BEVERAGE])
    business_start_date: date = Field(..., examples=["2020-04-01"])
    employees: int = Field(..., ge=0, le=1_000_000, examples=[5])
    annual_turnover: Decimal = Field(..., ge=0, decimal_places=2, examples=[250000])

    @field_validator("business_start_date")
    @classmethod
    def validate_start_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("business_start_date cannot be in the future")
        return value


class EnterpriseUpdate(RequestModel):
    enterprise_code: str | None = Field(None, min_length=2, max_length=50)
    name: str | None = Field(None, min_length=2, max_length=200)
    owner_name: str | None = Field(None, min_length=2, max_length=200)
    enterprise_type: EnterpriseType | None = None
    district: str | None = Field(None, min_length=2, max_length=120)
    state: str | None = Field(None, min_length=2, max_length=120)
    village: str | None = Field(None, min_length=2, max_length=120)
    sector: Sector | None = None
    business_start_date: date | None = None
    employees: int | None = Field(None, ge=0, le=1_000_000)
    annual_turnover: Decimal | None = Field(None, ge=0, decimal_places=2)

    @field_validator("business_start_date")
    @classmethod
    def validate_start_date(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("business_start_date cannot be in the future")
        return value


class EnterpriseResponse(TimestampedResponse):
    enterprise_code: str
    name: str
    owner_name: str
    enterprise_type: EnterpriseType
    district: str
    state: str
    village: str
    sector: Sector
    business_start_date: date
    employees: int
    annual_turnover: Decimal
