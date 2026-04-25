"""Modelos de auditoría inmutable: InventoryMovement, AuditLog.
SQLAlchemy 2.0 con Mapped y mapped_column.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, JSON, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.core import Product, User
from app.models.transaction import Transaction


class InventoryMovement(Base):
    """Movimiento de inventario (auditoría de stock)."""

    __tablename__ = "inventory_movements"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    transaction_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("transactions.id"), nullable=True, default=None
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity_before: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    quantity_after: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    delta: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

    __table_args__ = (
        Index("idx_inventory_movements_product_id", "product_id"),
        Index("idx_inventory_movements_transaction_id", "transaction_id"),
        Index("idx_inventory_movements_type", "type"),
        Index("idx_inventory_movements_timeline", "product_id", "created_at"),
        Index("idx_inventory_movements_user_id", "user_id"),
    )

    # Relationships
    product: Mapped[Product] = relationship(foreign_keys=[product_id])
    transaction: Mapped[Optional[Transaction]] = relationship(foreign_keys=[transaction_id])
    user: Mapped[User] = relationship(foreign_keys=[user_id])


class AuditLog(Base):
    """Log de auditoría del sistema (inmutable)."""

    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True, default=None
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    old_values: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="success")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

    __table_args__ = (
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_entity_type", "entity_type"),
        Index("idx_audit_logs_timeline", "created_at"),
    )

    # Relationships
    user: Mapped[Optional[User]] = relationship(foreign_keys=[user_id])
