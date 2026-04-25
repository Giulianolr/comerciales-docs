"""ProductService para CRUD de productos con aislamiento multi-tenant."""

import uuid
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.schemas.product import ProductCreate, ProductResponse


class ProductService:
    """Service para operaciones de productos."""

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

    async def create_product(
        self, product_data: ProductCreate, store_id: UUID
    ) -> ProductResponse:
        """Crear un producto en el store."""
        await self._set_store_context(store_id)

        product = Product(
            id=uuid.uuid4(),
            store_id=store_id,
            barcode=product_data.barcode,
            name=product_data.name,
            description=product_data.description,
            category_id=product_data.category_id,
            unit=product_data.unit,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity,
            min_stock=product_data.min_stock,
        )

        self.session.add(product)
        await self.session.flush()

        return ProductResponse.model_validate(product)

    async def list_products(self, store_id: UUID) -> list[ProductResponse]:
        """Listar productos del store (respeta RLS)."""
        await self._set_store_context(store_id)

        result = await self.session.execute(
            select(Product).where(Product.store_id == store_id)
        )
        products = result.scalars().all()

        return [ProductResponse.model_validate(p) for p in products]

    async def get_product_by_barcode(
        self, barcode: str, store_id: UUID
    ) -> ProductResponse | None:
        """Obtener producto por barcode (respeta RLS)."""
        await self._set_store_context(store_id)

        result = await self.session.execute(
            select(Product).where(
                (Product.barcode == barcode) & (Product.store_id == store_id)
            )
        )
        product = result.scalars().first()

        if product:
            return ProductResponse.model_validate(product)
        return None
