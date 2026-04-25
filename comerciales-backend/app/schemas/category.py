"""Pydantic schemas para Category."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    """Schema para crear una categoría."""

    name: str


class CategoryResponse(BaseModel):
    """Schema para respuesta de categoría."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    store_id: UUID
    name: str
