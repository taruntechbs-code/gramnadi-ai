from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TimestampedResponse(ORMResponse):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
