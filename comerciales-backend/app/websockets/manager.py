"""Manager de conexiones WebSocket para broadcast en tiempo real por store."""

from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Gestiona conexiones WebSocket activas, aisladas por store_id.

    Mantiene un diccionario de conexiones donde:
    - Key: store_id (identifica el local comercial)
    - Value: lista de WebSocket activos en ese local

    Permite broadcast solo a los clientes de un store específico,
    garantizando que un local no vea actualizaciones de otro.
    """

    def __init__(self):
        """Inicializa el manager con diccionario vacío de conexiones."""
        self.connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, store_id: str) -> None:
        """
        Acepta una nueva conexión WebSocket y la registra para un store.

        Args:
            websocket: Conexión WebSocket del cliente
            store_id: Identificador del local (para aislar por local)
        """
        if store_id not in self.connections:
            self.connections[store_id] = []

        self.connections[store_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, store_id: str) -> None:
        """
        Remueve una conexión WebSocket del store.

        Args:
            websocket: Conexión WebSocket a desconectar
            store_id: Identificador del local
        """
        if store_id in self.connections:
            try:
                self.connections[store_id].remove(websocket)
            except ValueError:
                # WebSocket no estaba en la lista (ok, graceful)
                pass

            # Si no hay más conexiones en el store, remover la key
            if not self.connections[store_id]:
                del self.connections[store_id]

    async def broadcast_to_store(self, store_id: str, message: dict[str, Any]) -> None:
        """
        Envía un mensaje a TODOS los clientes conectados en un store.

        Garantiza que los clientes de otros stores NO reciben el mensaje.

        Args:
            store_id: Identificador del local
            message: Diccionario JSON a enviar a los clientes
        """
        if store_id not in self.connections:
            # No hay conexiones en este store, simplemente retornar
            return

        # Enviar a todos los clientes del store
        for websocket in self.connections[store_id]:
            await websocket.send_json(message)
