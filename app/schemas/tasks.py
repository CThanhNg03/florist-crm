from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.task import TaskStatus


class AssignTaskPayload(BaseModel):
    floristId: int | None = Field(default=None)


class TaskBase(BaseModel):
    title: str | None = Field(default=None)
    status: TaskStatus | None = Field(default=None)
    schedule: datetime | None = Field(default=None)
    pricing: int | None = Field(default=None)
    notes: str | None = Field(default=None)
    photos: List[str] | None = Field(default=None)
    orderId: int | None = Field(default=None, validation_alias="order_id")
    floristId: int | None = Field(default=None, validation_alias="florist_id")

    model_config = ConfigDict(populate_by_name=True)


class TaskCreate(TaskBase):
    title: str
    status: TaskStatus | None = Field(default=TaskStatus.PENDING)
    photos: List[str] | None = Field(default_factory=list)


class TaskUpdate(TaskBase):
    pass


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskNotesUpdate(BaseModel):
    notes: str


class TaskCompletionPayload(BaseModel):
    completionProofUrl: str = Field(validation_alias="completion_proof_url")


class Task(BaseModel):
    id: int
    title: str
    status: TaskStatus
    schedule: datetime | None
    pricing: int | None
    notes: str | None
    photos: List[str]
    completionProofUrl: str | None = Field(default=None, validation_alias="completion_proof_url")
    floristId: int | None = Field(default=None, validation_alias="florist_id")
    orderId: int | None = Field(default=None, validation_alias="order_id")
    createdAt: datetime = Field(validation_alias="created_at")
    updatedAt: datetime = Field(validation_alias="updated_at")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
