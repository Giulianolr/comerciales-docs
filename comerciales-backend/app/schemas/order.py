"""Pydantic schemas para Order."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrderItemCreate(BaseModel):
    """Schema para crear un ítem en una orden."""

    product_id: UUID
    quantity: float


class OrderItemResponse(BaseModel):
    """Schema para respuesta de ítem en orden."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    product_id: UUID
    quantity: float
    unit_price: Decimal
    unit: str
    subtotal: Decimal


class OrderCreate(BaseModel):
    """Schema para crear una orden."""

    station_id: UUID


class OrderResponse(BaseModel):
    """Schema para respuesta de orden."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    uuid: str
    store_id: UUID
    station_id: UUID
    status: str
    total: Decimal
    item_count: int


class CheckoutRequest(BaseModel):
    """Schema para request de checkout."""

    payment_method: str
    amount_received: Decimal


class CheckoutResponse(BaseModel):
    """Schema para respuesta de checkout."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    uuid: str
    store_id: UUID
    station_id: UUID
    status: str
    total: Decimal
    item_count: int
