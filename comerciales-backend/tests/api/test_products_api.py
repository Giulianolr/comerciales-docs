"""
Integration Tests para Products API (TDD - RED → GREEN → REFACTOR).
Verifica: HTTP endpoints, respuestas JSON, multi-tenant isolation.
"""

import uuid
from decimal import Decimal

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models import Category, Product, Store, User


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
async def store_and_products(test_session: AsyncSession):
    """Crea un store con usuario y productos para tests."""
    store_id = uuid.uuid4()
    user_id = uuid.uuid4()
    category_id = uuid.uuid4()
    product_id_1 = uuid.uuid4()

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

    test_session.add_all([store, user, category, product])
    await test_session.commit()

    return store_id, user_id, category_id, product_id_1


class TestProductsAPI:
    """Tests de integración para Products API."""

    @pytest.mark.asyncio
    async def test_create_product_http_201(self, test_client: httpx.AsyncClient, store_and_products):
        """
        DADO: Una request POST a /api/v1/products/
        CUANDO: Enviamos datos válidos de un producto
        ENTONCES: Retorna HTTP 201 y el producto creado
        """
        store_id, _, category_id, _ = store_and_products

        payload = {
            "barcode": "NEWPROD001",
            "name": "Pera",
            "description": "Pera fresca",
            "category_id": str(category_id),
            "unit": "kg",
            "price": 3.50,
            "stock_quantity": 50.0,
            "min_stock": 5.0,
        }

        response = await test_client.post(
            "/api/v1/products/",
            json=payload,
            headers={"X-Store-ID": str(store_id)},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Pera"
        assert data["barcode"] == "NEWPROD001"
        assert float(data["price"]) == 3.50

    @pytest.mark.asyncio
    async def test_list_products_http_200(self, test_client: httpx.AsyncClient, store_and_products):
        """
        DADO: Un store con productos existentes
        CUANDO: Hacemos GET a /api/v1/products/
        ENTONCES: Retorna HTTP 200 y la lista de productos
        """
        store_id, _, _, _ = store_and_products

        response = await test_client.get(
            "/api/v1/products/",
            headers={"X-Store-ID": str(store_id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(p["name"] == "Manzana" for p in data)

    @pytest.mark.asyncio
    async def test_list_products_respects_store_isolation(
        self, test_client: httpx.AsyncClient, test_session: AsyncSession
    ):
        """
        DADO: Dos stores con productos diferentes
        CUANDO: Hacemos GET a /api/v1/products/ desde cada store
        ENTONCES: Cada store ve solo sus propios productos (aislamiento)
        """
        # Crear dos stores con sus productos
        store_id_1 = uuid.uuid4()
        store_id_2 = uuid.uuid4()
        user_id_1 = uuid.uuid4()
        user_id_2 = uuid.uuid4()
        cat_id_1 = uuid.uuid4()
        cat_id_2 = uuid.uuid4()
        prod_id_1 = uuid.uuid4()
        prod_id_2 = uuid.uuid4()

        store_1 = Store(id=store_id_1, name="Store 1", address="Addr 1", owner_id=user_id_1)
        user_1 = User(
            id=user_id_1,
            store_id=store_id_1,
            name="User 1",
            email="user1@test.com",
            pin="1111",
            password_hash="hash1",
            role="GERENTE",
        )
        cat_1 = Category(id=cat_id_1, store_id=store_id_1, name="Cat1")
        prod_1 = Product(
            id=prod_id_1,
            store_id=store_id_1,
            barcode="STORE1PROD",
            name="Produto Store 1",
            description="",
            category_id=cat_id_1,
            unit="kg",
            price=Decimal("1.0"),
            stock_quantity=10.0,
            min_stock=1.0,
        )

        store_2 = Store(id=store_id_2, name="Store 2", address="Addr 2", owner_id=user_id_2)
        user_2 = User(
            id=user_id_2,
            store_id=store_id_2,
            name="User 2",
            email="user2@test.com",
            pin="2222",
            password_hash="hash2",
            role="GERENTE",
        )
        cat_2 = Category(id=cat_id_2, store_id=store_id_2, name="Cat2")
        prod_2 = Product(
            id=prod_id_2,
            store_id=store_id_2,
            barcode="STORE2PROD",
            name="Producto Store 2",
            description="",
            category_id=cat_id_2,
            unit="kg",
            price=Decimal("2.0"),
            stock_quantity=20.0,
            min_stock=2.0,
        )

        test_session.add_all([store_1, user_1, cat_1, prod_1, store_2, user_2, cat_2, prod_2])
        await test_session.commit()

        # GET desde Store 1
        response_1 = await test_client.get(
            "/api/v1/products/",
            headers={"X-Store-ID": str(store_id_1)},
        )
        assert response_1.status_code == 200
        products_1 = response_1.json()
        assert len(products_1) == 1
        assert products_1[0]["name"] == "Produto Store 1"

        # GET desde Store 2
        response_2 = await test_client.get(
            "/api/v1/products/",
            headers={"X-Store-ID": str(store_id_2)},
        )
        assert response_2.status_code == 200
        products_2 = response_2.json()
        assert len(products_2) == 1
        assert products_2[0]["name"] == "Producto Store 2"

    @pytest.mark.asyncio
    async def test_get_product_by_barcode_http_200(
        self, test_client: httpx.AsyncClient, store_and_products
    ):
        """
        DADO: Un store con un producto que tiene un barcode específico
        CUANDO: Hacemos GET a /api/v1/products/barcode/{barcode}
        ENTONCES: Retorna HTTP 200 y el producto correcto
        """
        store_id, _, _, _ = store_and_products

        response = await test_client.get(
            "/api/v1/products/barcode/PROD001",
            headers={"X-Store-ID": str(store_id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Manzana"
        assert data["barcode"] == "PROD001"
        assert float(data["price"]) == 2.50

    @pytest.mark.asyncio
    async def test_get_product_by_barcode_http_404_not_found(
        self, test_client: httpx.AsyncClient, store_and_products
    ):
        """
        DADO: Un barcode que no existe en el store
        CUANDO: Hacemos GET a /api/v1/products/barcode/{barcode}
        ENTONCES: Retorna HTTP 404
        """
        store_id, _, _, _ = store_and_products

        response = await test_client.get(
            "/api/v1/products/barcode/NONEXISTENT",
            headers={"X-Store-ID": str(store_id)},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_product_by_barcode_respects_store_isolation(
        self, test_client: httpx.AsyncClient, test_session: AsyncSession
    ):
        """
        DADO: Dos stores con productos que comparten el mismo barcode
        CUANDO: Hacemos GET a /api/v1/products/barcode/{barcode} desde cada store
        ENTONCES: Cada store ve solo su propio producto (aislamiento)
        """
        # Store 1 con producto PROD001
        store_id_1 = uuid.uuid4()
        user_id_1 = uuid.uuid4()
        cat_id_1 = uuid.uuid4()
        prod_id_1 = uuid.uuid4()

        store_1 = Store(id=store_id_1, name="Store 1", address="Addr 1", owner_id=user_id_1)
        user_1 = User(
            id=user_id_1,
            store_id=store_id_1,
            name="User 1",
            email="user1@test.com",
            pin="1111",
            password_hash="hash1",
            role="GERENTE",
        )
        cat_1 = Category(id=cat_id_1, store_id=store_id_1, name="Cat1")
        prod_1 = Product(
            id=prod_id_1,
            store_id=store_id_1,
            barcode="SHARED001",
            name="Producto Store 1",
            description="Desc 1",
            category_id=cat_id_1,
            unit="kg",
            price=Decimal("1.50"),
            stock_quantity=10.0,
            min_stock=1.0,
        )

        # Store 2 con producto PROD001 diferente
        store_id_2 = uuid.uuid4()
        user_id_2 = uuid.uuid4()
        cat_id_2 = uuid.uuid4()
        prod_id_2 = uuid.uuid4()

        store_2 = Store(id=store_id_2, name="Store 2", address="Addr 2", owner_id=user_id_2)
        user_2 = User(
            id=user_id_2,
            store_id=store_id_2,
            name="User 2",
            email="user2@test.com",
            pin="2222",
            password_hash="hash2",
            role="GERENTE",
        )
        cat_2 = Category(id=cat_id_2, store_id=store_id_2, name="Cat2")
        prod_2 = Product(
            id=prod_id_2,
            store_id=store_id_2,
            barcode="SHARED001",
            name="Producto Store 2",
            description="Desc 2",
            category_id=cat_id_2,
            unit="kg",
            price=Decimal("2.50"),
            stock_quantity=20.0,
            min_stock=2.0,
        )

        test_session.add_all([store_1, user_1, cat_1, prod_1, store_2, user_2, cat_2, prod_2])
        await test_session.commit()

        # GET desde Store 1
        response_1 = await test_client.get(
            "/api/v1/products/barcode/SHARED001",
            headers={"X-Store-ID": str(store_id_1)},
        )
        assert response_1.status_code == 200
        product_1 = response_1.json()
        assert product_1["name"] == "Producto Store 1"
        assert float(product_1["price"]) == 1.50

        # GET desde Store 2
        response_2 = await test_client.get(
            "/api/v1/products/barcode/SHARED001",
            headers={"X-Store-ID": str(store_id_2)},
        )
        assert response_2.status_code == 200
        product_2 = response_2.json()
        assert product_2["name"] == "Producto Store 2"
        assert float(product_2["price"]) == 2.50
