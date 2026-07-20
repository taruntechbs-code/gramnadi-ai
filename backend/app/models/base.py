from datetime import datetime, timezone
from enum import Enum as PythonEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def enum_type(enum_cls: type[PythonEnum], name: str) -> SQLAlchemyEnum:
    return SQLAlchemyEnum(
        enum_cls,
        name=name,
        native_enum=True,
        values_callable=lambda members: [member.value for member in members],
    )


class Base(DeclarativeBase):
    """Declarative base for all persistence models."""


class UUIDPrimaryKeyMixin:
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
