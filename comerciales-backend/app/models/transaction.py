"""Modelos transaccionales: Station, Order, OrderItem, Transaction, Boleta.
SQLAlchemy 2.0 con Mapped y mapped_column.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, LargeBinary, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.core import Store, User, Product


class Station(Base):
    """Estación de pesaje/balanza (máximo 4 por local)."""

    __tablename__ = "stations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    store_id: Mapped[UUID] = mapped_column(ForeignKey("stores.id"), nullable=False)
    number: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="idle")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    __table_args__ = (
        Index("idx_stations_store_id", "store_id"),
        UniqueConstraint("store_id", "number", name="uq_stations_store_number"),
    )

    # Relationships
    store: Mapped[Store] = relationship(foreign_keys=[store_id])
    orders: Mapped[list["Order"]] = relationship(back_populates="station", lazy="selectin")


class Order(Base):
    """Pre-orden en balanza (antes de confirmar en caja)."""

    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    store_id: Mapped[UUID] = mapped_column(ForeignKey("stores.id"), nullable=False)
    station_id: Mapped[UUID] = mapped_column(ForeignKey("stations.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    item_count: Mapped[int] = mapped_column(default=0)
    qr_code: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    __table_args__ = (
        Index("idx_orders_by_uuid", "store_id", "uuid"),
        Index("idx_orders_store_id", "store_id"),
        Index("idx_orders_station_id", "station_id"),
        Index("idx_orders_created_at", "created_at"),
    )

    # Relationships
    store: Mapped[Store] = relationship(foreign_keys=[store_id])
    station: Mapped[Station] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan", lazy="selectin")
    transaction: Mapped[Optional["Transaction"]] = relationship(back_populates="order", uselist=False, lazy="selectin")


class OrderItem(Base):
    """Item dentro de una pre-orden."""

    __tablename__ = "order_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

    __table_args__ = (
        Index("idx_order_items_order_id", "order_id"),
        Index("idx_order_items_product_id", "product_id"),
    )

    # Relationships
    order: Mapped[Order] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(foreign_keys=[product_id])


class Transaction(Base):
    """Transacción de venta (confirmación en caja)."""

    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id"), unique=True, nullable=False
    )
    store_id: Mapped[UUID] = mapped_column(ForeignKey("stores.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    change_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="completed")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    __table_args__ = (
        Index("idx_transactions_store_id", "store_id"),
        Index("idx_transactions_user_id", "user_id"),
        Index("idx_transactions_order_id", "order_id"),
        Index("idx_transactions_by_date", "store_id", "created_at"),
    )

    # Relationships
    order: Mapped[Order] = relationship(back_populates="transaction")
    store: Mapped[Store] = relationship(foreign_keys=[store_id])
    user: Mapped[User] = relationship(foreign_keys=[user_id])
    boleta: Mapped[Optional["Boleta"]] = relationship(back_populates="transaction", uselist=False, lazy="selectin")


class Boleta(Base):
    """Boleta SII (Documento Tributario Electrónico)."""

    __tablename__ = "boletas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    transaction_id: Mapped[UUID] = mapped_column(
        ForeignKey("transactions.id"), unique=True, nullable=False
    )
    folio_sii: Mapped[Optional[int]] = mapped_column(nullable=True)
    xml_dte: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    emission_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    external_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    __table_args__ = (
        Index("idx_boletas_transaction_id", "transaction_id"),
        Index("idx_boletas_folio_sii", "folio_sii"),
        Index("idx_boletas_status", "status"),
    )

    # Relationships
    transaction: Mapped[Transaction] = relationship(back_populates="boleta")
