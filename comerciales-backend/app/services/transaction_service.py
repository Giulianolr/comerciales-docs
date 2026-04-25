"""TransactionService para procesar pagos y consolidar órdenes."""

import uuid
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import InventoryMovement, Order, OrderItem, Product, Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse


class TransactionService:
    """Service para operaciones de transacciones (caja registradora)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _set_store_context(self, store_id: UUID) -> None:
        """Inyectar store_id en contexto RLS (PostgreSQL only)."""
        try:
            await self.session.execute(
                text(f"SET LOCAL app.current_store_id = '{store_id}'")
            )
        except OperationalError:
            pass

    async def process_payment(
        self,
        order_id: UUID,
        transaction_data: TransactionCreate,
        user_id: UUID,
        store_id: UUID,
    ) -> TransactionResponse:
        """
        Procesar pago de una orden: consolidar venta, descontar stock, registrar auditoría.
        
        TODA la operación ocurre en UNA SOLA transacción SQLAlchemy.
        Si algo falla, el rollback automático deja todo intacto.
        """
        await self._set_store_context(store_id)

        # Validación: amount_paid debe ser positivo
        if transaction_data.amount_paid <= 0:
            raise ValueError("amount_paid debe ser mayor que cero")

        # Obtener la orden
        order_result = await self.session.execute(
            select(Order).where((Order.id == order_id) & (Order.store_id == store_id))
        )
        order = order_result.scalars().first()

        if not order:
            raise ValueError(f"Orden {order_id} no encontrada en store {store_id}")

        # Validación: no se puede procesar orden ya confirmada (evita doble cobro)
        if order.status == "confirmed":
            raise ValueError(f"Orden {order_id} already confirmed (no double charge)")

        # Obtener ítems de la orden
        items_result = await self.session.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        items = items_result.scalars().all()

        if not items:
            raise ValueError(f"Orden {order_id} no tiene ítems")

        # PRE-VALIDACIÓN: Verificar stock ANTES de procesar nada
        # Si algún producto no tiene suficiente stock, fallar aquí
        # sin modificar ninguna tabla (ACID guarantee)
        for item in items:
            product_result = await self.session.execute(
                select(Product).where(Product.id == item.product_id)
            )
            product = product_result.scalars().first()

            if not product:
                raise ValueError(f"Producto {item.product_id} no encontrado")

            if product.stock_quantity < item.quantity:
                raise ValueError(
                    f"Insufficient stock for product {product.name}: "
                    f"requested {item.quantity} but only {product.stock_quantity} available"
                )

        # TODO EN UNA TRANSACCIÓN:

        # 1. Actualizar orden a 'confirmed'
        order.status = "confirmed"
        self.session.add(order)

        # 2. Crear registro en transactions
        transaction = Transaction(
            id=uuid.uuid4(),
            order_id=order_id,
            store_id=store_id,
            user_id=user_id,
            payment_method=transaction_data.payment_method,
            amount_paid=transaction_data.amount_paid,
            change_amount=transaction_data.change_amount or Decimal("0.00"),
            status="completed",
        )
        self.session.add(transaction)

        # 3 & 4. Descontar stock y crear registros de inventario
        for item in items:
            product_result = await self.session.execute(
                select(Product).where(Product.id == item.product_id)
            )
            product = product_result.scalars().first()

            if not product:
                raise ValueError(f"Producto {item.product_id} no encontrado")

            # Guardar stock anterior para registro de auditoría
            stock_before = product.stock_quantity

            # Descontar stock
            product.stock_quantity -= item.quantity
            self.session.add(product)

            # Crear registro de movimiento de inventario
            movement = InventoryMovement(
                id=uuid.uuid4(),
                product_id=item.product_id,
                transaction_id=transaction.id,
                type="sale",
                quantity_before=stock_before,
                quantity_after=product.stock_quantity,
                delta=-item.quantity,
                reason=f"Sale via transaction {transaction.id}",
                user_id=user_id,
            )
            self.session.add(movement)

        # Commit único: si algo falla, rollback automático
        await self.session.commit()

        return TransactionResponse.model_validate(transaction)
