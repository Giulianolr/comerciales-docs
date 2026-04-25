"""Modelos ORM del Core: Store, User, Category, Product.
SQLAlchemy 2.0 con Mapped y mapped_column.
Multi-tenant con aislamiento por store_id.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.models import Station, Order, Transaction


class Store(Base):
    """Almacén/Local comercial — raíz del multi-tenant."""

    __tablename__ = "stores"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    sii_rut: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    __table_args__ = (
        Index("idx_stores_owner_id", "owner_id"),
        Index("idx_stores_sii_rut", "sii_rut"),
    )

    # Relationships (Core models only)
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id], back_populates="owned_stores")
    users: Mapped[list["User"]] = relationship(foreign_keys="User.store_id", back_populates="store")
    categories: Mapped[list["Category"]] = relationship(back_populates="store")
    products: Mapped[list["Product"]] = relationship(back_populates="store")


class User(Base):
    """Usuario del sistema (ADMIN, GERENTE, CAJERO, OPERADOR)."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    store_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("stores.id"), nullable=True, default=None)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    pin: Mapped[str] = mapped_column(String(4), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    __table_args__ = (
        Index("idx_users_store_id", "store_id"),
        Index("idx_users_email", "email"),
        Index("idx_users_role", "role"),
    )

    # Relationships
    store: Mapped[Optional["Store"]] = relationship(foreign_keys=[store_id], back_populates="users")
    owned_stores: Mapped[list["Store"]] = relationship(foreign_keys=[Store.owner_id], back_populates="owner")


class Category(Base):
    """Categoría de productos."""

    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    store_id: Mapped[UUID] = mapped_column(ForeignKey("stores.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    __table_args__ = (
        Index("idx_categories_store_id", "store_id"),
        UniqueConstraint("store_id", "name", name="uq_categories_store_name"),
    )

    # Relationships
    store: Mapped["Store"] = relationship(back_populates="categories")
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base):
    """Producto del inventario."""

    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    store_id: Mapped[UUID] = mapped_column(ForeignKey("stores.id"), nullable=False)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id"), nullable=False)
    barcode: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), default=Decimal("0"), nullable=False)
    min_stock: Mapped[Decimal] = mapped_column(Numeric(10, 3), default=Decimal("0"), nullable=False)
    reorder_quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    supplier_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    __table_args__ = (
        Index("idx_products_by_barcode", "store_id", "barcode"),
        Index("idx_products_store_id", "store_id"),
        Index("idx_products_category_id", "category_id"),
        UniqueConstraint("store_id", "barcode", name="uq_products_store_barcode"),
    )

    # Relationships
    store: Mapped["Store"] = relationship(back_populates="products")
    category: Mapped["Category"] = relationship(back_populates="products")
