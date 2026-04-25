"""Tests para modelos de auditoría: InventoryMovement, AuditLog."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models.core import Store, User, Product, Category
from app.models.transaction import Station, Order, OrderItem, Transaction
from app.models.audit import InventoryMovement, AuditLog


@pytest.mark.asyncio
async def test_inventory_movement_creation(test_session):
    """Verifica que InventoryMovement se crea correctamente."""
    owner = User(
        name="Owner",
        email="owner@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Local",
        address="Calle Principal",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    user = User(
        store_id=store.id,
        name="Operador",
        email="operador@example.com",
        pin="1234",
        password_hash="hashed",
        role="OPERADOR",
    )
    test_session.add(user)
    await test_session.flush()

    category = Category(store_id=store.id, name="Frutas")
    test_session.add(category)
    await test_session.flush()

    product = Product(
        store_id=store.id,
        category_id=category.id,
        barcode="123456",
        name="Manzana",
        unit="kg",
        price=Decimal("2.50"),
    )
    test_session.add(product)
    await test_session.flush()

    movement = InventoryMovement(
        product_id=product.id,
        transaction_id=None,
        user_id=user.id,
        type="adjustment",
        quantity_before=Decimal("100.0"),
        quantity_after=Decimal("95.0"),
        delta=Decimal("-5.0"),
        reason="Ajuste por pérdida",
    )
    test_session.add(movement)
    await test_session.flush()

    assert movement.id is not None
    assert movement.product_id == product.id
    assert movement.type == "adjustment"
    assert movement.delta == Decimal("-5.0")


@pytest.mark.asyncio
async def test_inventory_movement_with_transaction(test_session):
    """Verifica que InventoryMovement se asocia con Transaction."""
    owner = User(
        name="Owner",
        email="owner@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Local",
        address="Calle Principal",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    cashier = User(
        store_id=store.id,
        name="Cajero",
        email="cajero@example.com",
        pin="1234",
        password_hash="hashed",
        role="CAJERO",
    )
    test_session.add(cashier)
    await test_session.flush()

    operator = User(
        store_id=store.id,
        name="Operador",
        email="operador@example.com",
        pin="5678",
        password_hash="hashed",
        role="OPERADOR",
    )
    test_session.add(operator)
    await test_session.flush()

    category = Category(store_id=store.id, name="Frutas")
    test_session.add(category)
    await test_session.flush()

    product = Product(
        store_id=store.id,
        category_id=category.id,
        barcode="123456",
        name="Manzana",
        unit="kg",
        price=Decimal("2.50"),
        stock_quantity=Decimal("100.0"),
    )
    test_session.add(product)
    await test_session.flush()

    station = Station(store_id=store.id, number=1)
    test_session.add(station)
    await test_session.flush()

    order = Order(
        uuid=str(uuid.uuid4()),
        store_id=store.id,
        station_id=station.id,
        status="confirmed",
        total=Decimal("2.50"),
    )
    test_session.add(order)
    await test_session.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=Decimal("1.0"),
        unit_price=Decimal("2.50"),
        unit="kg",
        subtotal=Decimal("2.50"),
    )
    test_session.add(order_item)
    await test_session.flush()

    transaction = Transaction(
        order_id=order.id,
        store_id=store.id,
        user_id=cashier.id,
        payment_method="cash",
        amount_paid=Decimal("2.50"),
        status="completed",
    )
    test_session.add(transaction)
    await test_session.flush()

    movement = InventoryMovement(
        product_id=product.id,
        transaction_id=transaction.id,
        user_id=operator.id,
        type="sale",
        quantity_before=Decimal("100.0"),
        quantity_after=Decimal("99.0"),
        delta=Decimal("-1.0"),
        reason="Venta por transacción",
    )
    test_session.add(movement)
    await test_session.flush()

    assert movement.id is not None
    assert movement.transaction_id == transaction.id
    assert movement.type == "sale"


@pytest.mark.asyncio
async def test_audit_log_creation(test_session):
    """Verifica que AuditLog se crea correctamente."""
    owner = User(
        name="Owner",
        email="owner@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Local",
        address="Calle Principal",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    user = User(
        store_id=store.id,
        name="Admin",
        email="admin@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(user)
    await test_session.flush()

    audit_log = AuditLog(
        user_id=user.id,
        action="UPDATE",
        entity_type="Product",
        entity_id=uuid.uuid4(),
        old_values={"price": 2.50, "name": "Manzana Verde"},
        new_values={"price": 3.00, "name": "Manzana Roja"},
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0",
        status="success",
    )
    test_session.add(audit_log)
    await test_session.flush()

    assert audit_log.id is not None
    assert audit_log.action == "UPDATE"
    assert audit_log.entity_type == "Product"
    assert audit_log.old_values["price"] == 2.50
    assert audit_log.new_values["price"] == 3.00


@pytest.mark.asyncio
async def test_audit_log_nullable_user(test_session):
    """Verifica que AuditLog puede ser creado sin user_id (sistema automático)."""
    audit_log = AuditLog(
        user_id=None,
        action="DELETE",
        entity_type="Order",
        entity_id=uuid.uuid4(),
        old_values={"status": "pending", "total": 50.00},
        new_values=None,
        status="success",
    )
    test_session.add(audit_log)
    await test_session.flush()

    assert audit_log.id is not None
    assert audit_log.user_id is None
    assert audit_log.action == "DELETE"


@pytest.mark.asyncio
async def test_multiple_inventory_movements(test_session):
    """Verifica que se pueden crear múltiples movimientos de inventario."""
    owner = User(
        name="Owner",
        email="owner@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Local",
        address="Calle Principal",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    user = User(
        store_id=store.id,
        name="Operador",
        email="operador@example.com",
        pin="1234",
        password_hash="hashed",
        role="OPERADOR",
    )
    test_session.add(user)
    await test_session.flush()

    category = Category(store_id=store.id, name="Frutas")
    test_session.add(category)
    await test_session.flush()

    product = Product(
        store_id=store.id,
        category_id=category.id,
        barcode="123456",
        name="Manzana",
        unit="kg",
        price=Decimal("2.50"),
    )
    test_session.add(product)
    await test_session.flush()

    # Crear múltiples movimientos
    for i in range(3):
        movement = InventoryMovement(
            product_id=product.id,
            transaction_id=None,
            user_id=user.id,
            type="adjustment" if i % 2 == 0 else "restock",
            quantity_before=Decimal("100.0"),
            quantity_after=Decimal(str(100 - (i + 1) * 10)),
            delta=Decimal(str(-(i + 1) * 10)),
            reason=f"Movimiento {i + 1}",
        )
        test_session.add(movement)

    await test_session.flush()

    # Verificar que se crearon todos
    stmt = select(InventoryMovement).where(InventoryMovement.product_id == product.id)
    result = await test_session.execute(stmt)
    movements = result.scalars().all()

    assert len(movements) == 3


@pytest.mark.asyncio
async def test_audit_log_with_json_data(test_session):
    """Verifica que AuditLog maneja correctamente datos JSON complejos."""
    audit_log = AuditLog(
        user_id=None,
        action="UPDATE",
        entity_type="Order",
        entity_id=uuid.uuid4(),
        old_values={
            "status": "pending",
            "total": 100.50,
            "items": [
                {"product_id": str(uuid.uuid4()), "quantity": 2, "price": 50.25}
            ],
            "nested": {"key": "value", "count": 42},
        },
        new_values={
            "status": "confirmed",
            "total": 100.50,
            "items": [
                {"product_id": str(uuid.uuid4()), "quantity": 2, "price": 50.25}
            ],
            "nested": {"key": "updated_value", "count": 43},
        },
        status="success",
    )
    test_session.add(audit_log)
    await test_session.flush()

    assert audit_log.id is not None
    assert audit_log.old_values["nested"]["key"] == "value"
    assert audit_log.new_values["nested"]["count"] == 43
