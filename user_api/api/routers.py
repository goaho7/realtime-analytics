from api.endpoints import event_router
from fastapi import APIRouter

main_router = APIRouter(prefix="/api")

main_router.include_router(event_router, prefix="/event", tags=["Event"])
