import logging
from typing import Set

from fastapi import APIRouter, WebSocket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

active_connections: Set[WebSocket] = set()


@router.websocket("/analytics")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    logger.info(
        f"Новое подключение: {websocket.client}. Всего подключений: {len(active_connections)}"
    )
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        logger.error(f"Ошибка в WebSocket {websocket.client}: {str(e)}")
        active_connections.discard(websocket)


async def broadcast_analytics(data: dict):
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except Exception as e:
            logger.error(
                f"Ошибка отправки данных клиенту {connection.client}: {str(e)}"
            )
