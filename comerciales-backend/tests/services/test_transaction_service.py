"""
Tests para TransactionService (TDD - RED → GREEN → REFACTOR).
Verifica: Flujo de cobro, descuento de stock, auditoría y transaccionalidad.
"""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Category,
    InventoryMovement,
    Order,
    OrderItem,
    Product,
    Store,
    Transaction,
    User,
    Station,
)
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.order_service import OrderService
from app.services.transaction_service import TransactionService


async def set_store_context(session: AsyncSession, store_id: str) -> None:
    """Inyectar store_id en contexto (manejo de SQLite sin soporte RLS)."""
    from sqlalchemy import text
    from sqlalchemy.exc import OperationalError

    try:
        await session.execute(
            text("SET LOCAL app.current_store_id = :store_id"), {"store_id": store_id}
        )
    except OperationalError:
        pass


@pytest.fixture
async def complete_order_setup(test_session: AsyncSession):
    """Crea store, usuario, station, productos y una orden con ítems."""
    store_id = uuid.uuid4()
    user_id = uuid.uuid4()
    station_id = uuid.uuid4()
    category_id = uuid.uuid4()
    product_id_1 = uuid.uuid4()
    product_id_2 = uuid.uuid4()

    # Crear entidades base
    store = Store(id=store_id, name="Test Store", address="123 Main St", owner_id=user_id)
    user = User(
        id=user_id,
        store_id=store_id,
        name="Cajero Test",
        email="cashier@example.com",
        pin="1234",
        password_hash="hash",
        role="CAJERO",
    )
    station = Station(id=station_id, store_id=store_id, number=1, status="active")
    category = Category(id=category_id, store_id=store_id, name="Frutas")

    # Productos con stock conocido
    product_1 = Product(
        id=product_id_1,
        store_id=store_id,
        barcode="PROD001",
        name="Manzana",
        description="Manzana fresca",
        category_id=category_id,
        unit="kg",
        price=Decimal("2.50"),
        stock_quantity=100.0,
        min_stock=10.0,
    )
    product_2 = Product(
        id=product_id_2,
        store_id=store_id,
        barcode="PROD002",
        name="Pera",
        description="Pera fresca",
        category_id=category_id,
        unit="kg",
        price=Decimal("3.00"),
        stock_quantity=50.0,
        min_stock=5.0,
    )

    test_session.add_all([store, user, station, category, product_1, product_2])
    await test_session.commit()

    # Crear una orden con dos ítems
    await set_store_context(test_session, str(store_id))
    order_service = OrderService(test_session)

    from app.schemas.order import OrderCreate, OrderItemCreate

    order_data = OrderCreate(station_id=station_id)
    order = await order_service.create_order(order_data, store_id)

    # Añadir ítems: 3kg de manzana + 2kg de pera
    item_1_data = OrderItemCreate(product_id=product_id_1, quantity=3.0)
    item_2_data = OrderItemCreate(product_id=product_id_2, quantity=2.0)
    await order_service.add_item_to_order(order.id, item_1_data, store_id)
    await order_service.add_item_to_order(order.id, item_2_data, store_id)

    await test_session.commit()

    # Retornar datos para tests
    return {
        "store_id": store_id,
        "user_id": user_id,
        "order_id": order.id,
        "product_1_id": product_id_1,
        "product_2_id": product_id_2,
        "initial_stock_1": 100.0,
        "initial_stock_2": 50.0,
    }


class TestTransactionService:
    """Tests para TransactionService."""

    @pytest.mark.asyncio
    async def test_process_payment_successful_updates_all_tables(
        self, test_session: AsyncSession, complete_order_setup
    ):
        """
        DADO: Una orden 'pending' con ítems y stock disponible
        CUANDO: Procesamos el pago exitosamente
        ENTONCES: 
          a) La orden cambia a 'confirmed'
          b) Se crea un registro en transactions
          c) El stock se descuenta correctamente
          d) Se crean registros en inventory_movements (auditoría)
        """
        setup = complete_order_setup
        store_id = setup["store_id"]
        order_id = setup["order_id"]
        user_id = setup["user_id"]
        product_1_id = setup["product_1_id"]
        product_2_id = setup["product_2_id"]

        await set_store_context(test_session, str(store_id))

        # Procesar pago
        service = TransactionService(test_session)
        transaction_data = TransactionCreate(
            order_id=order_id,
            payment_method="cash",
            amount_paid=Decimal("13.50"),  # 3*2.50 + 2*3.00
            change_amount=Decimal("0.00"),
        )
        result = await service.process_payment(
            order_id=order_id,
            transaction_data=transaction_data,
            user_id=user_id,
            store_id=store_id,
        )

        # a) Verificar que la orden está 'confirmed'
        order_result = await test_session.execute(select(Order).where(Order.id == order_id))
        order = order_result.scalars().first()
        assert order is not None
        assert order.status == "confirmed"

        # b) Verificar que se creó el registro en transactions
        assert result.id is not None
        assert result.payment_method == "cash"
        assert result.amount_paid == Decimal("13.50")
        assert result.status == "completed"

        # c) Verificar que el stock se descuentó
        product_1_result = await test_session.execute(
            select(Product).where(Product.id == product_1_id)
        )
        product_1 = product_1_result.scalars().first()
        assert float(product_1.stock_quantity) == 97.0  # 100 - 3

        product_2_result = await test_session.execute(
            select(Product).where(Product.id == product_2_id)
        )
        product_2 = product_2_result.scalars().first()
        assert float(product_2.stock_quantity) == 48.0  # 50 - 2

        # d) Verificar que se crearon registros en inventory_movements
        movements_result = await test_session.execute(
            select(InventoryMovement).where(InventoryMovement.transaction_id == result.id)
        )
        movements = movements_result.scalars().all()
        assert len(movements) == 2  # Uno por cada producto

        # Verificar detalles de movimientos
        mov_prod1 = [m for m in movements if m.product_id == product_1_id][0]
        assert mov_prod1.type == "sale"
        assert float(mov_prod1.quantity_before) == 100.0
        assert float(mov_prod1.quantity_after) == 97.0
        assert float(mov_prod1.delta) == -3.0

        mov_prod2 = [m for m in movements if m.product_id == product_2_id][0]
        assert mov_prod2.type == "sale"
        assert float(mov_prod2.quantity_before) == 50.0
        assert float(mov_prod2.quantity_after) == 48.0
        assert float(mov_prod2.delta) == -2.0

    @pytest.mark.asyncio
    async def test_cannot_process_already_confirmed_order(
        self, test_session: AsyncSession, complete_order_setup
    ):
        """
        DADO: Una orden que ya fue procesada (status='confirmed')
        CUANDO: Intentamos procesar el pago nuevamente
        ENTONCES: El servicio falla con excepción (evita doble cobro)
        """
        setup = complete_order_setup
        store_id = setup["store_id"]
        order_id = setup["order_id"]
        user_id = setup["user_id"]

        await set_store_context(test_session, str(store_id))

        # Procesar pago la primera vez (exitoso)
        service = TransactionService(test_session)
        transaction_data = TransactionCreate(
            order_id=order_id,
            payment_method="cash",
            amount_paid=Decimal("13.50"),
            change_amount=Decimal("0.00"),
        )
        await service.process_payment(
            order_id=order_id,
            transaction_data=transaction_data,
            user_id=user_id,
            store_id=store_id,
        )

        # Intentar procesar nuevamente (debe fallar)
        with pytest.raises(ValueError, match="already confirmed"):
            await service.process_payment(
                order_id=order_id,
                transaction_data=transaction_data,
                user_id=user_id,
                store_id=store_id,
            )

    @pytest.mark.asyncio
    async def test_transaction_rolls_back_on_error(
        self, test_session: AsyncSession, complete_order_setup
    ):
        """
        DADO: Una orden con ítems
        CUANDO: Ocurre un error durante el procesamiento (ej: excepción)
        ENTONCES: Toda la transacción se revierte (rollback) y el estado queda intacto
        """
        setup = complete_order_setup
        store_id = setup["store_id"]
        order_id = setup["order_id"]
        user_id = setup["user_id"]
        product_1_id = setup["product_1_id"]

        await set_store_context(test_session, str(store_id))

        # Obtener stock inicial
        product_result = await test_session.execute(
            select(Product).where(Product.id == product_1_id)
        )
        initial_stock = product_result.scalars().first().stock_quantity

        # Crear un servicio que va a fallar (inyectamos error)
        service = TransactionService(test_session)

        # Usar amount_paid = -999 para simular una validación que falla
        transaction_data = TransactionCreate(
            order_id=order_id,
            payment_method="cash",
            amount_paid=Decimal("-999.00"),  # Esto debería fallar
            change_amount=Decimal("0.00"),
        )

        with pytest.raises(ValueError):
            await service.process_payment(
                order_id=order_id,
                transaction_data=transaction_data,
                user_id=user_id,
                store_id=store_id,
            )

        # Verificar que la orden SIGUE en 'pending' (no se modificó)
        order_result = await test_session.execute(select(Order).where(Order.id == order_id))
        order = order_result.scalars().first()
        assert order.status == "pending"

        # Verificar que el stock NO cambió
        product_result = await test_session.execute(
            select(Product).where(Product.id == product_1_id)
        )
        current_stock = product_result.scalars().first().stock_quantity
        assert current_stock == initial_stock

        # Verificar que NO hay transacción registrada
        tx_result = await test_session.execute(
            select(Transaction).where(Transaction.order_id == order_id)
        )
        tx = tx_result.scalars().first()
        assert tx is None

    @pytest.mark.asyncio
    async def test_insufficient_stock_blocks_sale_and_rolls_back(
        self, test_session: AsyncSession, complete_order_setup
    ):
        """
        CRÍTICO: Validar insuficiencia de stock.

        DADO: Una orden que intenta vender 150kg de manzana pero solo hay 100kg disponibles
        CUANDO: Intentamos procesar el pago
        ENTONCES:
          a) El servicio falla con ValueError (insuficiente stock)
          b) El stock NO se descuenta (sigue siendo 100kg)
          c) NO se crea registro en transactions
          d) La orden sigue en status 'pending'
          e) NO hay InventoryMovement registrado

        Este test PREVIENE la venta con stock negativo (ACID guarantee).
        """
        setup = complete_order_setup
        store_id = setup["store_id"]
        user_id = setup["user_id"]
        product_1_id = setup["product_1_id"]
        initial_stock_1 = setup["initial_stock_1"]  # 100kg

        await set_store_context(test_session, str(store_id))

        # Crear nueva orden que intenta vender 150kg (más que el stock de 100kg)
        from app.schemas.order import OrderCreate, OrderItemCreate

        order_service = OrderService(test_session)
        order_data = OrderCreate(station_id=uuid.uuid4())  # Station existe en setup

        # Obtener la station ID del setup
        station_result = await test_session.execute(
            select(Station).where(Station.store_id == store_id)
        )
        station = station_result.scalars().first()

        order_data = OrderCreate(station_id=station.id)
        order = await order_service.create_order(order_data, store_id)

        # Intenta vender 150kg de manzana (stock=100kg)
        item_data = OrderItemCreate(product_id=product_1_id, quantity=150.0)
        await order_service.add_item_to_order(order.id, item_data, store_id)
        await test_session.commit()

        # Intentar procesar pago (debe fallar porque no hay suficiente stock)
        service = TransactionService(test_session)
        transaction_data = TransactionCreate(
            order_id=order.id,
            payment_method="cash",
            amount_paid=Decimal("500.00"),
            change_amount=Decimal("0.00"),
        )

        # a) Debe fallar con ValueError de stock insuficiente
        with pytest.raises(ValueError, match="[Ii]nsufficient|[Ss]tock"):
            await service.process_payment(
                order_id=order.id,
                transaction_data=transaction_data,
                user_id=user_id,
                store_id=store_id,
            )

        # b) Verificar que el stock NO se descuentó
        product_result = await test_session.execute(
            select(Product).where(Product.id == product_1_id)
        )
        current_stock = product_result.scalars().first().stock_quantity
        assert float(current_stock) == initial_stock_1  # Sigue siendo 100kg

        # c) NO debe haber transacción registrada
        tx_result = await test_session.execute(
            select(Transaction).where(Transaction.order_id == order.id)
        )
        tx = tx_result.scalars().first()
        assert tx is None

        # d) La orden sigue en 'pending'
        order_result = await test_session.execute(select(Order).where(Order.id == order.id))
        order = order_result.scalars().first()
        assert order.status == "pending"

        # e) NO hay InventoryMovement creado
        movements_result = await test_session.execute(
            select(InventoryMovement).where(InventoryMovement.product_id == product_1_id)
        )
        movements = movements_result.scalars().all()
        assert len(movements) == 0
