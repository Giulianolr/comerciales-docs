#!/usr/bin/env uv run
"""Script E2E: Simula cliente agregando items a una orden y escuchando eventos WebSocket.

Flujo:
1. Autenticar usuario
2. Crear una orden
3. Conectar a WebSocket para escuchar cart_update eventos
4. Agregar 5 productos cada 2 segundos
5. Mostrar eventos en tiempo real
"""

import asyncio
import json
import time
import uuid
from decimal import Decimal
from typing import Optional
from uuid import UUID

import httpx
import websockets
from app.core.security import create_access_token

# Configuración
API_BASE = "http://localhost:8000/api/v1"
WS_BASE = "ws://localhost:8000/api/v1"


# Datos de test (del seed.sql y seed_products.sql)
TEST_STORE_ID = "11111111-1111-1111-1111-111111111111"  # Sucursal Central
TEST_USER_ID = "33333333-3333-3333-3333-333333333333"  # Cajero Uno
TEST_USER_EMAIL = "cajero@omsai.cl"
TEST_USER_PIN = "1234"
TEST_STATION_ID = "77777777-7777-7777-7777-777777777777"  # Station (si existe)
TEST_PRODUCTS = [
    "66666666-6666-6666-6666-666666666661",  # Queso Mantecoso 1Kg ($8500)
    "66666666-6666-6666-6666-666666666662",  # Queso Gouda 1Kg ($12500)
    "66666666-6666-6666-6666-666666666663",  # Salame Milán 1Kg ($14000)
    "66666666-6666-6666-6666-666666666664",  # Jamón Pierna 1Kg ($9900)
    "66666666-6666-6666-6666-666666666665",  # Mortadela 1Kg ($6500)
]


class OrderSimulator:
    """Simula un cliente que agrega items a una orden y escucha eventos."""

    def __init__(self):
        self.client = httpx.AsyncClient(base_url=API_BASE, timeout=10.0, follow_redirects=True)
        self.user_id: Optional[str] = None
        self.token: Optional[str] = None
        self.order_id: Optional[str] = None
        self.store_id = TEST_STORE_ID
        self.station_id = TEST_STATION_ID
        self.ws_connection = None
        self.events_received = []

    async def setup_test_data(self) -> bool:
        """Crea datos de test necesarios (station, etc)."""
        print("\n⚙️  Configurando datos de test...")
        try:
            # Crear una station para la prueba
            headers = {
                "Authorization": f"Bearer {self.token}",
                "X-Store-ID": self.store_id,
                "X-User-ID": TEST_USER_ID,
            }
            response = await self.client.post(
                "/stations/",
                json={
                    "number": 1,
                    "status": "active",
                },
                headers=headers,
            )
            if response.status_code in [201, 200]:
                data = response.json()
                self.station_id = data.get("id", TEST_STATION_ID)
                print(f"✅ Station creada: {self.station_id}")
                return True
            else:
                print(f"ℹ️  Station podría existir, continuando...")
                self.station_id = TEST_STATION_ID
                return True
        except Exception as e:
            print(f"⚠️  No se pudo crear station, continuando: {e}")
            self.station_id = TEST_STATION_ID
            return True

    async def login(self) -> bool:
        """Genera un JWT token para el usuario de test."""
        print("\n🔐 Iniciando sesión...")
        try:
            self.user_id = TEST_USER_ID
            self.token = create_access_token(UUID(TEST_USER_ID))
            print(f"✅ Sesión iniciada: {TEST_USER_EMAIL}")
            print(f"   User ID: {self.user_id}")
            print(f"   Token: {self.token[:20]}...")
            return await self.setup_test_data()
        except Exception as e:
            print(f"❌ Error generando token: {e}")
            return False

    async def create_order(self) -> bool:
        """Crea una nueva orden."""
        print("\n📋 Creando orden...")
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "X-Store-ID": self.store_id,
                "X-User-ID": self.user_id,
            }
            # Usar el station_id que se creó en setup
            response = await self.client.post(
                "/orders/",
                json={"station_id": self.station_id},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            self.order_id = data["id"]
            print(f"✅ Orden creada: {self.order_id}")
            print(f"   Total: ${data['total']}, Items: {data['item_count']}")
            return True
        except Exception as e:
            try:
                error_detail = response.text
                print(f"❌ Error creando orden: {e}")
                print(f"   Detalle: {error_detail}")
            except:
                print(f"❌ Error creando orden: {e}")
            return False

    async def listen_to_websocket(self):
        """Escucha eventos WebSocket en background."""
        print("\n🔊 Conectando a WebSocket...")
        try:
            ws_url = f"{WS_BASE}/ws/store/{self.store_id}?token={self.token}"
            async with websockets.connect(ws_url) as ws:
                self.ws_connection = ws
                print("✅ Conectado a WebSocket")

                # Escuchar mensajes indefinidamente
                while True:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=10.0)
                        event = json.loads(message)
                        self.events_received.append(event)

                        # Mostrar evento
                        event_type = event.get("type", "unknown")
                        total = event.get("total", "0")
                        items_count = len(event.get("items", []))

                        print(f"\n🚀 Evento {event_type}:")
                        print(f"   Total: ${total}")
                        print(f"   Items: {items_count}")

                        if items_count > 0:
                            print("   Items en carrito:")
                            for item in event.get("items", []):
                                print(
                                    f"     - {item['name']}: "
                                    f"{item['quantity']} × ${item['unit_price']} "
                                    f"= ${item['subtotal']}"
                                )
                    except asyncio.TimeoutError:
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        print("❌ WebSocket conexión cerrada")
                        break
        except Exception as e:
            print(f"❌ Error en WebSocket: {e}")

    async def add_item(self, product_id: str, quantity: int = 1) -> bool:
        """Agrega un item a la orden."""
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "X-Store-ID": self.store_id,
                "X-User-ID": self.user_id,
            }
            response = await self.client.post(
                f"/orders/{self.order_id}/items",
                json={
                    "product_id": product_id,
                    "quantity": quantity,
                },
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            print(f"   ✓ Item agregado. Total: ${data['total']}, Items: {data['item_count']}")
            return True
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False

    async def run(self):
        """Ejecuta el flujo completo."""
        print("=" * 60)
        print("🛒 SIMULADOR E2E: Orden con actualizaciones en tiempo real")
        print("=" * 60)

        # Step 1: Login
        if not await self.login():
            return

        # Step 2: Create order
        if not await self.create_order():
            return

        # Step 3: Connect WebSocket (background task)
        ws_task = asyncio.create_task(self.listen_to_websocket())

        # Esperar un poco para que se conecte
        await asyncio.sleep(1)

        # Step 4: Add items cada 2 segundos
        print("\n📦 Agregando productos cada 2 segundos...")
        print("-" * 60)

        for i, product_id in enumerate(TEST_PRODUCTS, 1):
            print(f"\n[{i}/{len(TEST_PRODUCTS)}] Agregando producto {i}...")
            await self.add_item(product_id, quantity=1)

            # Esperar 2 segundos antes del próximo
            if i < len(TEST_PRODUCTS):
                print("   Esperando 2 segundos antes del siguiente...")
                await asyncio.sleep(2)

        # Esperar a que lleguen los últimos eventos
        print("\n⏳ Esperando eventos finales...")
        await asyncio.sleep(2)

        # Mostrar resumen
        print("\n" + "=" * 60)
        print("📊 RESUMEN")
        print("=" * 60)
        print(f"Eventos recibidos: {len(self.events_received)}")
        if self.events_received:
            last_event = self.events_received[-1]
            print(f"Total final: ${last_event.get('total', 'N/A')}")
            print(f"Items finales: {len(last_event.get('items', []))}")
            print("\nÚltimo estado del carrito:")
            for item in last_event.get("items", []):
                print(f"  - {item['name']}: {item['quantity']} × ${item['unit_price']}")

        # Cleanup
        ws_task.cancel()
        try:
            await ws_task
        except asyncio.CancelledError:
            pass

        await self.client.aclose()
        print("\n✅ Test completado")


async def main():
    """Ejecuta el simulador."""
    simulator = OrderSimulator()
    try:
        await simulator.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted por usuario")
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
