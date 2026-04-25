"""Gestión centralizada de la instancia global de RedisPubSubManager.

Proporciona un singleton para el manager de Redis Pub/Sub evitando
imports circulares. El módulo de eventos es importado por ws.py y order_service.py.
"""

from typing import Optional

from app.core.redis import RedisPubSubManager

_redis_manager: Optional[RedisPubSubManager] = None


async def init_redis_manager(use_fake: bool = False) -> None:
    """Inicializa el RedisPubSubManager global.

    Args:
        use_fake: Si True, usa fakeredis para tests. Si False, usa Redis real.
    """
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisPubSubManager(use_fake=use_fake)
        await _redis_manager.connect()


def get_redis_manager() -> Optional[RedisPubSubManager]:
    """Obtiene la instancia global del RedisPubSubManager.

    Returns:
        La instancia del manager, o None si no ha sido inicializada.
    """
    return _redis_manager


def reset_redis_manager() -> None:
    """Limpia la instancia global del manager.

    Usado principalmente en tests para reiniciar el estado.
    """
    global _redis_manager
    _redis_manager = None
