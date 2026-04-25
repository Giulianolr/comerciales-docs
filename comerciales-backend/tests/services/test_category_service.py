"""Tests para CategoryService (TDD - RED → GREEN → REFACTOR).
Verifica: CRUD de categorías + aislamiento multi-tenant.
"""

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category, Store, User
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.category_service import CategoryService


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


class TestCategoryService:
    """Tests para CategoryService."""

    @pytest.mark.asyncio
    async def test_create_category_success(self, test_session: AsyncSession, store_and_user):
        """
        DADO: Un CategoryService con una sesión de test
        CUANDO: Creamos una categoría válida para un store
        ENTONCES: La categoría se crea y se retorna con todos los datos correctos
        """
        store_id, _ = store_and_user

        await set_store_context(test_session, str(store_id))

        service = CategoryService(test_session)
        category_data = CategoryCreate(name="Frutas")

        result = await service.create_category(category_data, store_id)

        assert result.name == "Frutas"
        assert result.store_id == store_id

    @pytest.mark.asyncio
    async def test_list_categories_respects_tenant_isolation(
        self, test_session: AsyncSession, store_and_user
    ):
        """
        DADO: Dos stores con categorías diferentes
        CUANDO: Listamos categorías con store_id inyectado
        ENTONCES: Solo vemos categorías del store actual (CRÍTICA PARA SEGURIDAD)
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

        # Crear categorías en ambos stores
        await set_store_context(test_session, str(store_id_1))
        service_1 = CategoryService(test_session)
        category_data_1 = CategoryCreate(name="Frutas")
        await service_1.create_category(category_data_1, store_id_1)
        await test_session.commit()

        # Crear categoría en store 2
        async with test_session.begin_nested():
            await set_store_context(test_session, str(store_id_2))
            service_2 = CategoryService(test_session)
            category_data_2 = CategoryCreate(name="Verduras")
            await service_2.create_category(category_data_2, store_id_2)

        # Ahora listar desde store_1 y verificar que solo ve sus categorías
        await set_store_context(test_session, str(store_id_1))
        service_1_list = CategoryService(test_session)
        categories_from_store_1 = await service_1_list.list_categories(store_id_1)

        # Debería solo ver 1 categoría
        assert len(categories_from_store_1) == 1
        assert categories_from_store_1[0].name == "Frutas"

        # Ahora listar desde store_2 y verificar que ve su propia categoría
        await set_store_context(test_session, str(store_id_2))
        service_2_list = CategoryService(test_session)
        categories_from_store_2 = await service_2_list.list_categories(store_id_2)

        # Debería solo ver 1 categoría (la suya)
        assert len(categories_from_store_2) == 1
        assert categories_from_store_2[0].name == "Verduras"

    @pytest.mark.asyncio
    async def test_get_category_by_id(self, test_session: AsyncSession, store_and_user):
        """
        DADO: Una categoría creada en un store
        CUANDO: Buscamos por ID con store_id inyectado
        ENTONCES: Solo obtenemos la categoría si pertenece al store
        """
        store_id, _ = store_and_user

        await set_store_context(test_session, str(store_id))

        service = CategoryService(test_session)
        category_data = CategoryCreate(name="Bebidas")

        created = await service.create_category(category_data, store_id)
        await test_session.commit()

        # Buscar la categoría
        found = await service.get_category(created.id, store_id)

        assert found is not None
        assert found.id == created.id
        assert found.name == "Bebidas"

    @pytest.mark.asyncio
    async def test_get_category_returns_none_for_wrong_store(
        self, test_session: AsyncSession, store_and_user
    ):
        """
        DADO: Una categoría en store A
        CUANDO: Intentamos obtenerla con store_id de store B
        ENTONCES: Retorna None (aislamiento multi-tenant)
        """
        store_id_1, _ = store_and_user
        store_id_2 = uuid.uuid4()

        # Crear segundo store
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

        # Crear categoría en store 1
        await set_store_context(test_session, str(store_id_1))
        service_1 = CategoryService(test_session)
        category_data = CategoryCreate(name="Lacteos")
        created = await service_1.create_category(category_data, store_id_1)
        await test_session.commit()

        # Intentar obtener desde store 2
        await set_store_context(test_session, str(store_id_2))
        service_2 = CategoryService(test_session)
        found = await service_2.get_category(created.id, store_id_2)

        # Debe retornar None porque la categoría no pertenece a este store
        assert found is None
