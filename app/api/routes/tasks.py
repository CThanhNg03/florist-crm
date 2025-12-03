from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_db
from app.db.models.crm_orders import CrmOrder
from app.db.models.florists import Florist
from app.db.models.tasks import Task, TaskStatus
from app.schemas.tasks import (
    AssignTaskPayload,
    Task as TaskSchema,
    TaskCreate,
    TaskNotesUpdate,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.services.storage import LocalStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])


async def _get_task(session: AsyncSession, task_id: int) -> Task:
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


async def _validate_relationships(
    session: AsyncSession, order_id: int | None = None, florist_id: int | None = None
) -> None:
    if order_id is not None:
        order = await session.get(CrmOrder, order_id)
        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if florist_id is not None:
        florist = await session.get(Florist, florist_id)
        if florist is None or not florist.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Florist not found or inactive")


@router.get("", response_model=list[TaskSchema])
async def list_tasks(db: AsyncSession = Depends(get_async_db)) -> list[Task]:
    result = await db.execute(select(Task))
    return result.scalars().all()


@router.post("", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, db: AsyncSession = Depends(get_async_db)) -> Task:
    await _validate_relationships(db, order_id=payload.orderId, florist_id=payload.floristId)
    task = Task(
        title=payload.title,
        status=payload.status or TaskStatus.PENDING,
        schedule=payload.schedule,
        pricing=payload.pricing,
        notes=payload.notes,
        photos=payload.photos or [],
        order_id=payload.orderId,
        florist_id=payload.floristId,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(task_id: int, db: AsyncSession = Depends(get_async_db)) -> Task:
    return await _get_task(db, task_id)


@router.patch("/{task_id}", response_model=TaskSchema)
async def update_task(task_id: int, payload: TaskUpdate, db: AsyncSession = Depends(get_async_db)) -> Task:
    task = await _get_task(db, task_id)
    await _validate_relationships(db, order_id=payload.orderId, florist_id=payload.floristId)

    field_map = {"orderId": "order_id", "floristId": "florist_id", "completionProofUrl": "completion_proof_url"}

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "photos" and value is None:
            continue
        target_attr = field_map.get(field, field)
        setattr(task, target_attr, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/{task_id}/status", response_model=TaskSchema)
async def update_status(task_id: int, payload: TaskStatusUpdate, db: AsyncSession = Depends(get_async_db)) -> Task:
    task = await _get_task(db, task_id)
    task.status = payload.status
    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/{task_id}/notes", response_model=TaskSchema)
async def update_notes(task_id: int, payload: TaskNotesUpdate, db: AsyncSession = Depends(get_async_db)) -> Task:
    task = await _get_task(db, task_id)
    task.notes = payload.notes
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/{task_id}/assign", response_model=TaskSchema)
async def assign_task(task_id: int, payload: AssignTaskPayload, db: AsyncSession = Depends(get_async_db)) -> Task:
    task = await _get_task(db, task_id)
    if payload.floristId is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="floristId is required")
    await _validate_relationships(db, florist_id=payload.floristId)
    task.florist_id = payload.floristId
    task.status = TaskStatus.ASSIGNED
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/{task_id}/unassign", response_model=TaskSchema)
async def unassign_task(task_id: int, payload: AssignTaskPayload, db: AsyncSession = Depends(get_async_db)) -> Task:
    task = await _get_task(db, task_id)
    task.florist_id = None
    if task.status == TaskStatus.ASSIGNED:
        task.status = TaskStatus.PENDING
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/{task_id}/complete", response_model=TaskSchema)
async def complete_task(
    task_id: int,
    photo: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
) -> Task:
    task = await _get_task(db, task_id)
    storage = LocalStorage()
    completion_url = await storage.save_completion_image(task_id, photo)
    task.completion_proof_url = completion_url
    task.status = TaskStatus.COMPLETED
    await db.commit()
    await db.refresh(task)
    return task
