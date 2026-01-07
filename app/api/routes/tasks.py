from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_use_cases
from app.schemas.tasks import (
    AssignTaskPayload,
    Task as TaskSchema,
    TaskCompletionPayload,
    TaskCreate,
    TaskNotesUpdate,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.use_cases.exceptions import NotFoundError, ValidationError
from app.use_cases.factory import UseCaseFactory

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _handle_errors(exc: Exception) -> None:
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ValidationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    raise exc


@router.get("", response_model=list[TaskSchema])
async def list_tasks(use_cases: UseCaseFactory = Depends(get_use_cases)) -> list[TaskSchema]:
    use_case = use_cases.list_tasks()
    tasks = await use_case.execute()
    return tasks


@router.post("", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate, use_cases: UseCaseFactory = Depends(get_use_cases)
) -> TaskSchema:
    use_case = use_cases.create_task()
    try:
        return await use_case.execute(
            title=payload.title,
            status=payload.status,
            schedule=payload.schedule,
            pricing=payload.pricing,
            notes=payload.notes,
            photos=payload.photos,
            order_id=payload.orderId,
            florist_id=payload.floristId,
        )
    except Exception as exc:  # noqa: BLE001
        _handle_errors(exc)


@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(task_id: int, use_cases: UseCaseFactory = Depends(get_use_cases)) -> TaskSchema:
    use_case = use_cases.get_task()
    try:
        return await use_case.execute(task_id)
    except Exception as exc:  # noqa: BLE001
        _handle_errors(exc)


@router.patch("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: int, payload: TaskUpdate, use_cases: UseCaseFactory = Depends(get_use_cases)
) -> TaskSchema:
    use_case = use_cases.update_task()
    updates = payload.model_dump(exclude_unset=True)
    field_map = {"orderId": "order_id", "floristId": "florist_id", "completionProofUrl": "completion_proof_url"}
    normalized_updates = {field_map.get(key, key): value for key, value in updates.items()}
    try:
        return await use_case.execute(task_id, normalized_updates)
    except Exception as exc:  # noqa: BLE001
        _handle_errors(exc)


@router.patch("/{task_id}/status", response_model=TaskSchema)
async def update_status(
    task_id: int, payload: TaskStatusUpdate, use_cases: UseCaseFactory = Depends(get_use_cases)
) -> TaskSchema:
    use_case = use_cases.update_task_status()
    try:
        return await use_case.execute(task_id, payload.status)
    except Exception as exc:  # noqa: BLE001
        _handle_errors(exc)


@router.patch("/{task_id}/notes", response_model=TaskSchema)
async def update_notes(
    task_id: int, payload: TaskNotesUpdate, use_cases: UseCaseFactory = Depends(get_use_cases)
) -> TaskSchema:
    use_case = use_cases.update_task_notes()
    try:
        return await use_case.execute(task_id, payload.notes)
    except Exception as exc:  # noqa: BLE001
        _handle_errors(exc)


@router.post("/{task_id}/assign", response_model=TaskSchema)
async def assign_task(
    task_id: int, payload: AssignTaskPayload, use_cases: UseCaseFactory = Depends(get_use_cases)
) -> TaskSchema:
    use_case = use_cases.assign_task()
    try:
        return await use_case.execute(task_id, payload.floristId)
    except Exception as exc:  # noqa: BLE001
        _handle_errors(exc)


@router.post("/{task_id}/unassign", response_model=TaskSchema)
async def unassign_task(task_id: int, use_cases: UseCaseFactory = Depends(get_use_cases)) -> TaskSchema:
    use_case = use_cases.unassign_task()
    try:
        return await use_case.execute(task_id)
    except Exception as exc:  # noqa: BLE001
        _handle_errors(exc)


@router.post("/{task_id}/complete", response_model=TaskSchema)
async def complete_task(
    task_id: int,
    payload: TaskCompletionPayload,
    use_cases: UseCaseFactory = Depends(get_use_cases),
) -> TaskSchema:
    use_case = use_cases.complete_task()
    try:
        return await use_case.execute(task_id, payload.completionProofUrl)
    except Exception as exc:  # noqa: BLE001
        _handle_errors(exc)
