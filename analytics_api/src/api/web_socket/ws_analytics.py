from typing import Set

from fastapi import APIRouter, WebSocket


router = APIRouter()

active_connections: Set[WebSocket] = set()


@router.websocket("/analytics")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        active_connections.remove(websocket)
        await websocket.close()


async def broadcast_analytics(data: dict):
    for connection in active_connections:
        await connection.send_json(data)
