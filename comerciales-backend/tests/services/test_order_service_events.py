"""Tests para eventos de OrderService (TDD - RED → GREEN → REFACTOR).
Verifica: Emisión de eventos cart_update cuando se crean/actualizan órdenes.
"""

import asyncio
import json
import uuid
from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import get_redis_manager, init_redis_manager, reset_redis_manager
from app.models import Category, Order, OrderItem, Product, Store, User
from app.services.order_service import OrderService
from app.schemas.order import OrderCreate, OrderItemCreate


@pytest.fixture
async def store_with_products(test_session: AsyncSession):
    """Fixture: Crea store, usuario, categoría y productos."""
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
        password_hash="fake_hash",
        role="ADMIN",
    )
    category = Category(id=category_id, store_id=store_id, name="Frutas")
    product = Product(
        id=product_id,
        store_id=store_id,
        barcode="PROD001",
        name="Manzana",
        description="Fruta fresca",
        category_id=category_id,
        unit="kg",
        price=Decimal("5.00"),
        stock_quantity=100.0,
        min_stock=10.0,
    )

    test_session.add_all([store, user, category, product])
    await test_session.commit()

    return {
        "store_id": store_id,
        "product_id": product_id,
        "user_id": user_id,
    }


class TestOrderServiceEvents:
    """Tests para eventos emitidos por OrderService."""

    @pytest.mark.asyncio
    async def test_create_order_publishes_cart_update_event(
        self, test_session: AsyncSession, store_with_products
    ):
        """
        DADO: OrderService con Redis manager inicializado
        CUANDO: Creamos una orden
        ENTONCES: Se publica evento 'cart_update' en Redis canal sales:{store_id}
        """
        reset_redis_manager()
        await init_redis_manager(use_fake=True)

        store_id = store_with_products["store_id"]
        station_id = uuid.uuid4()

        service = OrderService(test_session)
        order_create = OrderCreate(station_id=station_id)

        received_events = []

        async def listen_for_event():
            """Escuchar evento en Redis."""
            redis_manager = get_redis_manager()
            channel = f"sales:{store_id}"
            async for message in redis_manager.subscribe(channel):
                try:
                    event_data = json.loads(message) if isinstance(message, str) else message
                except (json.JSONDecodeError, TypeError):
                    event_data = message
                received_events.append(event_data)
                if len(received_events) >= 1:
                    break

        async def create_order_task():
            """Crear orden (dispara evento)."""
            await asyncio.sleep(0.1)  # Dar tiempo al listener
            order = await service.create_order(order_create, store_id)
            return order

        # Ejecutar en paralelo
        listener = asyncio.create_task(listen_for_event())
        creator = asyncio.create_task(create_order_task())

        try:
            order_result = await asyncio.wait_for(creator, timeout=2.0)
            await asyncio.wait_for(listener, timeout=2.0)
        except asyncio.TimeoutError:
            pytest.fail("Timeout waiting for event. No event published for create_order?")

        # Verificar que se recibió evento cart_update
        assert len(received_events) >= 1
        event = received_events[0]
        assert event.get("type") == "cart_update"
        assert event.get("total") is not None
        assert isinstance(event.get("items"), list)

    @pytest.mark.asyncio
    async def test_add_item_publishes_cart_update_event(
        self, test_session: AsyncSession, store_with_products
    ):
        """
        DADO: OrderService con Redis manager + una orden existente
        CUANDO: Añadimos un ítem a la orden
        ENTONCES: Se publica evento 'cart_update' con array completo de items
        """
        reset_redis_manager()
        await init_redis_manager(use_fake=True)

        store_id = store_with_products["store_id"]
        product_id = store_with_products["product_id"]
        station_id = uuid.uuid4()

        service = OrderService(test_session)
        order_create = OrderCreate(station_id=station_id)
        order = await service.create_order(order_create, store_id)
        order_id = order.id

        received_events = []

        async def listen_for_item_added():
            """Escuchar solo el evento de item agregado (no el de creación)."""
            redis_manager = get_redis_manager()
            channel = f"sales:{store_id}"
            async for message in redis_manager.subscribe(channel):
                try:
                    event_data = json.loads(message) if isinstance(message, str) else message
                except (json.JSONDecodeError, TypeError):
                    event_data = message
                received_events.append(event_data)
                # El segundo evento será el de item agregado
                if len(received_events) >= 1:
                    break

        async def add_item_task():
            """Añadir item (dispara evento)."""
            await asyncio.sleep(0.2)  # Dar tiempo al listener a conectarse y escuchar
            item_create = OrderItemCreate(product_id=product_id, quantity=2)
            await service.add_item_to_order(order_id, item_create, store_id)

        # Ejecutar en paralelo
        listener = asyncio.create_task(listen_for_item_added())
        adder = asyncio.create_task(add_item_task())

        try:
            await asyncio.wait_for(adder, timeout=3.0)
            await asyncio.wait_for(listener, timeout=3.0)
        except asyncio.TimeoutError:
            pytest.fail("Timeout waiting for cart_update event after adding item")

        # Debe haber al menos 1 evento cart_update
        assert len(received_events) >= 1
        item_event = received_events[0]
        assert item_event.get("type") == "cart_update"
        assert item_event.get("total") is not None
        assert isinstance(item_event.get("items"), list)
        # Debe contener el item que agregamos
        assert len(item_event.get("items", [])) >= 1

    @pytest.mark.asyncio
    async def test_events_gracefully_degrade_if_no_redis_manager(
        self, test_session: AsyncSession, store_with_products
    ):
        """
        DADO: Sin Redis manager inicializado
        CUANDO: Creamos una orden o añadimos item
        ENTONCES: No falla, solo no publica evento (graceful)
        """
        reset_redis_manager()
        # No inicializar manager

        store_id = store_with_products["store_id"]
        product_id = store_with_products["product_id"]
        station_id = uuid.uuid4()

        service = OrderService(test_session)

        # Crear orden - debe funcionar sin manager
        order_create = OrderCreate(station_id=station_id)
        order = await service.create_order(order_create, store_id)
        assert order.id is not None

        # Añadir item - debe funcionar sin manager
        item_create = OrderItemCreate(product_id=product_id, quantity=1)
        await service.add_item_to_order(order.id, item_create, store_id)

        # Si llegamos aquí, no hubo excepción - test pasó
        assert True

    @pytest.mark.asyncio
    async def test_cart_update_contains_all_items_and_total(
        self, test_session: AsyncSession, store_with_products
    ):
        """
        DADO: OrderService emitiendo cart_update
        CUANDO: Añadimos un ítem con cantidad y precio conocido
        ENTONCES: El evento contiene el total y array completo de items con detalles
        """
        reset_redis_manager()
        await init_redis_manager(use_fake=True)

        store_id = store_with_products["store_id"]
        product_id = store_with_products["product_id"]
        station_id = uuid.uuid4()

        service = OrderService(test_session)
        order_create = OrderCreate(station_id=station_id)
        order = await service.create_order(order_create, store_id)
        order_id = order.id

        received_events = []

        async def listen_for_item_with_totals():
            """Escuchar evento con el item agregado y totales."""
            redis_manager = get_redis_manager()
            channel = f"sales:{store_id}"
            async for message in redis_manager.subscribe(channel):
                try:
                    event_data = json.loads(message) if isinstance(message, str) else message
                except (json.JSONDecodeError, TypeError):
                    event_data = message
                received_events.append(event_data)
                # Esperar el evento que tiene items
                if len(event_data.get("items", [])) > 0:
                    break

        async def add_item_task():
            await asyncio.sleep(0.2)
            # Producto: $5.00, cantidad: 3 = $15.00
            item_create = OrderItemCreate(product_id=product_id, quantity=3)
            await service.add_item_to_order(order_id, item_create, store_id)

        listener = asyncio.create_task(listen_for_item_with_totals())
        adder = asyncio.create_task(add_item_task())

        try:
            await asyncio.wait_for(adder, timeout=3.0)
            await asyncio.wait_for(listener, timeout=3.0)
        except asyncio.TimeoutError:
            pytest.fail("Timeout waiting for cart_update event with items and totals")

        # Encontrar el evento con items
        cart_event = None
        for event in received_events:
            if len(event.get("items", [])) > 0:
                cart_event = event
                break

        assert cart_event is not None, "No cart_update event with items found"

        # Verificar estructura del evento
        assert cart_event.get("type") == "cart_update"
        total = cart_event.get("total")
        assert total is not None
        # Total debe ser "15.00" (Decimal serializado a string)
        assert total == "15.00" or Decimal(str(total)) == Decimal("15.00")

        # Verificar que el array items contiene el item que agregamos
        items = cart_event.get("items", [])
        assert len(items) >= 1

        # Verificar estructura del item
        item = items[0]
        assert "id" in item
        assert "name" in item
        assert "quantity" in item
        assert "unit_price" in item
        assert "subtotal" in item
        # Cantidad: Decimal serializado a string (puede ser "3" o "3.0" o 3)
        assert Decimal(str(item["quantity"])) == Decimal("3")
        # Precio: Decimal serializado a string
        assert Decimal(str(item["unit_price"])) == Decimal("5.00")
