from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CommodityPrice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "commodity_prices"
    __table_args__ = (
        UniqueConstraint(
            "commodity", "district", "date", name="uq_commodity_prices_daily"
        ),
        Index(
            "ix_commodity_prices_commodity_district_date",
            "commodity",
            "district",
            "date",
        ),
        CheckConstraint("price >= 0", name="ck_commodity_prices_price_non_negative"),
    )

    commodity: Mapped[str] = mapped_column(String(160), nullable=False)
    district: Mapped[str] = mapped_column(String(120), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
