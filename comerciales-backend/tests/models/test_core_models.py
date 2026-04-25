"""Tests para modelos ORM del Core: Store, User, Category, Product."""

import uuid
from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models.core import Store, User, Category, Product


@pytest.mark.asyncio
async def test_store_creation(test_session):
    """RED: Verifica que Store se crea con UUID autogenerado."""
    # Crear owner primero
    owner = User(
        name="Admin",
        email="admin@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Mi Local",
        address="Calle Principal 123",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    assert store.id is not None
    assert isinstance(store.id, uuid.UUID)
    assert store.name == "Mi Local"
    assert store.owner_id == owner.id
    assert store.is_active is True


@pytest.mark.asyncio
async def test_user_creation_with_store(test_session):
    """RED: Verifica que User se crea con FK a Store."""
    # Crear owner primero
    owner = User(
        name="Admin",
        email="admin@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Mi Local",
        address="Calle Principal 123",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    user = User(
        store_id=store.id,
        name="Juan Pérez",
        email="juan@example.com",
        pin="1234",
        password_hash="hashed_password",
        role="CAJERO",
    )
    test_session.add(user)
    await test_session.flush()

    assert user.id is not None
    assert user.store_id == store.id
    assert user.role == "CAJERO"
    assert user.is_active is True


@pytest.mark.asyncio
async def test_store_owner_relationship(test_session):
    """RED: Verifica relación Store.owner_id -> User."""
    owner = User(
        store_id=None,  # Temporal, luego lo actualizamos
        name="Admin",
        email="admin@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Mi Local",
        address="Calle Principal 123",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    # Actualizar el store_id del owner para que coincida
    owner.store_id = store.id
    await test_session.flush()

    assert store.owner_id == owner.id


@pytest.mark.asyncio
async def test_category_creation_with_store(test_session):
    """RED: Verifica que Category se crea con FK a Store."""
    owner = User(
        name="Admin",
        email="admin@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Mi Local",
        address="Calle Principal 123",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    category = Category(
        store_id=store.id,
        name="Frutas",
        description="Productos frescos de frutas",
    )
    test_session.add(category)
    await test_session.flush()

    assert category.id is not None
    assert category.store_id == store.id
    assert category.name == "Frutas"


@pytest.mark.asyncio
async def test_product_creation_with_category(test_session):
    """RED: Verifica que Product se crea con FK a Store y Category."""
    owner = User(
        name="Admin",
        email="admin@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Mi Local",
        address="Calle Principal 123",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    category = Category(
        store_id=store.id,
        name="Frutas",
        description="Productos frescos",
    )
    test_session.add(category)
    await test_session.flush()

    product = Product(
        store_id=store.id,
        category_id=category.id,
        barcode="1234567890123",
        name="Manzana Roja",
        unit="kg",
        price=Decimal("2.50"),
        stock_quantity=Decimal("100.0"),
    )
    test_session.add(product)
    await test_session.flush()

    assert product.id is not None
    assert product.store_id == store.id
    assert product.category_id == category.id
    assert product.barcode == "1234567890123"
    assert product.price == Decimal("2.50")


@pytest.mark.asyncio
async def test_product_multi_tenant_isolation(test_session):
    """RED: Verifica que Products respetan multi-tenant (store_id)."""
    owner1 = User(
        name="Owner 1",
        email="owner1@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    owner2 = User(
        name="Owner 2",
        email="owner2@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner1)
    test_session.add(owner2)
    await test_session.flush()

    store1 = Store(
        name="Local 1",
        address="Calle 1",
        owner_id=owner1.id,
        sii_rut="11.111.111-1",
    )
    store2 = Store(
        name="Local 2",
        address="Calle 2",
        owner_id=owner2.id,
        sii_rut="22.222.222-2",
    )
    test_session.add(store1)
    test_session.add(store2)
    await test_session.flush()

    cat1 = Category(store_id=store1.id, name="Cat1")
    cat2 = Category(store_id=store2.id, name="Cat2")
    test_session.add(cat1)
    test_session.add(cat2)
    await test_session.flush()

    prod1 = Product(
        store_id=store1.id,
        category_id=cat1.id,
        barcode="111",
        name="Product 1",
        unit="kg",
        price=Decimal("1.0"),
        stock_quantity=Decimal("10.0"),
    )
    prod2 = Product(
        store_id=store2.id,
        category_id=cat2.id,
        barcode="222",
        name="Product 2",
        unit="kg",
        price=Decimal("2.0"),
        stock_quantity=Decimal("20.0"),
    )
    test_session.add(prod1)
    test_session.add(prod2)
    await test_session.flush()

    # Verificar que se pueden recuperar por store_id
    stmt = select(Product).where(Product.store_id == store1.id)
    result = await test_session.execute(stmt)
    products_store1 = result.scalars().all()

    assert len(products_store1) == 1
    assert products_store1[0].barcode == "111"


@pytest.mark.asyncio
async def test_category_unique_constraint(test_session):
    """RED: Verifica que Category respeta unicidad (store_id, name)."""
    owner = User(
        name="Admin",
        email="admin@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Mi Local",
        address="Calle Principal 123",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    cat1 = Category(store_id=store.id, name="Frutas")
    test_session.add(cat1)
    await test_session.flush()

    # Intenta crear otra categoría con el mismo nombre en el mismo store
    cat2 = Category(store_id=store.id, name="Frutas")
    test_session.add(cat2)

    with pytest.raises(Exception):  # IntegrityError
        await test_session.flush()


@pytest.mark.asyncio
async def test_product_barcode_unique_constraint(test_session):
    """RED: Verifica que Product respeta unicidad (store_id, barcode)."""
    owner = User(
        name="Admin",
        email="admin@example.com",
        pin="0000",
        password_hash="hashed",
        role="ADMIN",
    )
    test_session.add(owner)
    await test_session.flush()

    store = Store(
        name="Mi Local",
        address="Calle Principal 123",
        owner_id=owner.id,
        sii_rut="12.345.678-9",
    )
    test_session.add(store)
    await test_session.flush()

    category = Category(store_id=store.id, name="Frutas")
    test_session.add(category)
    await test_session.flush()

    prod1 = Product(
        store_id=store.id,
        category_id=category.id,
        barcode="1234567890",
        name="Manzana",
        unit="kg",
        price=Decimal("2.50"),
        stock_quantity=Decimal("100.0"),
    )
    test_session.add(prod1)
    await test_session.flush()

    # Intenta crear otro producto con el mismo barcode en el mismo store
    prod2 = Product(
        store_id=store.id,
        category_id=category.id,
        barcode="1234567890",
        name="Pera",
        unit="kg",
        price=Decimal("3.0"),
        stock_quantity=Decimal("50.0"),
    )
    test_session.add(prod2)

    with pytest.raises(Exception):  # IntegrityError
        await test_session.flush()
