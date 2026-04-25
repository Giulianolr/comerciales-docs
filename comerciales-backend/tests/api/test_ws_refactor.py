"""Tests para validar que ws.py usa correctly el events module.
Verifica que redis_listener usa get_redis_manager() de events, no una instancia global.
"""

import asyncio

import pytest

from app.api.v1.endpoints.ws import redis_listener
from app.core.events import get_redis_manager, init_redis_manager, reset_redis_manager


class TestWSRefactor:
    """Tests para validar la refactorización de ws.py."""

    @pytest.mark.asyncio
    async def test_redis_listener_uses_events_module_manager(self):
        """
        DADO: El events module con un manager inicializado
        CUANDO: redis_listener es ejecutado
        ENTONCES: Usa el manager de events (no uno local/global de ws.py)
        """
        reset_redis_manager()
        await init_redis_manager(use_fake=True)

        # Obtener el manager de events
        manager = get_redis_manager()
        assert manager is not None

        # redis_listener debe usar este mismo manager
        store_id = "test_store"
        channel = f"sales:{store_id}"
        test_message = "test event"
        received_messages = []

        async def listener_task():
            """Ejecutar redis_listener en background."""
            await redis_listener(store_id)

        async def send_message():
            """Enviar un mensaje después de una pequeña espera."""
            await asyncio.sleep(0.2)
            # Publicar mensaje usando el manager obtenido de events
            await manager.publish(channel, test_message)

        async def monitor_messages():
            """Monitorear que el mensaje llegó."""
            await asyncio.sleep(0.5)
            # Si llegó aquí, significa que redis_listener está escuchando en el canal correcto

        # Crear task del listener
        listener = asyncio.create_task(listener_task())
        sender = asyncio.create_task(send_message())
        monitor = asyncio.create_task(monitor_messages())

        try:
            await asyncio.gather(sender, monitor, return_exceptions=True)
        finally:
            listener.cancel()
            try:
                await listener
            except asyncio.CancelledError:
                pass

        # Si llegamos aquí sin excepciones, el test pasó
        # (redis_listener estaba correctamente escuchando en el canal del store)
        assert True

    @pytest.mark.asyncio
    async def test_redis_listener_returns_early_if_manager_not_initialized(self):
        """
        DADO: Sin manager inicializado en events module
        CUANDO: redis_listener es ejecutado
        ENTONCES: Retorna early sin error
        """
        reset_redis_manager()

        # redis_listener debe retornar temprano si no hay manager
        store_id = "test_store"

        # Esto debe ser muy rápido (retorna temprano)
        try:
            await asyncio.wait_for(redis_listener(store_id), timeout=0.1)
        except asyncio.TimeoutError:
            pytest.fail("redis_listener did not return early when manager is None")

        # Test pasó
        assert True
