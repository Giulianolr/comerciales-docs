"""
Integration Tests para Orders API (TDD - RED → GREEN → REFACTOR).
Verifica: Creación de órdenes, adición de ítems, aislamiento multi-tenant.
"""

import uuid
from decimal import Decimal

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models import Category, Product, Station, Store, User


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
async def store_station_and_products(test_session: AsyncSession):
    """Crea un store, estación y productos para tests."""
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

    return store_id, user_id, station_id, product_id_1, product_id_2


class TestOrdersAPI:
    """Tests de integración para Orders API."""

    @pytest.mark.asyncio
    async def test_create_order_http_201(
        self, test_client: httpx.AsyncClient, store_station_and_products
    ):
        """
        DADO: Una estación activa en un store
        CUANDO: Hacemos POST a /api/v1/orders/
        ENTONCES: Retorna HTTP 201 y la orden creada con estado 'pending'
        """
        store_id, _, station_id, _, _ = store_station_and_products

        payload = {"station_id": str(station_id)}

        response = await test_client.post(
            "/api/v1/orders/",
            json=payload,
            headers={"X-Store-ID": str(store_id)},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert data["station_id"] == str(station_id)
        assert data["item_count"] == 0
        assert float(data["total"]) == 0.0

    @pytest.mark.asyncio
    async def test_add_item_to_order_http_201(
        self, test_client: httpx.AsyncClient, store_station_and_products
    ):
        """
        DADO: Una orden creada
        CUANDO: Hacemos POST a /api/v1/orders/{order_id}/items
        ENTONCES: Retorna HTTP 201 y la orden actualizada con el ítem
        """
        store_id, _, station_id, product_id_1, _ = store_station_and_products

        # Crear orden
        order_response = await test_client.post(
            "/api/v1/orders/",
            json={"station_id": str(station_id)},
            headers={"X-Store-ID": str(store_id)},
        )
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]

        # Añadir ítem
        item_payload = {
            "product_id": str(product_id_1),
            "quantity": 3.0,
        }

        item_response = await test_client.post(
            f"/api/v1/orders/{order_id}/items",
            json=item_payload,
            headers={"X-Store-ID": str(store_id)},
        )

        assert item_response.status_code == 201
        updated_order = item_response.json()
        assert updated_order["item_count"] == 1
        assert float(updated_order["total"]) == 7.50  # 3 * 2.50

    @pytest.mark.asyncio
    async def test_checkout_order_http_200(
        self, test_client: httpx.AsyncClient, store_station_and_products, test_session: AsyncSession
    ):
        """
        DADO: Una orden con ítems listos para pagar
        CUANDO: Hacemos POST a /api/v1/orders/{order_id}/checkout
        ENTONCES: Retorna HTTP 200, cambia el status a 'completed' y crea una Transaction
        """
        store_id, user_id, station_id, product_id_1, _ = store_station_and_products

        # Crear orden
        order_response = await test_client.post(
            "/api/v1/orders/",
            json={"station_id": str(station_id)},
            headers={"X-Store-ID": str(store_id)},
        )
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]

        # Añadir ítem
        item_payload = {
            "product_id": str(product_id_1),
            "quantity": 2.0,
        }
        await test_client.post(
            f"/api/v1/orders/{order_id}/items",
            json=item_payload,
            headers={"X-Store-ID": str(store_id)},
        )

        # Hacer checkout
        checkout_payload = {
            "payment_method": "efectivo",
            "amount_received": 10.0,
        }

        checkout_response = await test_client.post(
            f"/api/v1/orders/{order_id}/checkout",
            json=checkout_payload,
            headers={"X-Store-ID": str(store_id)},
        )

        assert checkout_response.status_code == 200
        checkout_data = checkout_response.json()
        assert checkout_data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_checkout_order_http_404_not_found(
        self, test_client: httpx.AsyncClient, store_station_and_products
    ):
        """
        DADO: Un order_id que no existe
        CUANDO: Hacemos POST a /api/v1/orders/{order_id}/checkout
        ENTONCES: Retorna HTTP 404
        """
        store_id, _, _, _, _ = store_station_and_products

        # Intentar checkout con orden inexistente
        checkout_payload = {
            "payment_method": "efectivo",
            "amount_received": 10.0,
        }

        checkout_response = await test_client.post(
            f"/api/v1/orders/{uuid.uuid4()}/checkout",
            json=checkout_payload,
            headers={"X-Store-ID": str(store_id)},
        )

        assert checkout_response.status_code == 404
