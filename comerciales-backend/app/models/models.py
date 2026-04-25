"""
Modelos ORM para el Sistema de Inventario Dinámico.
SQLAlchemy 2.0 + asyncpg + PostgreSQL 15
Multi-tenant con aislamiento por store_id.

Modelos importados de submódulos:
- Core: Store, User, Category, Product
- Transaction: Station, Order, OrderItem, Transaction, Boleta
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    UUID,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    CheckConstraint,
    Column,
    JSON,
    func,
)
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.core import Store, User, Category, Product
from app.models.transaction import Station, Order, OrderItem, Transaction, Boleta
from app.models.audit import InventoryMovement, AuditLog
