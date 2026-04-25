"""Pydantic schemas para Transaction."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    """Schema para crear una transacción."""

    order_id: UUID
    payment_method: str
    amount_paid: Decimal
    change_amount: Decimal | None = None


class TransactionResponse(BaseModel):
    """Schema para respuesta de transacción."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    store_id: UUID
    user_id: UUID
    payment_method: str
    amount_paid: Decimal
    change_amount: Decimal | None
    status: str
