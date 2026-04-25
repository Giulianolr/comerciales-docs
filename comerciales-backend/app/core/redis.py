"""Configuración de Redis y RedisPubSubManager para pub/sub en tiempo real."""

from typing import AsyncGenerator, Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from redis.asyncio import Redis


class RedisConfig(BaseSettings):
    """Configuración de Redis desde variables de entorno."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    decode_responses: bool = True

    model_config = ConfigDict(env_prefix="REDIS_", case_sensitive=False)

    @property
    def url(self) -> str:
        """Construye la URL de Redis."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class RedisPubSubManager:
    """Manager para publicar y suscribirse a canales Redis en tiempo real."""

    def __init__(self, config: Optional[RedisConfig] = None, use_fake: bool = False):
        """
        Inicializa el manager.

        Args:
            config: Configuración de Redis (si es None, se crea una por defecto)
            use_fake: Si True, usa fakeredis para tests (no requiere servidor real)
        """
        self.config = config or RedisConfig()
        self.use_fake = use_fake
        self.redis: Optional[Redis] = None
        self.pubsub = None

    async def connect(self) -> None:
        """Conecta a Redis (real o fake)."""
        if self.use_fake:
            # Para tests: usar fakeredis
            import fakeredis.aioredis

            self.redis = fakeredis.aioredis.FakeRedis(decode_responses=self.config.decode_responses)
        else:
            # Para producción: usar Redis real
            self.redis = Redis.from_url(self.url, decode_responses=self.config.decode_responses)
            await self.redis.ping()

    async def close(self) -> None:
        """Cierra la conexión a Redis."""
        if self.redis:
            await self.redis.aclose()
            self.redis = None

    async def publish(self, channel: str, message: str) -> int:
        """
        Publica un mensaje en un canal.

        Args:
            channel: Nombre del canal
            message: Mensaje a publicar

        Returns:
            Número de suscriptores que recibieron el mensaje
        """
        if not self.redis:
            raise RuntimeError("Redis not connected. Call connect() first.")

        return await self.redis.publish(channel, message)

    async def subscribe(self, channel: str) -> AsyncGenerator[str, None]:
        """
        Se suscribe a un canal y recibe mensajes.

        Args:
            channel: Nombre del canal a suscribirse

        Yields:
            Mensajes recibidos en el canal
        """
        if not self.redis:
            raise RuntimeError("Redis not connected. Call connect() first.")

        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)

        try:
            # Escuchar mensajes indefinidamente
            async for message in pubsub.listen():
                # Ignorar mensajes de sistema (subscribe, unsubscribe)
                if message["type"] == "message":
                    yield message["data"]
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()
