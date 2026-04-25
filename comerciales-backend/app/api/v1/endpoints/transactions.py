"""Endpoints para gestión de transacciones."""

import json
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_store_id
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TransactionResponse)
async def process_payment(
    transaction_data: TransactionCreate,
    store_id: UUID = Depends(get_store_id),
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Procesar el pago de una orden.

    Requiere headers:
    - X-Store-ID: UUID del store
    - X-User-ID: UUID del usuario (cajero)
    """
    try:
        user_id = UUID(x_user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid X-User-ID header")

    try:
        service = TransactionService(db)
        result = await service.process_payment(
            order_id=transaction_data.order_id,
            transaction_data=transaction_data,
            user_id=user_id,
            store_id=store_id,
        )

        # Publicar evento de venta a Redis para que WebSocket lo difunda
        from app.core.events import get_redis_manager

        redis_manager = get_redis_manager()
        if redis_manager is not None:
            channel = f"sales:{store_id}"
            event = {
                "type": "sale",
                "transaction_id": str(result.id),
                "order_id": str(result.order_id),
                "amount": str(result.amount_paid),
                "payment_method": result.payment_method,
            }
            await redis_manager.publish(channel, json.dumps(event))

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
