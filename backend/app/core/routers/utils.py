from fastapi import APIRouter
from app.crud import healthchecker
from app.utils.deps import SessionDep

router = APIRouter(prefix="/utils", tags=["utils"])


@router.get("/health")
async def health_check(session: SessionDep) -> bool:
    return healthchecker(session)


@router.get("/auth")
async def check() -> dict:
    return {
        "message": "我懒得写验证了,你直接进来吧",
        "ok": True,
    }
