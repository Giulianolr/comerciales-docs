"""Test E2E para integración WebSocket + Ventas (TDD - RED → GREEN → REFACTOR).
Verifica: Conexión WebSocket autenticada y recepción de eventos de venta en tiempo real.
"""

import asyncio
import json
import uuid
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password
from app.models.core import Category, Product, Store, User
from app.models.transaction import Order, OrderItem, Station


@pytest.fixture
async def store_with_user_and_products(test_session: AsyncSession):
    """Crea un setup completo: store, usuario, station, categoría y productos."""
    store_id = uuid.uuid4()
    user_id = uuid.uuid4()
    station_id = uuid.uuid4()
    category_id = uuid.uuid4()
    product_id = uuid.uuid4()

    # Crear entidades
    store = Store(id=store_id, name="Test Store", address="123 Main St", owner_id=user_id)
    user = User(
        id=user_id,
        store_id=store_id,
        name="Cashier",
        email="cashier@example.com",
        pin="1234",
        password_hash=hash_password("cashier_pass"),
        role="CAJERO",
    )
    station = Station(id=station_id, store_id=store_id, number=1, status="active")
    category = Category(id=category_id, store_id=store_id, name="Frutas")
    product = Product(
        id=product_id,
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

    test_session.add_all([store, user, station, category, product])
    await test_session.commit()

    token = create_access_token(user_id)

    return {
        "store_id": store_id,
        "user_id": user_id,
        "token": token,
        "station_id": station_id,
        "product_id": product_id,
    }


@pytest.mark.asyncio
async def test_websocket_receives_sale_event(
    test_client_sync, test_session: AsyncSession, store_with_user_and_products
):
    """
    CRÍTICA: Test E2E completo.

    DADO: Un usuario autenticado conectado a WebSocket de su store
    CUANDO: Se procesa una venta en el backend
    ENTONCES: El usuario recibe el evento de "Nueva Venta" en tiempo real
    """
    setup = store_with_user_and_products
    store_id = str(setup["store_id"])
    user_id = str(setup["user_id"])
    token = setup["token"]
    station_id = setup["station_id"]
    product_id = setup["product_id"]

    # 1. Conectar WebSocket autenticado
    with test_client_sync.websocket_connect(f"/api/v1/ws/store/{store_id}?token={token}") as ws:
        # 2. Verificar conexión (puede recibir un mensaje de bienvenida o simplemente estar conectado)
        # TODO: implementar sending de welcome message si es necesario

        # 3. Crear una orden
        from app.schemas.order import OrderCreate, OrderItemCreate

        order_create = OrderCreate(station_id=station_id)
        # Crear orden manualmente en la BD
        order = Order(
            id=uuid.uuid4(),
            uuid=str(uuid.uuid4()),
            store_id=setup["store_id"],
            station_id=station_id,
            status="pending",
            total=Decimal("2.50"),
        )
        test_session.add(order)
        await test_session.commit()

        # Agregar item
        item = OrderItem(
            id=uuid.uuid4(),
            order_id=order.id,
            product_id=setup["product_id"],
            quantity=Decimal("1.0"),
            unit_price=Decimal("2.50"),
            unit="kg",
            subtotal=Decimal("2.50"),
        )
        test_session.add(item)
        await test_session.commit()

        # 4. Procesar la venta (HTTP POST)
        from app.schemas.transaction import TransactionCreate

        tx_create = TransactionCreate(
            order_id=order.id,
            payment_method="cash",
            amount_paid=Decimal("2.50"),
            change_amount=Decimal("0.00"),
        )

        # Simular POST a /api/v1/transactions con headers requeridos
        response = test_client_sync.post(
            "/api/v1/transactions",
            json={
                "order_id": str(order.id),
                "payment_method": "cash",
                "amount_paid": "2.50",
                "change_amount": "0.00",
            },
            headers={
                "X-Store-ID": store_id,
                "X-User-ID": user_id,
            },
        )

        # La venta debe ser exitosa
        assert response.status_code == 201

        # 5. Recibir el evento en el WebSocket (con timeout)
        # Esperar hasta 2 segundos por un mensaje
        try:
            # Los mensajes pueden llegar en formato JSON
            data = ws.receive_json()

            # Verificar que el evento contiene información de venta
            assert data is not None
            assert "type" in data or "event" in data or "message" in data
            # El evento debe ser sobre una venta ("sale", "venta", "transaction", etc)
            event_type = data.get("type") or data.get("event") or "sale"
            assert event_type in [
                "sale",
                "venta",
                "transaction",
                "new_sale",
                "nueva_venta",
            ] or "sale" in str(data).lower()

        except Exception as e:
            pytest.fail(
                f"WebSocket did not receive sale event. Error: {e}. "
                f"Make sure RedisPubSubManager and ConnectionManager are wired up."
            )
