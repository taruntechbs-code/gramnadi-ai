from datetime import date as Date
from decimal import Decimal

from pydantic import Field

from app.schemas.common import RequestModel, TimestampedResponse


class CommodityPriceCreate(RequestModel):
    commodity: str = Field(..., min_length=2, max_length=160, examples=["Wheat"])
    district: str = Field(..., min_length=2, max_length=120, examples=["Pune"])
    date: Date = Field(..., examples=["2026-05-01"])
    price: Decimal = Field(..., ge=0, decimal_places=2, examples=[2450])


class CommodityPriceUpdate(RequestModel):
    commodity: str | None = Field(None, min_length=2, max_length=160)
    district: str | None = Field(None, min_length=2, max_length=120)
    date: Date | None = None
    price: Decimal | None = Field(None, ge=0, decimal_places=2)


class CommodityPriceResponse(TimestampedResponse):
    commodity: str
    district: str
    date: Date
    price: Decimal
