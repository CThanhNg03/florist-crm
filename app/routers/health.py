from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Health check")
def get_health() -> dict[str, bool]:
    return {"ok": True}
