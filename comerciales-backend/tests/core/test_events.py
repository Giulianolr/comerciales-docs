"""Tests para gestión centralizada de eventos Redis (TDD - RED → GREEN → REFACTOR).
Verifica: Inicialización y acceso global al RedisPubSubManager.
"""

import pytest

from app.core.events import get_redis_manager, init_redis_manager, reset_redis_manager


class TestEventsModule:
    """Tests para el módulo centralizado de eventos."""

    @pytest.mark.asyncio
    async def test_init_redis_manager_creates_instance(self):
        """
        DADO: Sin manager inicializado
        CUANDO: Llamamos init_redis_manager()
        ENTONCES: Se crea una instancia de RedisPubSubManager y se conecta
        """
        # Limpiar antes de test
        reset_redis_manager()

        # Inicializar con fakeredis
        await init_redis_manager(use_fake=True)

        # Verificar que el manager está disponible
        manager = get_redis_manager()
        assert manager is not None
        assert manager.redis is not None

    @pytest.mark.asyncio
    async def test_get_redis_manager_returns_same_instance(self):
        """
        DADO: Un manager inicializado
        CUANDO: Llamamos get_redis_manager() múltiples veces
        ENTONCES: Retorna la misma instancia (singleton)
        """
        reset_redis_manager()
        await init_redis_manager(use_fake=True)

        manager1 = get_redis_manager()
        manager2 = get_redis_manager()

        assert manager1 is manager2

    @pytest.mark.asyncio
    async def test_get_redis_manager_returns_none_if_not_initialized(self):
        """
        DADO: Sin manager inicializado
        CUANDO: Llamamos get_redis_manager()
        ENTONCES: Retorna None (no debe lanzar excepción)
        """
        reset_redis_manager()

        manager = get_redis_manager()
        assert manager is None

    @pytest.mark.asyncio
    async def test_publish_message_through_events_module(self):
        """
        DADO: Un manager inicializado vía events module
        CUANDO: Publicamos un mensaje
        ENTONCES: El mensaje se publica correctamente
        """
        import asyncio

        reset_redis_manager()
        await init_redis_manager(use_fake=True)

        manager = get_redis_manager()
        channel = "test:channel"
        message = "Test message"
        received = []

        async def subscriber():
            async for msg in manager.subscribe(channel):
                received.append(msg)
                if len(received) == 1:
                    break

        async def publisher():
            await asyncio.sleep(0.1)
            await manager.publish(channel, message)

        await asyncio.gather(subscriber(), publisher())

        assert len(received) == 1
        assert received[0] == message

    @pytest.mark.asyncio
    async def test_reset_redis_manager(self):
        """
        DADO: Un manager inicializado
        CUANDO: Llamamos reset_redis_manager()
        ENTONCES: El manager se limpia y get_redis_manager() retorna None
        """
        await init_redis_manager(use_fake=True)
        assert get_redis_manager() is not None

        # Limpiar manager y desconectar
        reset_redis_manager()

        assert get_redis_manager() is None
