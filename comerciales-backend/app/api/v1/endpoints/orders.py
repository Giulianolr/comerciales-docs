"""Endpoints para gestión de órdenes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_store_id
from app.schemas.order import (
    CheckoutRequest,
    CheckoutResponse,
    OrderCreate,
    OrderItemCreate,
    OrderResponse,
)
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    store_id: UUID = Depends(get_store_id),
    db: AsyncSession = Depends(get_db),
):
    """Crear una nueva pre-orden."""
    try:
        service = OrderService(db)
        result = await service.create_order(order_data, store_id)
        await db.commit()
        return result
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/items", status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
async def add_item_to_order(
    order_id: UUID,
    item_data: OrderItemCreate,
    store_id: UUID = Depends(get_store_id),
    db: AsyncSession = Depends(get_db),
):
    """Añadir un ítem a una orden."""
    try:
        service = OrderService(db)
        await service.add_item_to_order(order_id, item_data, store_id)
        await db.commit()
        updated_order = await service.get_order_by_id(order_id, store_id)
        if not updated_order:
            raise ValueError(f"Orden {order_id} no encontrada")
        return updated_order
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/checkout", status_code=status.HTTP_200_OK, response_model=CheckoutResponse)
async def checkout_order(
    order_id: UUID,
    checkout_data: CheckoutRequest,
    store_id: UUID = Depends(get_store_id),
    db: AsyncSession = Depends(get_db),
):
    """Procesar checkout de una orden."""
    try:
        service = OrderService(db)
        result = await service.checkout_order(
            order_id,
            checkout_data.payment_method,
            checkout_data.amount_received,
            store_id,
        )
        await db.commit()
        return result
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
