from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_type
from app.models.enums import WeatherCondition


class WeatherSnapshot(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "weather_snapshots"
    __table_args__ = (
        UniqueConstraint("district", "date", name="uq_weather_snapshots_district_date"),
        Index("ix_weather_snapshots_district_date", "district", "date"),
        CheckConstraint(
            "temperature >= -90 AND temperature <= 70",
            name="ck_weather_snapshots_temperature_range",
        ),
        CheckConstraint(
            "rainfall >= 0", name="ck_weather_snapshots_rainfall_non_negative"
        ),
        CheckConstraint(
            "humidity >= 0 AND humidity <= 100",
            name="ck_weather_snapshots_humidity_range",
        ),
    )

    district: Mapped[str] = mapped_column(String(120), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    temperature: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    rainfall: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    humidity: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    weather_condition: Mapped[WeatherCondition] = mapped_column(
        enum_type(WeatherCondition, "weather_condition_enum"), nullable=False
    )
