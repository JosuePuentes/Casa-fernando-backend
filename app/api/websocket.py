"""WebSocket para notificaciones en tiempo real a mesoneras."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Set
import json

router = APIRouter(tags=["WebSocket"])

# Conexiones activas de mesoneras (reciben notificaciones y vibración)
mesonera_connections: Set[WebSocket] = set()


@router.websocket("/ws/mesonera")
async def websocket_mesonera(websocket: WebSocket):
    """
    WebSocket para módulo de mesonera.
    Al conectarse, recibe notificaciones en tiempo real cuando un cliente
    presiona el botón de llamar. El frontend puede usar la API de vibración
    del navegador (navigator.vibrate) al recibir el mensaje.
    """
    await websocket.accept()
    mesonera_connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # El cliente puede enviar ping para mantener conexión
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        mesonera_connections.discard(websocket)


async def broadcast_notificacion_mesonera(mesa_id: int | None, mensaje: str, notif_id: int):
    """Enviar notificación a todas las mesoneras conectadas (para vibración)."""
    msg = json.dumps({
        "type": "notificacion_cliente",
        "vibrar": True,
        "mesa_id": mesa_id,
        "mensaje": mensaje,
        "id": notif_id,
    })
    disconnected = set()
    for ws in mesonera_connections:
        try:
            await ws.send_text(msg)
        except Exception:
            disconnected.add(ws)
    for ws in disconnected:
        mesonera_connections.discard(ws)
