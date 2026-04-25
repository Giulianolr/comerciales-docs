#!/usr/bin/env python3
"""Script E2E Simple: Simula agregar items a una orden cada 2 segundos.

Este script es una versión simplificada que:
1. Crea un token JWT para un usuario
2. Crea una orden
3. Agrega 3 productos cada 2 segundos
4. Muestra el estado actualizado

Nota: Este test NO usa WebSocket (requiere más setup de Redis).
      Muestra cómo se agregan items vía HTTP API.
"""

import asyncio
import time
import uuid
from uuid import UUID

import httpx
from app.core.security import create_access_token

# Configuración
API_BASE = "http://localhost:8000/api/v1"
TEST_STORE_ID = "11111111-1111-1111-1111-111111111111"  # Sucursal Central
TEST_USER_ID = "33333333-3333-3333-3333-333333333333"   # Cajero Uno
TEST_STATION_ID = "77777777-7777-7777-7777-777777777777"  # Station creada

# Productos del seed (IDs reales)
TEST_PRODUCTS = [
    ("66666666-6666-6666-6666-666666666661", "Queso Mantecoso", 8500),
    ("66666666-6666-6666-6666-666666666662", "Queso Gouda", 12500),
    ("66666666-6666-6666-6666-666666666663", "Salame Milán", 14000),
]


class SimpleOrderSimulator:
    """Simulador simple que agrega items a una orden."""

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=API_BASE, timeout=10.0, follow_redirects=True
        )
        self.user_id = TEST_USER_ID
        self.token = create_access_token(UUID(TEST_USER_ID))
        self.order_id = None
        self.store_id = TEST_STORE_ID

    async def create_order(self) -> bool:
        """Crea una nueva orden."""
        print("\n📋 Creando orden...")
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "X-Store-ID": self.store_id,
                "X-User-ID": self.user_id,
            }
            response = await self.client.post(
                "/orders/",
                json={"station_id": TEST_STATION_ID},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            self.order_id = data["id"]
            print(f"✅ Orden creada: {self.order_id}")
            print(f"   Total: ${data['total']}, Items: {data['item_count']}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    async def add_item(self, product_id: str, name: str, price: int) -> bool:
        """Agrega un item a la orden."""
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "X-Store-ID": self.store_id,
                "X-User-ID": self.user_id,
            }
            response = await self.client.post(
                f"/orders/{self.order_id}/items/",
                json={"product_id": product_id, "quantity": 1},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            print(f"   ✅ {name}: ${price} → Total: ${data['total']}, Items: {data['item_count']}")
            return True
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    async def run(self):
        """Ejecuta el flujo completo."""
        print("\n" + "=" * 70)
        print("🛒 E2E TEST: Agregando productos cada 2 segundos")
        print("=" * 70)

        print(f"\n🔐 Usuario: {self.user_id}")
        print(f"   Token: {self.token[:30]}...")

        # Crear orden
        if not await self.create_order():
            return

        # Agregar items
        print("\n📦 Agregando productos cada 2 segundos...")
        print("-" * 70)

        for i, (product_id, name, price) in enumerate(TEST_PRODUCTS, 1):
            print(f"\n[{i}/{len(TEST_PRODUCTS)}] Agregando: {name} (${price})")
            await self.add_item(product_id, name, price)

            # Esperar antes del siguiente
            if i < len(TEST_PRODUCTS):
                print("   ⏳ Esperando 2 segundos...")
                await asyncio.sleep(2)

        # Resumen
        print("\n" + "=" * 70)
        print("✅ TEST COMPLETADO")
        print("=" * 70)
        print(f"\n📊 Resumen:")
        print(f"   Orden: {self.order_id}")
        print(f"   Productos agregados: {len(TEST_PRODUCTS)}")
        print(f"   Total esperado: ${sum(p[2] for p in TEST_PRODUCTS)}")

        await self.client.aclose()


async def main():
    """Ejecuta el test."""
    simulator = SimpleOrderSimulator()
    try:
        await simulator.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por usuario")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
