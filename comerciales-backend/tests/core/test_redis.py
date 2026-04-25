"""Tests para Redis PubSub Manager (TDD - RED → GREEN → REFACTOR).
Verifica: Publicar y suscribirse a canales en tiempo real.
"""

import asyncio

import pytest

from app.core.redis import RedisPubSubManager


@pytest.fixture
async def redis_manager():
    """Crea un RedisPubSubManager con fakeredis para tests."""
    manager = RedisPubSubManager(use_fake=True)
    await manager.connect()
    yield manager
    await manager.close()


class TestRedisPubSubManager:
    """Tests para RedisPubSubManager."""

    @pytest.mark.asyncio
    async def test_publish_and_subscribe_message(self, redis_manager: RedisPubSubManager):
        """
        DADO: Un RedisPubSubManager conectado
        CUANDO: Publicamos un mensaje en un canal
        ENTONCES: Los suscriptores reciben el mensaje correctamente
        """
        channel = "test_channel"
        message = "Hola, esto es un mensaje de prueba"
        received_messages = []

        async def subscriber():
            """Suscriptor que escucha el canal."""
            async for msg in redis_manager.subscribe(channel):
                received_messages.append(msg)
                if len(received_messages) == 1:
                    break  # Salir después de recibir 1 mensaje

        async def publisher():
            """Publicador que espera un poco y luego envía."""
            await asyncio.sleep(0.1)  # Dar tiempo al suscriptor a conectarse
            await redis_manager.publish(channel, message)

        # Ejecutar suscriptor y publicador en paralelo
        await asyncio.gather(subscriber(), publisher())

        # Verificar que se recibió el mensaje
        assert len(received_messages) == 1
        assert received_messages[0] == message

    @pytest.mark.asyncio
    async def test_publish_before_subscribe(self, redis_manager: RedisPubSubManager):
        """
        DADO: Un canal sin suscriptores
        CUANDO: Publicamos un mensaje
        ENTONCES: El mensaje se envía sin error (aunque nadie lo reciba)
        """
        channel = "empty_channel"
        message = "Mensaje sin suscriptores"

        # Esto no debe fallar
        result = await redis_manager.publish(channel, message)

        # publish() retorna el número de suscriptores que recibieron el mensaje
        # En este caso, 0 porque no hay suscriptores
        assert result == 0

    @pytest.mark.asyncio
    async def test_multiple_subscribers_same_channel(
        self, redis_manager: RedisPubSubManager
    ):
        """
        DADO: Múltiples suscriptores en el mismo canal
        CUANDO: Publicamos un mensaje
        ENTONCES: Todos los suscriptores reciben el mensaje
        """
        channel = "multi_sub_channel"
        message = "Mensaje para múltiples suscriptores"
        subscriber_1_messages = []
        subscriber_2_messages = []

        async def sub_1():
            async for msg in redis_manager.subscribe(channel):
                subscriber_1_messages.append(msg)
                if len(subscriber_1_messages) == 1:
                    break

        async def sub_2():
            async for msg in redis_manager.subscribe(channel):
                subscriber_2_messages.append(msg)
                if len(subscriber_2_messages) == 1:
                    break

        async def pub():
            await asyncio.sleep(0.1)
            await redis_manager.publish(channel, message)

        # Ejecutar suscriptores y publicador en paralelo
        await asyncio.gather(sub_1(), sub_2(), pub())

        # Ambos suscriptores deben recibir el mensaje
        assert len(subscriber_1_messages) == 1
        assert len(subscriber_2_messages) == 1
        assert subscriber_1_messages[0] == message
        assert subscriber_2_messages[0] == message

    @pytest.mark.asyncio
    async def test_different_channels_isolation(self, redis_manager: RedisPubSubManager):
        """
        DADO: Dos canales diferentes
        CUANDO: Publicamos en un canal
        ENTONCES: Los suscriptores del otro canal NO reciben el mensaje
        """
        channel_a = "channel_a"
        channel_b = "channel_b"
        message_a = "Mensaje en canal A"
        message_b = "Mensaje en canal B"
        messages_a = []
        messages_b = []

        async def sub_a():
            async for msg in redis_manager.subscribe(channel_a):
                messages_a.append(msg)
                if len(messages_a) == 1:
                    break

        async def sub_b():
            async for msg in redis_manager.subscribe(channel_b):
                messages_b.append(msg)
                if len(messages_b) == 1:
                    break

        async def pub():
            await asyncio.sleep(0.1)
            await redis_manager.publish(channel_a, message_a)
            await asyncio.sleep(0.05)
            await redis_manager.publish(channel_b, message_b)

        # Ejecutar en paralelo
        await asyncio.gather(sub_a(), sub_b(), pub())

        # Cada suscriptor debe recibir SOLO su mensaje
        assert len(messages_a) == 1
        assert messages_a[0] == message_a
        assert len(messages_b) == 1
        assert messages_b[0] == message_b
