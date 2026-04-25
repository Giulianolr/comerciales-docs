"""Tests para WebSocket ConnectionManager (TDD - RED → GREEN → REFACTOR).
Verifica: Conexiones, desconexiones y broadcast por store_id.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.websockets.manager import ConnectionManager


@pytest.fixture
def connection_manager():
    """Crea un ConnectionManager para tests."""
    return ConnectionManager()


@pytest.fixture
def mock_websocket():
    """Crea un mock de WebSocket."""
    ws = MagicMock()
    ws.send_json = AsyncMock()
    return ws


class TestConnectionManager:
    """Tests para ConnectionManager."""

    @pytest.mark.asyncio
    async def test_connect_stores_websocket(
        self, connection_manager: ConnectionManager, mock_websocket
    ):
        """
        DADO: Un ConnectionManager vacío
        CUANDO: Conectamos un WebSocket a un store
        ENTONCES: El WebSocket se almacena en el diccionario del store
        """
        store_id = "store_A"

        await connection_manager.connect(mock_websocket, store_id)

        # Verificar que la conexión está almacenada
        assert store_id in connection_manager.connections
        assert mock_websocket in connection_manager.connections[store_id]

    @pytest.mark.asyncio
    async def test_connect_multiple_clients_same_store(
        self, connection_manager: ConnectionManager
    ):
        """
        DADO: Un ConnectionManager
        CUANDO: Conectamos múltiples WebSockets al mismo store
        ENTONCES: Todos se almacenan en la lista del store
        """
        store_id = "store_A"
        ws1 = MagicMock()
        ws1.send_json = AsyncMock()
        ws2 = MagicMock()
        ws2.send_json = AsyncMock()

        await connection_manager.connect(ws1, store_id)
        await connection_manager.connect(ws2, store_id)

        # Verificar que ambos están almacenados
        assert len(connection_manager.connections[store_id]) == 2
        assert ws1 in connection_manager.connections[store_id]
        assert ws2 in connection_manager.connections[store_id]

    @pytest.mark.asyncio
    async def test_disconnect_removes_websocket(
        self, connection_manager: ConnectionManager
    ):
        """
        DADO: Un store con conexiones activas
        CUANDO: Desconectamos un WebSocket
        ENTONCES: Se remove de la lista del store
        """
        store_id = "store_A"
        ws1 = MagicMock()
        ws1.send_json = AsyncMock()
        ws2 = MagicMock()
        ws2.send_json = AsyncMock()

        await connection_manager.connect(ws1, store_id)
        await connection_manager.connect(ws2, store_id)

        # Verificar que están conectados
        assert len(connection_manager.connections[store_id]) == 2

        # Desconectar ws1
        await connection_manager.disconnect(ws1, store_id)

        # Verificar que se removió
        assert ws1 not in connection_manager.connections[store_id]
        assert ws2 in connection_manager.connections[store_id]
        assert len(connection_manager.connections[store_id]) == 1

        # Desconectar ws2 (último)
        await connection_manager.disconnect(ws2, store_id)

        # Cuando no hay más conexiones, la key se elimina
        assert store_id not in connection_manager.connections

    @pytest.mark.asyncio
    async def test_broadcast_to_store_sends_to_all_clients_in_store(
        self, connection_manager: ConnectionManager
    ):
        """
        DADO: Dos clients en store_A y uno en store_B
        CUANDO: Hacemos broadcast a store_A
        ENTONCES: Solo los dos clients de store_A reciben el mensaje
        """
        store_a_id = "store_A"
        store_b_id = "store_B"

        # Crear mocks
        client_a1 = MagicMock()
        client_a1.send_json = AsyncMock()
        client_a2 = MagicMock()
        client_a2.send_json = AsyncMock()
        client_b1 = MagicMock()
        client_b1.send_json = AsyncMock()

        # Conectar
        await connection_manager.connect(client_a1, store_a_id)
        await connection_manager.connect(client_a2, store_a_id)
        await connection_manager.connect(client_b1, store_b_id)

        # Broadcast a store_A
        message = {"type": "update", "data": "Inventario actualizado"}
        await connection_manager.broadcast_to_store(store_a_id, message)

        # Verificar que SOLO los clientes de store_A recibieron
        client_a1.send_json.assert_called_once_with(message)
        client_a2.send_json.assert_called_once_with(message)
        client_b1.send_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_broadcast_to_store_with_no_clients(
        self, connection_manager: ConnectionManager
    ):
        """
        DADO: Un store sin conexiones
        CUANDO: Hacemos broadcast a ese store
        ENTONCES: No hay error (simplemente no envía a nadie)
        """
        store_id = "empty_store"
        message = {"type": "update", "data": "Mensaje"}

        # Broadcast a un store sin clientes (no debe fallar)
        await connection_manager.broadcast_to_store(store_id, message)

        # Si llegamos aquí, no hubo excepción
        assert True

    @pytest.mark.asyncio
    async def test_broadcast_isolation_between_stores(
        self, connection_manager: ConnectionManager
    ):
        """
        CRÍTICA: Verificar que broadcast en store_A NO afecta store_B.

        DADO: Dos stores con clientes
        CUANDO: Hacemos broadcast en store_A
        ENTONCES: Los clientes de store_B NO reciben el mensaje
        """
        store_a = "store_A"
        store_b = "store_B"

        client_a = MagicMock()
        client_a.send_json = AsyncMock()
        client_b = MagicMock()
        client_b.send_json = AsyncMock()

        await connection_manager.connect(client_a, store_a)
        await connection_manager.connect(client_b, store_b)

        message = {"type": "sale", "store": "A"}
        await connection_manager.broadcast_to_store(store_a, message)

        # client_a recibe, client_b NO
        client_a.send_json.assert_called_once_with(message)
        client_b.send_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_websocket_does_not_error(
        self, connection_manager: ConnectionManager, mock_websocket
    ):
        """
        DADO: Un WebSocket que nunca se conectó
        CUANDO: Intentamos desconectarlo
        ENTONCES: No hay error (graceful)
        """
        store_id = "store_A"

        # Intentar desconectar un WebSocket que nunca se conectó
        # Esto NO debe fallar
        await connection_manager.disconnect(mock_websocket, store_id)

        assert True  # Si llegamos aquí, no hubo excepción
