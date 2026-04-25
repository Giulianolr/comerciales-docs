"""Test E2E del flujo de Caja: escaneo → cobro"""
import uuid
from decimal import Decimal
import pytest
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_flujo_caja_completo(test_client: httpx.AsyncClient, test_session: AsyncSession):
    """Flujo completo: escaneo → confirmar → procesar cobro"""
    from app.models import Store, User, Category, Product, Station
    
    # Setup: crear datos
    store_id = uuid.uuid4()
    user_id = uuid.uuid4()
    station_id = uuid.uuid4()
    cat_id = uuid.uuid4()
    prod_id = uuid.uuid4()
    
    store = Store(id=store_id, name="Test Store", address="123 Main", owner_id=user_id)
    user = User(
        id=user_id, store_id=store_id, name="Test User",
        email="test@test.com", pin="1234", password_hash="hash", role="CAJERO"
    )
    station = Station(id=station_id, store_id=store_id, number=1, status="active")
    category = Category(id=cat_id, store_id=store_id, name="Frutas")
    product = Product(
        id=prod_id, store_id=store_id, barcode="PROD-TEST-001",
        name="Manzana Test", description="", category_id=cat_id,
        unit="kg", price=Decimal("2.50"), stock_quantity=100.0, min_stock=10.0
    )
    
    test_session.add_all([store, user, station, category, product])
    await test_session.commit()
    
    # 1. GET producto por barcode
    prod_response = await test_client.get(
        "/api/v1/products/barcode/PROD-TEST-001",
        headers={"X-Store-ID": str(store_id)}
    )
    assert prod_response.status_code == 200
    prod_data = prod_response.json()
    print(f"✓ Producto encontrado: {prod_data['name']}")
    
    # 2. Crear orden
    order_response = await test_client.post(
        "/api/v1/orders/",
        json={"station_id": str(station_id)},
        headers={"X-Store-ID": str(store_id)}
    )
    assert order_response.status_code == 201
    order_data = order_response.json()
    order_id = order_data["id"]
    print(f"✓ Orden creada: {order_id}")
    
    # 3. Agregar item a la orden
    item_response = await test_client.post(
        f"/api/v1/orders/{order_id}/items",
        json={"product_id": str(prod_id), "quantity": 2},
        headers={"X-Store-ID": str(store_id)}
    )
    assert item_response.status_code == 201
    item_data = item_response.json()
    print(f"✓ Item agregado. Total: ${item_data['total']}")
    
    # 4. Procesar checkout
    checkout_response = await test_client.post(
        f"/api/v1/orders/{order_id}/checkout",
        json={"payment_method": "efectivo", "amount_received": 10.0},
        headers={"X-Store-ID": str(store_id)}
    )
    assert checkout_response.status_code == 200
    checkout_data = checkout_response.json()
    assert checkout_data["status"] == "completed"
    print(f"✓ Checkout completado. Status: {checkout_data['status']}")
    
    print("\n✅ FLUJO COMPLETO EXITOSO: escaneo → cobro")

if __name__ == "__main__":
    print("Ejecutar con: cd comerciales-backend && uv run pytest /tmp/test_e2e_caja.py -xvs")
