from collections.abc import Sequence
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.base import Base, utc_now
from app.services.exceptions import ConflictError, ResourceNotFoundError

ModelT = TypeVar("ModelT", bound=Base)
CreateT = TypeVar("CreateT", bound=BaseModel)
UpdateT = TypeVar("UpdateT", bound=BaseModel)


class CRUDService(Generic[ModelT, CreateT, UpdateT]):
    model: type[ModelT]
    resource_name: str

    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, *, skip: int = 0, limit: int = 100) -> Sequence[ModelT]:
        statement = (
            select(self.model)
            .where(self.model.deleted_at.is_(None))
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.db.scalars(statement).all()

    def get(self, resource_id: UUID) -> ModelT:
        statement = select(self.model).where(
            self.model.id == resource_id, self.model.deleted_at.is_(None)
        )
        resource = self.db.scalar(statement)
        if resource is None:
            raise ResourceNotFoundError(self.resource_name, resource_id)
        return resource

    def create(self, payload: CreateT) -> ModelT:
        resource = self.model(**payload.model_dump())
        self.db.add(resource)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError(
                f"Unable to create {self.resource_name}; a related or unique "
                "value conflicts"
            ) from exc
        self.db.refresh(resource)
        return resource

    def update(self, resource_id: UUID, payload: UpdateT) -> ModelT:
        resource = self.get(resource_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(resource, field, value)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError(
                f"Unable to update {self.resource_name}; a related or unique "
                "value conflicts"
            ) from exc
        self.db.refresh(resource)
        return resource

    def soft_delete(self, resource_id: UUID) -> None:
        resource = self.get(resource_id)
        resource.deleted_at = utc_now()
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError(f"Unable to delete {self.resource_name}") from exc
