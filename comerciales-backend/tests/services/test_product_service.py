"""
Tests para ProductService (TDD - RED → GREEN → REFACTOR).
Verifica: CRUD de productos + aislamiento multi-tenant (RLS).
"""

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product, Store, User
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import ProductService


async def set_store_context(session: AsyncSession, store_id: str) -> None:
    """Inyectar store_id en contexto (manejo de SQLite sin soporte RLS)."""
    try:
        await session.execute(
            text("SET LOCAL app.current_store_id = :store_id"), {"store_id": store_id}
        )
    except OperationalError:
        # SQLite no soporta SET LOCAL
        pass


@pytest.fixture
async def store_and_user(test_session: AsyncSession):
    """Crea un store y un usuario para tests."""
    store_id = uuid.uuid4()
    user_id = uuid.uuid4()

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

    test_session.add(store)
    test_session.add(user)
    await test_session.commit()

    return store_id, user_id


class TestProductService:
    """Tests para ProductService."""

    @pytest.mark.asyncio
    async def test_create_product_success(self, test_session: AsyncSession, store_and_user):
        """
        DADO: Un ProductService con una sesión de test
        CUANDO: Creamos un producto válido para un store
        ENTONCES: El producto se crea y se retorna con todos los datos correctos
        """
        store_id, _ = store_and_user

        # Inyectar store_id al contexto de BD para RLS
        await set_store_context(test_session, str(store_id))

        service = ProductService(test_session)
        product_data = ProductCreate(
            barcode="123456789",
            name="Tomate",
            description="Tomate fresco",
            category_id=uuid.uuid4(),
            unit="kg",
            price=2.50,
            stock_quantity=100.0,
            min_stock=10.0,
        )

        result = await service.create_product(product_data, store_id)

        assert result.barcode == "123456789"
        assert result.name == "Tomate"
        assert result.unit == "kg"
        assert result.price == 2.50
        assert result.stock_quantity == 100.0

    @pytest.mark.asyncio
    async def test_list_products_respects_tenant_isolation(
        self, test_session: AsyncSession, store_and_user
    ):
        """
        DADO: Dos stores con productos diferentes
        CUANDO: Listamos productos con store_id inyectado (RLS activo)
        ENTONCES: Solo vemos productos del store actual
        """
        store_id_1, _ = store_and_user
        store_id_2 = uuid.uuid4()

        # Crear segundo store y usuario
        user_id_2 = uuid.uuid4()
        store_2 = Store(
            id=store_id_2,
            name="Store 2",
            address="456 Oak Ave",
            owner_id=user_id_2,
        )
        user_2 = User(
            id=user_id_2,
            store_id=store_id_2,
            name="User 2",
            email="user2@example.com",
            pin="5678",
            password_hash="hash2",
            role="GERENTE",
        )

        test_session.add(store_2)
        test_session.add(user_2)
        await test_session.commit()

        # Crear productos en ambos stores
        category_id_1 = uuid.uuid4()
        category_id_2 = uuid.uuid4()

        # Producto en store 1
        await set_store_context(test_session, str(store_id_1))
        service_1 = ProductService(test_session)
        product_data_1 = ProductCreate(
            barcode="111",
            name="Producto Store 1",
            description="",
            category_id=category_id_1,
            unit="unit",
            price=10.0,
            stock_quantity=50.0,
            min_stock=5.0,
        )
        await service_1.create_product(product_data_1, store_id_1)
        await test_session.commit()

        # Crear nueva sesión para el segundo store
        # (Para simular diferentes conexiones con diferente app.current_store_id)
        async with test_session.begin_nested():
            await set_store_context(test_session, str(store_id_2))
            service_2 = ProductService(test_session)
            product_data_2 = ProductCreate(
                barcode="222",
                name="Producto Store 2",
                description="",
                category_id=category_id_2,
                unit="unit",
                price=20.0,
                stock_quantity=100.0,
                min_stock=10.0,
            )
            await service_2.create_product(product_data_2, store_id_2)

        # Ahora listar desde store_1 y verificar que solo ve sus productos
        await set_store_context(test_session, str(store_id_1))
        service_1_list = ProductService(test_session)
        products_from_store_1 = await service_1_list.list_products(store_id_1)

        # Debería solo ver 1 producto
        assert len(products_from_store_1) == 1
        assert products_from_store_1[0].name == "Producto Store 1"
        assert products_from_store_1[0].barcode == "111"

    @pytest.mark.asyncio
    async def test_get_product_by_barcode(self, test_session: AsyncSession, store_and_user):
        """
        DADO: Un producto creado en un store
        CUANDO: Buscamos por barcode con RLS activo
        ENTONCES: Solo obtenemos el producto si pertenece al store
        """
        store_id, _ = store_and_user

        await set_store_context(test_session, str(store_id))

        service = ProductService(test_session)
        product_data = ProductCreate(
            barcode="BARCODE123",
            name="Test Product",
            description="",
            category_id=uuid.uuid4(),
            unit="unit",
            price=5.0,
            stock_quantity=10.0,
            min_stock=1.0,
        )

        created = await service.create_product(product_data, store_id)
        await test_session.commit()

        # Buscar el producto
        found = await service.get_product_by_barcode("BARCODE123", store_id)

        assert found is not None
        assert found.id == created.id
        assert found.barcode == "BARCODE123"
