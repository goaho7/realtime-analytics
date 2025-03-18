from src.api.endpoints import analytic_router
from src.api.web_socket import ws_analytics_router
from fastapi import APIRouter

main_router = APIRouter(prefix="/api")

main_router.include_router(analytic_router, prefix="/stats", tags=["Stats"])
main_router.include_router(ws_analytics_router, prefix="/ws_stats", tags=["WsStats"])
