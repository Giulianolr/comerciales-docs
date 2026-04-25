"""
Tests para OrderService (TDD - RED → GREEN → REFACTOR).
Verifica: Creación de pre-órdenes, gestión de ítems, cálculo de totales, stock sin descuento.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category, Order, OrderItem, Product, Store, User, Station
from app.schemas.order import OrderCreate, OrderItemCreate, OrderResponse
from app.services.order_service import OrderService


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
async def store_user_category_product(test_session: AsyncSession):
    """Crea un store, usuario, categoría y producto para tests."""
    store_id = uuid.uuid4()
    user_id = uuid.uuid4()
    category_id = uuid.uuid4()
    product_id = uuid.uuid4()

    store = Store(id=store_id, name="Test Store", address="123 Main St", owner_id=user_id)
    user = User(
        id=user_id,
        store_id=store_id,
        name="Test User",
        email="test@example.com",
        pin="1234",
        password_hash="hash",
        role="GERENTE",
    )
    category = Category(id=category_id, store_id=store_id, name="Frutas")
    product = Product(
        id=product_id,
        store_id=store_id,
        barcode="PROD123",
        name="Manzana",
        description="Manzana fresca",
        category_id=category_id,
        unit="kg",
        price=2.50,
        stock_quantity=100.0,
        min_stock=10.0,
    )

    test_session.add(store)
    test_session.add(user)
    test_session.add(category)
    test_session.add(product)
    await test_session.commit()

    return store_id, user_id, category_id, product_id


@pytest.fixture
async def station_for_store(test_session: AsyncSession, store_user_category_product):
    """Crea una estación (balanza) para el store."""
    store_id, user_id, _, _ = store_user_category_product
    station_id = uuid.uuid4()

    station = Station(
        id=station_id,
        store_id=store_id,
        number=1,
        status="active",
    )

    test_session.add(station)
    await test_session.commit()

    return station_id, store_id


class TestOrderService:
    """Tests para OrderService."""

    @pytest.mark.asyncio
    async def test_create_order_success(
        self, test_session: AsyncSession, station_for_store
    ):
        """
        DADO: Una estación (balanza) activa en un store
        CUANDO: Creamos una nueva pre-orden
        ENTONCES: Se crea con UUID único, estado 'pending', y totales inicializados en cero
        """
        station_id, store_id = station_for_store

        await set_store_context(test_session, str(store_id))

        service = OrderService(test_session)
        order_data = OrderCreate(station_id=station_id)

        result = await service.create_order(order_data, store_id)

        assert result.station_id == station_id
        assert result.store_id == store_id
        assert result.status == "pending"
        assert result.total == 0
        assert result.item_count == 0
        assert result.uuid is not None
        assert len(result.uuid) > 0

    @pytest.mark.asyncio
    async def test_add_item_to_order_calculates_totals(
        self, test_session: AsyncSession, station_for_store, store_user_category_product
    ):
        """
        DADO: Una pre-orden creada
        CUANDO: Añadimos un ítem (product_id, quantity)
        ENTONCES: Se consulta el precio del producto, se calcula subtotal, y se actualiza total de orden
        """
        station_id, store_id = station_for_store
        _, _, _, product_id = store_user_category_product

        await set_store_context(test_session, str(store_id))

        service = OrderService(test_session)
        order_data = OrderCreate(station_id=station_id)
        order = await service.create_order(order_data, store_id)

        # Añadir ítem: 5 kg de manzana a $2.50/kg = $12.50
        item_data = OrderItemCreate(product_id=product_id, quantity=5.0)
        await service.add_item_to_order(order.id, item_data, store_id)

        # Verificar que la orden fue actualizada
        updated_order = await service.get_order_by_id(order.id, store_id)

        assert updated_order is not None
        assert updated_order.item_count == 1
        assert float(updated_order.total) == 12.50

    @pytest.mark.asyncio
    async def test_add_multiple_items_and_verify_totals(
        self, test_session: AsyncSession, station_for_store, store_user_category_product
    ):
        """
        DADO: Una pre-orden con múltiples ítems
        CUANDO: Consultamos la orden y sus ítems
        ENTONCES: El total es correcto y la cantidad de ítems es correcta
        """
        station_id, store_id = station_for_store
        _, _, _, product_id = store_user_category_product

        await set_store_context(test_session, str(store_id))

        service = OrderService(test_session)
        order_data = OrderCreate(station_id=station_id)
        order = await service.create_order(order_data, store_id)

        # Añadir dos ítems
        item_data_1 = OrderItemCreate(product_id=product_id, quantity=3.0)  # 3 * 2.50 = 7.50
        item_data_2 = OrderItemCreate(product_id=product_id, quantity=2.0)  # 2 * 2.50 = 5.00
        await service.add_item_to_order(order.id, item_data_1, store_id)
        await service.add_item_to_order(order.id, item_data_2, store_id)

        updated_order = await service.get_order_by_id(order.id, store_id)

        assert updated_order is not None
        assert updated_order.item_count == 2
        assert float(updated_order.total) == 12.50  # 7.50 + 5.00

    @pytest.mark.asyncio
    async def test_stock_not_decremented_on_add_item(
        self, test_session: AsyncSession, station_for_store, store_user_category_product
    ):
        """
        DADO: Un producto con stock inicial
        CUANDO: Añadimos ítems a una orden
        ENTONCES: El stock del producto NO disminuye (stock solo se descuenta en transacción)
        """
        station_id, store_id = station_for_store
        _, _, _, product_id = store_user_category_product

        await set_store_context(test_session, str(store_id))

        # Obtener stock inicial del producto
        service = OrderService(test_session)
        initial_product = await service._get_product(product_id, store_id)
        initial_stock = initial_product.stock_quantity

        # Crear orden y añadir ítem
        order_data = OrderCreate(station_id=station_id)
        order = await service.create_order(order_data, store_id)
        item_data = OrderItemCreate(product_id=product_id, quantity=10.0)
        await service.add_item_to_order(order.id, item_data, store_id)

        # Verificar que el stock sigue siendo el mismo
        updated_product = await service._get_product(product_id, store_id)
        assert updated_product.stock_quantity == initial_stock
