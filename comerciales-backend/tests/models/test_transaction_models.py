"""Tests para modelos transaccionales: Station, Order, OrderItem, Transaction, Boleta."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models.core import Store, User, Product, Category
from app.models.transaction import Station, Order, OrderItem, Transaction, Boleta


@pytest.mark.asyncio
async def test_station_creation(test_session):
    """Verifica que Station se crea correctamente."""
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

    station = Station(
        store_id=store.id,
        number=1,
        status="idle",
    )
    test_session.add(station)
    await test_session.flush()

    assert station.id is not None
    assert station.store_id == store.id
    assert station.number == 1
    assert station.status == "idle"


@pytest.mark.asyncio
async def test_order_creation_with_uuid(test_session):
    """Verifica que Order se crea con UUID único para QR."""
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

    station = Station(store_id=store.id, number=1)
    test_session.add(station)
    await test_session.flush()

    order = Order(
        uuid=str(uuid.uuid4()),
        store_id=store.id,
        station_id=station.id,
        status="pending",
        total=Decimal("0.00"),
    )
    test_session.add(order)
    await test_session.flush()

    assert order.id is not None
    assert order.uuid is not None
    assert order.status == "pending"
    assert order.total == Decimal("0.00")


@pytest.mark.asyncio
async def test_order_items_cascade_delete(test_session):
    """Verifica que al eliminar Order se eliminan sus OrderItems (cascada)."""
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

    station = Station(store_id=store.id, number=1)
    test_session.add(station)
    await test_session.flush()

    order = Order(
        uuid=str(uuid.uuid4()),
        store_id=store.id,
        station_id=station.id,
        status="pending",
        total=Decimal("0.00"),
    )
    test_session.add(order)
    await test_session.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=Decimal("5.0"),
        unit_price=Decimal("2.50"),
        unit="kg",
        subtotal=Decimal("12.50"),
    )
    test_session.add(order_item)
    await test_session.flush()

    order_id = order.id
    item_id = order_item.id

    # Eliminar la orden
    await test_session.delete(order)
    await test_session.flush()

    # Verificar que el OrderItem también fue eliminado (cascada)
    stmt = select(OrderItem).where(OrderItem.id == item_id)
    result = await test_session.execute(stmt)
    deleted_item = result.scalars().first()

    assert deleted_item is None


@pytest.mark.asyncio
async def test_order_items_relationship(test_session):
    """Verifica que Order y OrderItem tienen relación correcta."""
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

    station = Station(store_id=store.id, number=1)
    test_session.add(station)
    await test_session.flush()

    order = Order(
        uuid=str(uuid.uuid4()),
        store_id=store.id,
        station_id=station.id,
        status="pending",
        total=Decimal("12.50"),
    )
    test_session.add(order)
    await test_session.flush()

    item1 = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=Decimal("5.0"),
        unit_price=Decimal("2.50"),
        unit="kg",
        subtotal=Decimal("12.50"),
    )
    test_session.add(item1)
    await test_session.flush()

    # Recargar order para que las relaciones se carguen
    stmt = select(Order).where(Order.id == order.id)
    result = await test_session.execute(stmt)
    reloaded_order = result.scalars().first()

    # Verificar relación
    assert reloaded_order is not None
    assert len(reloaded_order.items) == 1
    assert reloaded_order.items[0].product_id == product.id


@pytest.mark.asyncio
async def test_transaction_one_to_one_with_order(test_session):
    """Verifica que Transaction y Order tienen relación 1-a-1."""
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
        name="Cajero",
        email="cajero@example.com",
        pin="1234",
        password_hash="hashed",
        role="CAJERO",
    )
    test_session.add(user)
    await test_session.flush()

    station = Station(store_id=store.id, number=1)
    test_session.add(station)
    await test_session.flush()

    order = Order(
        uuid=str(uuid.uuid4()),
        store_id=store.id,
        station_id=station.id,
        status="confirmed",
        total=Decimal("50.00"),
    )
    test_session.add(order)
    await test_session.flush()

    transaction = Transaction(
        order_id=order.id,
        store_id=store.id,
        user_id=user.id,
        payment_method="cash",
        amount_paid=Decimal("50.00"),
        status="completed",
    )
    test_session.add(transaction)
    await test_session.flush()

    assert transaction.id is not None
    assert transaction.order_id == order.id
    assert transaction.amount_paid == Decimal("50.00")

    # Recargar order para verificar relación
    stmt = select(Order).where(Order.id == order.id)
    result = await test_session.execute(stmt)
    reloaded_order = result.scalars().first()
    assert reloaded_order.transaction is not None


@pytest.mark.asyncio
async def test_boleta_one_to_one_with_transaction(test_session):
    """Verifica que Boleta y Transaction tienen relación 1-a-1."""
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
        name="Cajero",
        email="cajero@example.com",
        pin="1234",
        password_hash="hashed",
        role="CAJERO",
    )
    test_session.add(user)
    await test_session.flush()

    station = Station(store_id=store.id, number=1)
    test_session.add(station)
    await test_session.flush()

    order = Order(
        uuid=str(uuid.uuid4()),
        store_id=store.id,
        station_id=station.id,
        status="confirmed",
        total=Decimal("50.00"),
    )
    test_session.add(order)
    await test_session.flush()

    transaction = Transaction(
        order_id=order.id,
        store_id=store.id,
        user_id=user.id,
        payment_method="cash",
        amount_paid=Decimal("50.00"),
        status="completed",
    )
    test_session.add(transaction)
    await test_session.flush()

    boleta = Boleta(
        transaction_id=transaction.id,
        folio_sii=1001,
        status="emitted",
    )
    test_session.add(boleta)
    await test_session.flush()

    assert boleta.id is not None
    assert boleta.transaction_id == transaction.id
    assert boleta.folio_sii == 1001

    # Recargar transaction para verificar relación
    stmt = select(Transaction).where(Transaction.id == transaction.id)
    result = await test_session.execute(stmt)
    reloaded_transaction = result.scalars().first()
    assert reloaded_transaction.boleta is not None


@pytest.mark.asyncio
async def test_transaction_unique_constraint_on_order(test_session):
    """Verifica que cada Order solo puede tener una Transaction."""
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
        name="Cajero",
        email="cajero@example.com",
        pin="1234",
        password_hash="hashed",
        role="CAJERO",
    )
    test_session.add(user)
    await test_session.flush()

    station = Station(store_id=store.id, number=1)
    test_session.add(station)
    await test_session.flush()

    order = Order(
        uuid=str(uuid.uuid4()),
        store_id=store.id,
        station_id=station.id,
        status="confirmed",
        total=Decimal("50.00"),
    )
    test_session.add(order)
    await test_session.flush()

    transaction1 = Transaction(
        order_id=order.id,
        store_id=store.id,
        user_id=user.id,
        payment_method="cash",
        amount_paid=Decimal("50.00"),
        status="completed",
    )
    test_session.add(transaction1)
    await test_session.flush()

    # Intentar crear una segunda Transaction para la misma Order
    transaction2 = Transaction(
        order_id=order.id,
        store_id=store.id,
        user_id=user.id,
        payment_method="debit",
        amount_paid=Decimal("50.00"),
        status="completed",
    )
    test_session.add(transaction2)

    with pytest.raises(Exception):  # IntegrityError
        await test_session.flush()
