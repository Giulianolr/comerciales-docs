"""Endpoints para gestión de productos."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_store_id
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    store_id: UUID = Depends(get_store_id),
    db: AsyncSession = Depends(get_db),
):
    """Crear un nuevo producto."""
    try:
        service = ProductService(db)
        result = await service.create_product(product_data, store_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    store_id: UUID = Depends(get_store_id),
    db: AsyncSession = Depends(get_db),
):
    """Listar productos del store."""
    try:
        service = ProductService(db)
        results = await service.list_products(store_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/barcode/{barcode}", response_model=ProductResponse)
async def get_product_by_barcode(
    barcode: str,
    store_id: UUID = Depends(get_store_id),
    db: AsyncSession = Depends(get_db),
):
    """Obtener producto por código de barras."""
    try:
        service = ProductService(db)
        product = await service.get_product_by_barcode(barcode, store_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con código de barras '{barcode}' no encontrado",
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
