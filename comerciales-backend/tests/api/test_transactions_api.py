"""
Integration Tests para Transactions API (TDD - RED → GREEN → REFACTOR).
Verifica: Procesamiento de pagos, consolidación de órdenes, stock deduction.
"""

import uuid
from decimal import Decimal

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models import Category, Product, Station, Store, User, Order, Transaction
from app.services.order_service import OrderService
from app.schemas.order import OrderCreate, OrderItemCreate


@pytest.fixture
async def test_client(test_session: AsyncSession):
    """TestClient asincrónico para hacer requests HTTP a la API."""
    
    async def override_get_db():
        yield test_session

    from app.api.deps import get_db
    
    app.dependency_overrides[get_db] = override_get_db

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def order_with_items(test_session: AsyncSession):
    """Crea un store, estación, productos y una orden con ítems."""
    store_id = uuid.uuid4()
    user_id = uuid.uuid4()
    station_id = uuid.uuid4()
    category_id = uuid.uuid4()
    product_id_1 = uuid.uuid4()
    product_id_2 = uuid.uuid4()

    store = Store(id=store_id, name="Test Store", address="123 Main St", owner_id=user_id)
    user = User(
        id=user_id,
        store_id=store_id,
        name="Test Cashier",
        email="cashier@example.com",
        pin="1234",
        password_hash="hash",
        role="CAJERO",
    )
    station = Station(id=station_id, store_id=store_id, number=1, status="active")
    category = Category(id=category_id, store_id=store_id, name="Frutas")
    
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

    # Crear una orden con ítems
    from sqlalchemy import text
    from sqlalchemy.exc import OperationalError
    
    async def set_store_context(session, store_id_val):
        try:
            await session.execute(
                text("SET LOCAL app.current_store_id = :store_id"), 
                {"store_id": str(store_id_val)}
            )
        except OperationalError:
            pass
    
    await set_store_context(test_session, store_id)
    
    order_service = OrderService(test_session)
    order_data = OrderCreate(station_id=station_id)
    order = await order_service.create_order(order_data, store_id)
    
    # Añadir ítems: 3kg manzana + 2kg pera = 7.50 + 6.00 = 13.50
    item_1_data = OrderItemCreate(product_id=product_id_1, quantity=3.0)
    item_2_data = OrderItemCreate(product_id=product_id_2, quantity=2.0)
    await order_service.add_item_to_order(order.id, item_1_data, store_id)
    await order_service.add_item_to_order(order.id, item_2_data, store_id)
    
    await test_session.commit()

    return store_id, user_id, order.id, product_id_1, product_id_2


class TestTransactionsAPI:
    """Tests de integración para Transactions API."""

    @pytest.mark.asyncio
    async def test_process_payment_http_201(
        self, test_client: httpx.AsyncClient, order_with_items, test_session: AsyncSession
    ):
        """
        DADO: Una orden 'pending' con ítems
        CUANDO: Hacemos POST a /api/v1/transactions/
        ENTONCES: Retorna HTTP 201, crea transaction, actualiza orden a 'confirmed', descuenta stock
        """
        store_id, user_id, order_id, product_id_1, product_id_2 = order_with_items

        payload = {
            "order_id": str(order_id),
            "payment_method": "cash",
            "amount_paid": 13.50,
            "change_amount": 0.00,
        }

        response = await test_client.post(
            "/api/v1/transactions/",
            json=payload,
            headers={
                "X-Store-ID": str(store_id),
                "X-User-ID": str(user_id),
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "completed"
        assert float(data["amount_paid"]) == 13.50
        assert data["payment_method"] == "cash"

        # Verificar que la orden pasó a 'confirmed'
        order_result = await test_session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = order_result.scalars().first()
        assert order.status == "confirmed"

        # Verificar que el stock se descuentó
        product_1_result = await test_session.execute(
            select(Product).where(Product.id == product_id_1)
        )
        product_1 = product_1_result.scalars().first()
        assert float(product_1.stock_quantity) == 97.0  # 100 - 3

        product_2_result = await test_session.execute(
            select(Product).where(Product.id == product_id_2)
        )
        product_2 = product_2_result.scalars().first()
        assert float(product_2.stock_quantity) == 48.0  # 50 - 2
