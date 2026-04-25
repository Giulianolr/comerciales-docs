"""WebSocket endpoints para actualizaciones en tiempo real."""

import asyncio
import logging
from fastapi import APIRouter, Depends, Query, WebSocketException
from starlette.websockets import WebSocket

from app.api.deps import get_db
from app.api.deps_ws import get_current_user_ws
from app.core.events import get_redis_manager
from app.websockets.manager import ConnectionManager

router = APIRouter(prefix="/ws", tags=["websocket"])
connection_manager = ConnectionManager()
logger = logging.getLogger(__name__)


async def redis_listener(store_id: str) -> None:
    """
    Escucha eventos de Redis para un store y los difunde a todos los clientes
    conectados al WebSocket de ese store.
    """
    redis_manager = get_redis_manager()

    if redis_manager is None:
        return

    channel = f"sales:{store_id}"

    try:
        async for message in redis_manager.subscribe(channel):
            import json

            try:
                event_data = json.loads(message) if isinstance(message, str) else message
            except (json.JSONDecodeError, TypeError):
                event_data = {"type": "message", "data": message}

            await connection_manager.broadcast_to_store(store_id, event_data)
    except Exception:
        pass


@router.websocket("/store/{store_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    store_id: str,
    token: str = Query(...),
    db=Depends(get_db),
) -> None:
    """
    Endpoint WebSocket para recibir actualizaciones en tiempo real.

    Flujo:
    1. Validar token y user via get_current_user_ws
    2. Verificar que user.store_id == store_id (evitar espionaje)
    3. Aceptar la conexión
    4. Conectar al ConnectionManager
    5. Escuchar eventos de Redis (nuevas ventas, etc) en background task
    6. Broadcastear a todos los clientes del store
    """
    try:
        # 1. Validar usuario autenticado
        try:
            query_params = {"token": token}
            user = await get_current_user_ws(query_params=query_params, session=db)
        except WebSocketException as e:
            logger.warning(f"WebSocket auth failed: {e.reason}")
            await websocket.close(code=1008, reason="Unauthorized")
            return
        except Exception as e:
            logger.error(f"WebSocket auth error: {e}", exc_info=True)
            await websocket.close(code=1011, reason="Auth failed")
            return

        # 2. Verificar que el user pertenece a este store_id (seguridad multi-tenant)
        if str(user.store_id) != store_id:
            await websocket.close(code=1008, reason="Store ID mismatch")
            return

        # 3. Aceptar conexión
        await websocket.accept()

        # 4. Conectar al ConnectionManager
        await connection_manager.connect(websocket, store_id)

        # 5. Iniciar task de escucha de Redis
        redis_task = asyncio.create_task(redis_listener(store_id))

        try:
            # 6. Escuchar mensajes desde el cliente
            while True:
                data = await websocket.receive_text()

        except Exception as e:
            logger.debug(f"WebSocket client disconnected: {e}")
        finally:
            # 7. Desconectar del ConnectionManager
            await connection_manager.disconnect(websocket, store_id)
            # Cancelar la task de Redis
            redis_task.cancel()
            try:
                await redis_task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        logger.error(f"Unhandled WebSocket error: {e}", exc_info=True)
        try:
            await websocket.close(code=1011, reason="Server error")
        except Exception:
            pass
