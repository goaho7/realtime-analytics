from src.api.endpoints import analytic_router
from fastapi import APIRouter

main_router = APIRouter(prefix="/api")

main_router.include_router(analytic_router, prefix="/stats", tags=["Stats"])
