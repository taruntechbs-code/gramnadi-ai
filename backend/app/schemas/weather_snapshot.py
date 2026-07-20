from datetime import date as Date
from decimal import Decimal

from pydantic import Field

from app.models.enums import WeatherCondition
from app.schemas.common import RequestModel, TimestampedResponse


class WeatherSnapshotCreate(RequestModel):
    district: str = Field(..., min_length=2, max_length=120, examples=["Pune"])
    date: Date = Field(..., examples=["2026-05-01"])
    temperature: Decimal = Field(..., ge=-90, le=70, decimal_places=2, examples=[31.5])
    rainfall: Decimal = Field(..., ge=0, decimal_places=2, examples=[4.2])
    humidity: Decimal = Field(..., ge=0, le=100, decimal_places=2, examples=[64])
    weather_condition: WeatherCondition = Field(..., examples=[WeatherCondition.CLOUDY])


class WeatherSnapshotUpdate(RequestModel):
    district: str | None = Field(None, min_length=2, max_length=120)
    date: Date | None = None
    temperature: Decimal | None = Field(None, ge=-90, le=70, decimal_places=2)
    rainfall: Decimal | None = Field(None, ge=0, decimal_places=2)
    humidity: Decimal | None = Field(None, ge=0, le=100, decimal_places=2)
    weather_condition: WeatherCondition | None = None


class WeatherSnapshotResponse(TimestampedResponse):
    district: str
    date: Date
    temperature: Decimal
    rainfall: Decimal
    humidity: Decimal
    weather_condition: WeatherCondition
