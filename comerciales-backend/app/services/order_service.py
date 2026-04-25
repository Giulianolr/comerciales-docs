"""OrderService para gestión de pre-órdenes con ítems y cálculo de totales."""

import json
import uuid
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import get_redis_manager
from app.core.redis import RedisPubSubManager
from app.models import Order, OrderItem, Product, Transaction, User
from app.schemas.order import OrderCreate, OrderItemCreate, OrderResponse


class OrderService:
    """Service para operaciones de órdenes."""

    def __init__(self, session: AsyncSession, redis_manager: Optional[RedisPubSubManager] = None):
        self.session = session
        # Si no se inyecta manager, obtenerlo de events module
        self.redis_manager = redis_manager or get_redis_manager()

    async def _set_store_context(self, store_id: UUID) -> None:
        """Inyectar store_id en contexto RLS (PostgreSQL only)."""
        try:
            await self.session.execute(
                text(f"SET LOCAL app.current_store_id = '{str(store_id)}'")
            )
        except (OperationalError, Exception):
            # Si RLS falla, continuar sin contexto
            pass

    async def _get_cart_update_payload(self, order_id: UUID, store_id: UUID) -> dict:
        """Construye el payload de un evento cart_update con todos los items de la orden.

        Nota: Asume que el contexto RLS ya ha sido establecido por el método que lo llama.

        Retorna: {
            "type": "cart_update",
            "total": "<decimal>",
            "items": [
                {
                    "id": "<uuid>",
                    "name": "<product_name>",
                    "quantity": "<decimal>",
                    "unit_price": "<decimal>",
                    "subtotal": "<decimal>"
                },
                ...
            ]
        }
        """
        # Obtener todos los items de la orden
        items_result = await self.session.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        order_items = items_result.scalars().all()

        # Construir array de items
        items = []
        for order_item in order_items:
            # Obtener el producto para su nombre (sin llamar a _set_store_context nuevamente)
            product_result = await self.session.execute(
                select(Product).where(
                    (Product.id == order_item.product_id) & (Product.store_id == store_id)
                )
            )
            product = product_result.scalars().first()

            if product:
                items.append({
                    "id": str(order_item.id),
                    "name": product.name,
                    "quantity": str(order_item.quantity),
                    "unit_price": str(order_item.unit_price),
                    "subtotal": str(order_item.subtotal),
                })

        # Obtener total de la orden
        order_result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = order_result.scalars().first()
        total = str(order.total) if order else "0.00"

        return {
            "type": "cart_update",
            "total": total,
            "items": items,
        }

    async def _publish_cart_update(self, order_id: UUID, store_id: UUID) -> None:
        """Publica evento cart_update en Redis al canal sales:{store_id}.

        Si no hay manager inicializado, no falla (graceful degradation).
        """
        if not self.redis_manager:
            return

        try:
            channel = f"sales:{store_id}"
            event_payload = await self._get_cart_update_payload(order_id, store_id)
            message = json.dumps(event_payload)
            await self.redis_manager.publish(channel, message)
        except Exception:
            # Si falla la publicación, no afecta la lógica de la orden
            pass

    async def _get_product(self, product_id: UUID, store_id: UUID) -> Product:
        """Obtener producto por ID (respeta RLS)."""
        await self._set_store_context(store_id)

        result = await self.session.execute(
            select(Product).where(
                (Product.id == product_id) & (Product.store_id == store_id)
            )
        )
        product = result.scalars().first()

        if not product:
            raise ValueError(f"Producto {product_id} no encontrado en store {store_id}")

        return product

    async def create_order(
        self, order_data: OrderCreate, store_id: UUID
    ) -> OrderResponse:
        """Crear una nueva pre-orden."""
        await self._set_store_context(store_id)

        order = Order(
            id=uuid.uuid4(),
            uuid=str(uuid.uuid4()),
            store_id=store_id,
            station_id=order_data.station_id,
            status="pending",
            total=Decimal("0.00"),
            item_count=0,
        )

        self.session.add(order)
        await self.session.flush()

        result = OrderResponse.model_validate(order)

        # Publicar evento cart_update (orden vacía al crear)
        await self._publish_cart_update(result.id, store_id)

        return result

    async def add_item_to_order(
        self, order_id: UUID, item_data: OrderItemCreate, store_id: UUID
    ) -> None:
        """Añadir un ítem a una orden, consultando el precio actual del producto."""
        await self._set_store_context(store_id)

        # Obtener el producto para consultar su precio
        product = await self._get_product(item_data.product_id, store_id)

        # Crear el ítem con el precio actual
        subtotal = product.price * Decimal(str(item_data.quantity))
        order_item = OrderItem(
            id=uuid.uuid4(),
            order_id=order_id,
            product_id=item_data.product_id,
            quantity=Decimal(str(item_data.quantity)),
            unit_price=product.price,
            unit=product.unit,
            subtotal=subtotal,
        )

        self.session.add(order_item)
        await self.session.flush()

        # Actualizar total y item_count de la orden
        result = await self.session.execute(
            select(
                func.count(OrderItem.id).label("item_count"),
                func.sum(OrderItem.subtotal).label("total"),
            ).where(OrderItem.order_id == order_id)
        )
        counts = result.first()

        order_result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = order_result.scalars().first()

        if order:
            order.item_count = counts[0] or 0
            order.total = counts[1] or Decimal("0.00")
            self.session.add(order)
            await self.session.flush()

            # Publicar evento cart_update con todos los items de la orden
            await self._publish_cart_update(order_id, store_id)

    async def get_order_by_id(self, order_id: UUID, store_id: UUID) -> OrderResponse | None:
        """Obtener orden por ID (respeta RLS)."""
        await self._set_store_context(store_id)

        result = await self.session.execute(
            select(Order).where(
                (Order.id == order_id) & (Order.store_id == store_id)
            )
        )
        order = result.scalars().first()

        if order:
            return OrderResponse.model_validate(order)

        return None

    async def checkout_order(
        self,
        order_id: UUID,
        payment_method: str,
        amount_received: Decimal,
        store_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> OrderResponse:
        """
        Procesar checkout de una orden.

        Cambia el status de 'pending' a 'completed' y crea una Transaction asociada.
        """
        await self._set_store_context(store_id)

        # Obtener la orden
        order_result = await self.session.execute(
            select(Order).where(
                (Order.id == order_id) & (Order.store_id == store_id)
            )
        )
        order = order_result.scalars().first()

        if not order:
            raise ValueError(f"Orden {order_id} no encontrada")

        # Cambiar status a completed
        order.status = "completed"
        self.session.add(order)
        await self.session.flush()

        # Calcular el cambio (si aplica)
        change_amount = None
        if amount_received > order.total:
            change_amount = amount_received - order.total

        # Crear Transaction
        transaction = Transaction(
            id=uuid.uuid4(),
            order_id=order_id,
            store_id=store_id,
            user_id=user_id or uuid.uuid4(),  # Usar user_id proporcionado o generar uno
            payment_method=payment_method,
            amount_paid=amount_received,
            change_amount=change_amount,
            status="completed",
        )

        self.session.add(transaction)
        await self.session.flush()

        return OrderResponse.model_validate(order)
