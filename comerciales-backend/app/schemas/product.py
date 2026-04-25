"""Pydantic schemas para Product."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    """Schema para crear un producto."""

    barcode: str
    name: str
    description: str = ""
    category_id: UUID
    unit: str
    price: Decimal
    stock_quantity: float
    min_stock: float


class ProductResponse(BaseModel):
    """Schema para respuesta de producto."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    barcode: str
    name: str
    description: str | None = ""
    category_id: UUID
    unit: str
    price: Decimal
    stock_quantity: float
    min_stock: float
