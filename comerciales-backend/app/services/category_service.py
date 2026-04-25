"""CategoryService para CRUD de categorías con aislamiento multi-tenant."""

import uuid
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category
from app.schemas.category import CategoryCreate, CategoryResponse


class CategoryService:
    """Service para operaciones de categorías."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _set_store_context(self, store_id: UUID) -> None:
        """Inyectar store_id en contexto RLS (PostgreSQL only)."""
        try:
            await self.session.execute(
                text(f"SET LOCAL app.current_store_id = '{store_id}'")
            )
        except OperationalError:
            # SQLite no soporta SET LOCAL; solo se ignora en tests
            pass

    async def create_category(
        self, category_data: CategoryCreate, store_id: UUID
    ) -> CategoryResponse:
        """Crear una categoría en el store."""
        await self._set_store_context(store_id)

        category = Category(
            id=uuid.uuid4(),
            store_id=store_id,
            name=category_data.name,
        )

        self.session.add(category)
        await self.session.flush()

        return CategoryResponse.model_validate(category)

    async def list_categories(self, store_id: UUID) -> list[CategoryResponse]:
        """Listar categorías del store (respeta RLS)."""
        await self._set_store_context(store_id)

        result = await self.session.execute(
            select(Category).where(Category.store_id == store_id)
        )
        categories = result.scalars().all()

        return [CategoryResponse.model_validate(c) for c in categories]

    async def get_category(self, category_id: UUID, store_id: UUID) -> CategoryResponse | None:
        """Obtener categoría por ID (respeta RLS)."""
        await self._set_store_context(store_id)

        result = await self.session.execute(
            select(Category).where(
                (Category.id == category_id) & (Category.store_id == store_id)
            )
        )
        category = result.scalars().first()

        if category:
            return CategoryResponse.model_validate(category)
        return None
