# 🧪 E2E Test: Simulador de Cliente en Tiempo Real

Script que simula un cliente (cajero) autenticándose, creando una orden y agregando productos cada 2 segundos, mientras escucha los eventos `cart_update` en tiempo real vía WebSocket.

## 📋 Flujo

1. **Autenticar** → Login con PIN
2. **Crear orden** → Nueva pre-orden vacía
3. **Conectar WebSocket** → Escuchar eventos `cart_update` en background
4. **Agregar items** → 5 productos, cada uno cada 2 segundos
5. **Ver actualizaciones** → Los eventos llegan en tiempo real

## 🚀 Antes de ejecutar

### 1. Iniciar el servidor backend

```bash
cd comerciales-backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Seed database (si es primera vez)

```bash
cd comerciales-backend
uv run python seed.py
```

Esto crea:
- ✅ Store 1 (ID: `550e8400-e29b-41d4-a716-446655440001`)
- ✅ User cajero1 (Email: `cashier1@store1.com`, PIN: `1234`)
- ✅ Station 1 (para la caja registradora)
- ✅ 5 productos (Manzana, Plátano, Naranja, Fresa, Uva)

## ▶️ Ejecutar el test

```bash
cd comerciales-backend
chmod +x test_e2e.py
./test_e2e.py
```

O directamente:

```bash
cd comerciales-backend
uv run python test_e2e.py
```

## 📊 Salida esperada

```
============================================================
🛒 SIMULADOR E2E: Orden con actualizaciones en tiempo real
============================================================

🔐 Iniciando sesión...
✅ Sesión iniciada: cashier1@store1.com
   Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

📋 Creando orden...
✅ Orden creada: 550e8400-e29b-41d4-a716-446655440999
   Total: $0.00, Items: 0

🔊 Conectando a WebSocket...
✅ Conectado a WebSocket

📦 Agregando productos cada 2 segundos...
------------------------------------------------------------

[1/5] Agregando producto 1...
   ✓ Item agregado. Total: $2.50, Items: 1

🚀 Evento cart_update:
   Total: $2.50
   Items: 1
   Items en carrito:
     - Manzana: 1 × $2.50 = $2.50

   Esperando 2 segundos antes del siguiente...

[2/5] Agregando producto 2...
   ✓ Item agregado. Total: $5.00, Items: 2

🚀 Evento cart_update:
   Total: $5.00
   Items: 2
   Items en carrito:
     - Manzana: 1 × $2.50 = $2.50
     - Plátano: 1 × $2.50 = $2.50

... (continúa por los 5 productos)

============================================================
📊 RESUMEN
============================================================
Eventos recibidos: 5
Total final: $12.50
Items finales: 5

Último estado del carrito:
  - Manzana: 1 × $2.50
  - Plátano: 1 × $2.50
  - Naranja: 1 × $2.50
  - Fresa: 1 × $2.50
  - Uva: 1 × $2.50

✅ Test completado
```

## 🔧 Customizar el test

Edita `test_e2e.py` para cambiar:

```python
# Usuarios
TEST_USER_EMAIL = "cashier1@store1.com"
TEST_USER_PIN = "1234"

# Store/Station
TEST_STORE_ID = "550e8400-e29b-41d4-a716-446655440001"
TEST_STATION_ID = "550e8400-e29b-41d4-a716-446655440011"

# Productos a agregar
TEST_PRODUCTS = [...]

# Espera entre items
await asyncio.sleep(2)  # ← Cambiar aquí
```

## 🐛 Troubleshooting

### `Connection refused` (no se conecta al servidor)
```bash
# Verificar que el servidor esté corriendo
curl http://localhost:8000/docs
```

### `Unauthorized` (login falla)
```bash
# Verificar que el seed corrió y creó el usuario
sqlite3 app.db "SELECT * FROM users LIMIT 1;"
```

### `WebSocket timeout` (no recibe eventos)
- Verificar que Redis esté corriendo: `redis-cli ping`
- Verificar logs del servidor en la terminal del backend

## 📈 Qué observar

1. **Cada evento llega instantáneamente** después de agregar un item
2. **El array `items` crece** con cada adición
3. **El `total` se actualiza** correctamente
4. **Nombres de productos** aparecen en el evento

Esto demuestra que:
- ✅ OrderService emite `cart_update` correctamente
- ✅ Redis Pub/Sub funciona
- ✅ WebSocket difunde a clientes
- ✅ Frontend puede actualizar la UI en tiempo real

---

**¡Listo para ver la magia en tiempo real! 🚀**
