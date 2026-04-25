# ARQUITECTURA DEL SISTEMA
## Sistema de Inventario Dinámico - Locales Comerciales Chile

**Para:** Equipo técnico (Allan, Jonathan) + PM  
**Versión:** 0.2-Sprint0  
**Stack:** Python + Vue + PostgreSQL + VPS (Hetzner)  
**Nota:** Arquitectura preparada para migración a GCP en futuro  

---

## 📐 DIAGRAMA C4 - NIVEL 1 (Contexto del Sistema)

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIOS EXTERNOS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [Operador Balanza]     [Cajero]     [Gerente]    [SII Chile]   │
│         │                   │              │            │        │
│         └───────────────────┼──────────────┼────────────┼───────┘
│                             │              │            │
│                    ┌────────▼──────────────▼────────────▼─────┐
│                    │                                           │
│                    │  SISTEMA DE INVENTARIO DINÁMICO          │
│                    │  (Backend + Frontend + Analytics)        │
│                    │                                           │
│                    └───────────────────────────────────────────┘
│                             │              │
│             ┌───────────────┼──────────────┘
│             │               │
│    ┌────────▼────┐   ┌──────▼──────────┐
│    │  Proveedor  │   │  Base de Datos  │
│    │  SII (DTE)  │   │  PostgreSQL     │
│    │             │   │  + Audit Log    │
│    └─────────────┘   └─────────────────┘

FLUJOS DE DATOS:
1. Operador escanea → API Backend (WebSocket)
2. Backend sincroniza ↔ Caja en tiempo real
3. Confirmación venta → SII para boleta electrónica
4. Toda la data → PostgreSQL con auditoría completa
5. Analítica → Metabase dashboard gerencial
```

---

## 🏗️ DIAGRAMA C4 - NIVEL 2 (Contenedores)

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vue 3)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  │  Pantalla Caja   │  │ Pantalla Operador│  │ Dashboard Gerente │
│  │  (Tablet/Monitor)│  │  (Balanza)       │  │ (Analytics)      │
│  │                  │  │                  │  │                  │
│  │ • Lectura QR     │  │ • Escaneo items  │  │ • Stock real-time│
│  │ • Confirmación   │  │ • 4 Estaciones   │  │ • Ventas/Hora    │
│  │ • Historial      │  │ • Pre-boleta QR  │  │ • Alertas        │
│  │ • Estado venta   │  │ • Pantalla nube  │  │ • Reportes       │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘
│           │                     │                    │           │
│           │                     │                    │           │
│           └─────────────────────┼────────────────────┘           │
│                                 │                                 │
│                        [TanStack Query + Pinia]                  │
│                        (Real-time state sync)                    │
│                                 │                                 │
└─────────────────────────────────┼─────────────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   WebSocket / HTTPS       │
                    │   (Conexión segura)       │
                    │                           │
                    └─────────────┬─────────────┘
                                  │
┌─────────────────────────────────┼─────────────────────────────────┐
│                    BACKEND (FastAPI - Python)                     │
├─────────────────────────────────┼─────────────────────────────────┤
│                                 │                                 │
│                         [API REST + WebSocket]                    │
│                                 │                                 │
│  ┌──────────────────────────────▼──────────────────────────────┐ │
│  │              ROUTERS & CONTROLLERS                          │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │  /products         → CRUD productos + stock                 │ │
│  │  /stations         → Gestión 4 estaciones                   │ │
│  │  /orders           → Pre-órdenes + QR generation            │ │
│  │  /transactions     → Ventas + confirmación                  │ │
│  │  /boletas          → Integración SII                        │ │
│  │  /inventory        → Movimientos de stock (auditoría)       │ │
│  │  /ws               → WebSocket real-time sync               │ │
│  │  /analytics        → Datos para dashboards                  │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                 │                                 │
│  ┌──────────────────────────────▼──────────────────────────────┐ │
│  │              SERVICIOS & LÓGICA DE NEGOCIO                  │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │  ProductService        → Gestión de catálogo                │ │
│  │  StationService        → Gestión de 4 estaciones            │ │
│  │  OrderService          → Creación de pre-órdenes            │ │
│  │  TransactionService    → Confirmación ventas                │ │
│  │  BolService            → Integración SII/DTE                │ │
│  │  InventoryService      → Sincronización stock               │ │
│  │  AuditService          → Log inmutable de operaciones       │ │
│  │  NotificationService   → Alertas (email, WhatsApp)          │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                 │                                 │
│  ┌──────────────────────────────▼──────────────────────────────┐ │
│  │              DATA ACCESS LAYER (SQLAlchemy)                 │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │  Modelos ORM:  Product, Station, Order, OrderItem,          │ │
│  │                Transaction, Boleta, InventoryMovement,      │ │
│  │                User, AuditLog                               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                 │                                 │
│  ┌──────────────────────────────▼──────────────────────────────┐ │
│  │              INTEGRACIONES EXTERNAS                         │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │  ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐   │ │
│  │  │  SII Provider   │  │   Redis      │  │   n8n        │   │ │
│  │  │  (Bsale/Acepta) │  │  (Pub/Sub)   │  │  (Workflows) │   │ │
│  │  │                 │  │              │  │              │   │ │
│  │  │ • Emisión DTE   │  │ • WebSocket  │  │ • Alertas    │   │ │
│  │  │ • Folio SII     │  │ • Caché      │  │ • Noti       │   │ │
│  │  │ • XML Boleta    │  │ • Sessions   │  │ • Webhooks   │   │ │
│  │  └─────────────────┘  └──────────────┘  └──────────────┘   │ │
│  │                                                              │ │
│  │  ┌──────────────────┐  ┌──────────────────────────────┐    │ │
│  │  │  Celery + Redis  │  │  Sentry (Error Tracking)     │    │ │
│  │  │  (Task Queue)    │  │                              │    │ │
│  │  │                  │  │  Monitoreo de errores en     │    │ │
│  │  │ • Boletas async  │  │  producción                 │    │ │
│  │  │ • Notificaciones │  │                              │    │ │
│  │  │ • Reportes       │  │                              │    │ │
│  │  └──────────────────┘  └──────────────────────────────┘    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                 │                                 │
└─────────────────────────────────┼─────────────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   PostgreSQL + Redis      │
                    │   (VPS Hetzner)           │
                    │                           │
                    └─────────────┬─────────────┘
                                  │
┌─────────────────────────────────┼─────────────────────────────────┐
│                      DATOS & PERSISTENCIA                         │
├─────────────────────────────────┼─────────────────────────────────┤
│                                 │                                 │
│  ┌───────────────────────────────▼───────────────────────────┐  │
│  │  PostgreSQL (VPS Hetzner - Docker)                        │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  • Tablas: products, stations, orders, transactions,      │  │
│  │           boletas, inventory_movements, audit_logs, users │  │
│  │  • Multi-tenant: Row-Level Security (RLS) por store_id    │  │
│  │  • Constraints: FK, NOT NULL, UNIQUE (barcode, UUID)      │  │
│  │  • Indices: para búsquedas rápidas (barcode, UUID)        │  │
│  │  • Migraciones: Alembic (versionadas)                     │  │
│  │  • Backups: Scripts cron a almacenamiento local           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Redis (VPS Hetzner - Docker)                             │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  • Pub/Sub: WebSocket broadcast (estaciones ↔ caja)       │  │
│  │  • Caché: Productos + precios (TTL 1 hora)                │  │
│  │  • Sessions: Autenticación JWT                            │  │
│  │  • Queues: Celery (tareas asíncronas)                     │  │
│  │  • Rate limiting: API endpoints                           │  │
│  │  • Almacenamiento local con persistencia (RDB/AOF)        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Almacenamiento Local (VPS Hetzner)                       │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  • XML DTE (boletas SII) - volumen local                  │  │
│  │  • Backups automáticos DB - scripts cron                 │  │
│  │  • Logs de auditoría exportados                           │  │
│  │  • Assets de la aplicación (Docker volumes)               │  │
│  │  • Cola offline: boletas pendientes de sincronizar (JSON) │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🔄 FLUJO DE DATOS COMPLETO (End-to-End)

### Scenario: Cliente compra 2kg de tomates + 1 pan

```
1. OPERADOR EN BALANZA (Estación 1)
   └─> Escanea código de barra [123456 - Tomate]
       └─> WebSocket: POST /api/v1/orders/add_item
           {
             "station_id": 1,
             "product_barcode": "123456",
             "quantity": 2.0,
             "unit": "kg"
           }

2. BACKEND RECIBE ITEM
   └─> Valida barcode en DB → obtiene precio
       {
         "product_id": 15,
         "name": "Tomate",
         "price": $2.50 USD/kg,
         "stock": 50 kg
       }
   └─> Calcula subtotal: 2 * $2.50 = $5.00 USD
   └─> Crea OrderItem en DB
   └─> Publica en Redis Pub/Sub: "station:1:update"

3. PANTALLA CLIENTE (Estación 1) - TIEMPO REAL
   └─> WebSocket recibe actualización
       ┌─────────────────────────────┐
       │   SU COMPRA - Estación 1    │
       ├─────────────────────────────┤
       │ Tomate × 2kg       $5.00    │
       │                             │
       │ Subtotal:          $5.00    │
       │ Total:             $5.00    │
       │                             │
       │ [Agregar más] [Finalizar]   │
       └─────────────────────────────┘

4. OPERADOR AGREGA OTRO ITEM
   └─> Escanea código de barra [789012 - Pan integral]
       └─> WebSocket: POST /api/v1/orders/add_item
           {
             "station_id": 1,
             "product_barcode": "789012",
             "quantity": 1.0,
             "unit": "unit"
           }

5. PANTALLA CLIENTE ACTUALIZA (WebSocket)
       ┌─────────────────────────────┐
       │   SU COMPRA - Estación 1    │
       ├─────────────────────────────┤
       │ Tomate × 2kg       $5.00    │
       │ Pan integral × 1   $3.50    │
       │                             │
       │ Subtotal:          $8.50    │
       │ Total:             $8.50    │
       │                             │
       │ [Agregar más] [Finalizar]   │
       └─────────────────────────────┘

6. CLIENTE DICE "LISTO" → GENERA QR
   └─> Backend crea pre-orden final
       {
         "order_id": "ORD-20260405-000142",
         "uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
         "station_id": 1,
         "total": $8.50,
         "items": [
           {"product": "Tomate", "qty": 2, "unit": "kg", "price": $5.00},
           {"product": "Pan integral", "qty": 1, "unit": "unit", "price": $3.50}
         ]
       }
   └─> Genera QR con UUID (contiene DETALLE COMPLETO, no solo total)
   └─> Imprime en pantalla

7. CLIENTE VA A CAJA CON QR

8. CAJERO EN CAJA ESCANEA QR
   └─> Escanea QR → extrae UUID
       └─> API: GET /api/v1/orders/{uuid}
           └─> Backend busca en DB: SELECT * FROM orders WHERE uuid=...
               └─> Retorna DETALLE COMPLETO:
                   {
                     "order_uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                     "items": [
                       {"product": "Tomate", "qty": 2, "unit": "kg", "price": $5.00},
                       {"product": "Pan integral", "qty": 1, "unit": "unit", "price": $3.50}
                     ],
                     "total": $8.50
                   }

9. PANTALLA CAJA MUESTRA DETALLE COMPLETO
       ┌─────────────────────────────────────┐
       │   TRANSACCIÓN - Cliente 142         │
       ├─────────────────────────────────────┤
       │ Tomate × 2kg               $5.00    │
       │ Pan integral × 1           $3.50    │
       │                                     │
       │ Subtotal:                  $8.50    │
       │ IVA (19%):                 $1.61    │
       │ TOTAL:                    $10.11    │
       │                                     │
       │ [Efectivo] [Tarjeta] [Transferencia]
       └─────────────────────────────────────┘

10. CAJERO CONFIRMA PAGO → $10.11 USD efectivo
    └─> API: POST /api/v1/transactions/complete
        {
          "order_uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
          "payment_method": "cash",
          "amount": 10.11
        }

11. BACKEND PROCESA VENTA
    └─> En DB (transacción ACID):
        • INSERT INTO transactions (order_id, amount, method, timestamp, user_id)
        • UPDATE products SET stock_quantity = stock_quantity - qty WHERE id = ...
          - Tomate: 50 kg - 2 kg = 48 kg
          - Pan: 120 units - 1 = 119 units
        • INSERT INTO inventory_movements (product_id, type, qty, reason, timestamp)
          - "SALE", -2, "QR-ORD-20260405-000142"
        • COMMIT (todo o nada)
    
    └─> Valida stock no sea negativo (fail-safe)
    
    └─> Celery task: "emitir_boleta.task" 
        {
          "transaction_id": 456,
          "items": [...],
          "total": 10.11,
          "customer": "Consumidor Final",
          "folio": "auto"  # SII asigna
        }

12. CELERY TASK: EMITIR BOLETA (Async, ~2-5 segundos)
    └─> Conecta con proveedor SII (Bsale/Acepta)
    └─> Envía datos completos
    └─> SII responde:
        {
          "folio": "00000142",
          "xml_dte": "<documento>...", 
          "timestamp_sii": "2026-04-05T15:45:23Z"
        }
    
    └─> Backend almacena en DB + GCS
        • UPDATE transactions SET boleta_folio = "00000142"
        • INSERT INTO boletas (transaction_id, folio_sii, xml_dte)
        • GCS: store XML en "boletas/00000142.xml"
    
    └─> Webhook SII: notifica si hay errores

13. PANTALLA CAJA MUESTRA CONFIRMACIÓN
    ┌───────────────────────────────────┐
    │   ✓ VENTA COMPLETADA              │
    ├───────────────────────────────────┤
    │ Folio SII: 00000142               │
    │ Hora: 15:45                       │
    │ Monto: $10.11                     │
    │                                   │
    │ Boleta: [Imprimir] [Email]        │
    │                                   │
    │ INVENTARIO ACTUALIZADO ✓          │
    │ Tomate: 48 kg                     │
    │ Pan: 119 units                    │
    │                                   │
    │ [Nueva Venta]                     │
    └───────────────────────────────────┘

14. AUDITORÍA REGISTRA TODO
    └─> INSERT INTO audit_logs:
        {
          "transaction_id": 456,
          "user_id": 3,  # Cajero "Juan"
          "action": "VENTA_CONFIRMADA",
          "details": {
            "order_uuid": "f47ac10b-...",
            "items": [...],
            "folio_sii": "00000142",
            "stock_before": {"tomate": 50, "pan": 120},
            "stock_after": {"tomate": 48, "pan": 119}
          },
          "timestamp": "2026-04-05T15:45:23Z"
        }

15. DASHBOARD GERENCIAL SE ACTUALIZA (Real-time)
    └─> Redis Pub/Sub: "analytics:update"
    └─> Metabase webhook recibe datos
    ┌───────────────────────────────────┐
    │   DASHBOARD GERENCIAL EN VIVO      │
    ├───────────────────────────────────┤
    │ Ventas hoy: $247.50 USD (↑8%)     │
    │ Transacciones: 24                 │
    │ Ticket promedio: $10.31           │
    │                                   │
    │ PRODUCTOS BAJOS DE STOCK:         │
    │ ⚠️ Lechuga: 2 unid (min: 10)      │
    │ ⚠️ Leche: 3L (min: 5L)            │
    │                                   │
    │ TOP 5 PRODUCTOS:                  │
    │ 1. Pan integral: 12 units         │
    │ 2. Tomate: 8 kg                   │
    │ 3. Lechuga: 5 bundles             │
    │ ...                               │
    └───────────────────────────────────┘

16. ALERTAS AUTOMÁTICAS (si hay bajo stock)
    └─> n8n detecta: Lechuga < min_stock
    └─> Envía notificación a gerente:
        📧 Email: "ALERTA: Lechuga bajo stock (2/10)"
        📱 WhatsApp: "⚠️ Comprar lechuga hoy"

```

**Duración total:** ~10 segundos (tiempo real)
**Puntos críticos:** 
- ✅ Pre-boleta contiene DETALLE, no solo total
- ✅ Inventario actualiza AUTOMÁTICAMENTE al confirmar venta
- ✅ SII recibe datos correctos y emite boleta
- ✅ Auditoría captura toda la operación
- ✅ Dashboard muestra cambios en vivo

---

## 🖥️ Especificaciones de Hardware

### Equipos en el Local

| Equipamiento | Modelo | Especificación | Integración |
|-------------|--------|-----------------|------------|
| **Balanza** | Digi SM-110 | Digital, capacidad 30kg, precisión 1g, USB | Scanner barcode auto-conectado |
| **Scanner** | Scan lux desktop 2D | 2D barcode reader, USB HID, lectura EAN-13 | WebSocket → Backend → Balanza pantalla |
| **Terminal Pago** | MercadoPago (SDK) | API REST, webhooks pagos, modo offline | Backend Celery task, reintentos async |
| **Pantalla Cliente** | Monitor/Tablet 10" | HDMI/USB, navegador web o app Vue | Servidor local o tablet con app PWA |
| **Pantalla Caja** | Monitor 15" | HDMI/USB, navegador web Firefox | Misma app Vue, responsive design |

### Conectividad

- **Red:** Ethernet LAN local (preferible) o WiFi 2.4/5GHz
- **Internet:** ADSL/Fibra (backup: LTE módem)
- **Tolerancia:** Si cae internet, sistema continúa en **MODO OFFLINE**

---

## 🔌 Modo Offline (Fallback Sin Conexión Internet)

### Escenario: Caída de Internet durante venta

```
1. Usuario escanea en balanza
2. Backend intenta conectar con SII → TIMEOUT (sin internet)
3. Sistema entra en MODO OFFLINE automáticamente

4. CAJERO CONTINÚA COBRANDO SIN BOLETA SII
   • Venta se procesa normalmente (caja local)
   • Inventario actualiza localmente
   • NO se emite boleta de SII en vivo
   
5. BOLETA SE GUARDA EN COLA OFFLINE (tabla: pending_boletas)
   {
     "order_id": "ORD-20260405-000142",
     "items": [...],
     "total": 10.11,
     "payment_method": "cash",
     "status": "pending_emission",
     "timestamp": "2026-04-05T15:45:23Z"
   }

6. CUANDO VUELVE INTERNET (dentro de 24 horas típicamente)
   • Cron job cada 5 minutos intenta emitir boletas pendientes
   • Sistema reconecta con SII provider
   • Boletas se emiten retroactivamente
   • Cliente recibe boleta por email o la imprime después
   • Auditoría registra: "boleta_emitted_offline_mode"
```

### Tablas para Offline

```sql
-- Cola de boletas pendientes de sincronizar
CREATE TABLE pending_boletas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(id),
    order_id UUID NOT NULL REFERENCES orders(id),
    transaction_id UUID NOT NULL REFERENCES transactions(id),
    folio_sii_provisional VARCHAR(10),  -- Local, será reemplazado por real
    status VARCHAR(50) DEFAULT 'pending'  -- pending, synced, failed
    retry_count INTEGER DEFAULT 0,
    last_retry_timestamp TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_at TIMESTAMP,
    
    INDEX (store_id, status),
    INDEX (created_at)
);

-- Detección de desconexión
CREATE TABLE connection_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(id),
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('offline', 'online')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB,
    
    INDEX (store_id, timestamp DESC)
);
```

### Garantías Offline

- ✅ **Inventario local:** Siempre se descuenta (incluso sin internet)
- ✅ **Auditoría inmutable:** Cada operación registrada localmente
- ✅ **Integridad financiera:** Transacciones guardadas, boletas emitidas cuando vuelva conexión
- ✅ **Transparencia:** Operador ve claramente "⚠️ MODO OFFLINE - Boleta pendiente"
- ✅ **Auto-reintentos:** Celery reintentas cada 5min por 24 horas

---

## 👥 Arquitectura Multi-Tenant con Row-Level Security (RLS)

### Concepto: Un Local ≠ Ve datos de Otro

Aunque toda la data está en PostgreSQL centralizada, cada local solo ve SUS datos.

```
PROBLEMA:
  Dueño Local A hizo login → ¿Puede ver ventas de Local B?
  ❌ NO. Nunca.

SOLUCIÓN: Row-Level Security (RLS) en PostgreSQL
  • Tabla `stores`: cada local tiene store_id único
  • Todas las tablas tienen columna `store_id`
  • PostgreSQL policy: "user can only SELECT rows where store_id = current_user's store_id"
```

### Implementación RLS

```sql
-- Contexto: obtener store_id del usuario logueado
CREATE OR REPLACE FUNCTION get_current_store_id()
RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_store_id')::UUID;
END;
$$ LANGUAGE plpgsql;

-- Policy en tabla PRODUCTS
CREATE POLICY products_isolation ON products
    USING (store_id = get_current_store_id());

ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Similar para: orders, transactions, inventory_movements, users, etc.
CREATE POLICY orders_isolation ON orders
    USING (store_id = get_current_store_id());

CREATE POLICY transactions_isolation ON transactions
    USING (store_id = get_current_store_id());

-- Backend FastAPI: al autenticar
def verify_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY)
    user_id = payload["sub"]
    store_id = payload["store_id"]
    
    # Pasar store_id a PostgreSQL
    connection.execute("SET app.current_store_id = %s", (store_id,))
    
    return {"user_id": user_id, "store_id": store_id}
```

### Garantías Multi-Tenant

- ✅ **Aislamiento de datos:** SQL-level, no application-level
- ✅ **Escalable:** Un local → 10 locales → 100 locales, misma DB
- ✅ **Seguro:** Si hacker accede a BD directamente, RLS lo detiene
- ✅ **Sin cambios de código:** RLS es transparente para la app
- ✅ **Auditabilidad:** Cada query registra store_id en audit_logs

---

## 🔐 Matriz de Autenticación & Autorización

```
┌──────────────────────────────────────────────────────────────────┐
│                     ROLES & PERMISOS                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ADMIN (Administrador Sistema)                                   │
│  └─> Permisos: TODOS                                             │
│      • Crear/editar/eliminar usuarios                            │
│      • Cambiar roles                                             │
│      • Acceso auditoria completa                                 │
│      • Config sistema                                            │
│      • Reset DB (⚠️ peligroso)                                   │
│                                                                   │
│  GERENTE (Dueño/Encargado local)                                 │
│  └─> Permisos: Lectura + Configuración                           │
│      • Ver dashboard analítico                                   │
│      • Reportes de ventas                                        │
│      • Alertas de inventario                                     │
│      • Crear/editar productos                                    │
│      • Crear/editar usuarios (no admin)                          │
│      • Exportar reportes                                         │
│      ✗ NO puede: eliminar transacciones, acceso auditoria       │
│                                                                   │
│  CAJERO (Operador Caja)                                          │
│  └─> Permisos: Lectura limitada + Venta                          │
│      • Ver pre-órdenes (solo por QR escaneo)                     │
│      • Confirmar ventas                                          │
│      • Ver historial de transacciones propias                    │
│      • Cambiar método pago                                       │
│      ✗ NO puede: ver dashboard, editar precios, inventario      │
│                                                                   │
│  OPERADOR (Balanza)                                              │
│  └─> Permisos: Lectura + Agregar items                           │
│      • Ver 4 estaciones asignadas                                │
│      • Escanear productos (agregar a orden)                      │
│      • Ver pre-boleta en tiempo real                             │
│      • Generar QR                                                │
│      ✗ NO puede: confirmar ventas, ver precios, editar          │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                   SEGURIDAD DE TRANSPORTE                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Authentication:                                                 │
│  • JWT tokens (email/pin + password)                             │
│  • Refresh tokens (7 días, rotable)                              │
│  • Sesión activa: ~8 horas                                       │
│                                                                   │
│  Transport:                                                      │
│  • HTTPS obligatorio (TLS 1.3)                                   │
│  • WebSocket seguro (WSS)                                        │
│  • CORS: solo localhost:3000 en desarrollo                       │
│                                                                   │
│  Secretos:                                                       │
│  • GCP Secret Manager (nunca en código)                          │
│  • Rotación automática: 30 días                                  │
│  • Audit log: quién accedió a secreto y cuándo                   │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📦 Tecnologías Seleccionadas & Por Qué

### Backend — FastAPI (Python)

| Aspecto | FastAPI | Por qué |
|---------|---------|---------|
| **Lenguaje** | Python 3.11+ | Stack del equipo, prototipado rápido |
| **Framework** | FastAPI | WebSockets nativos, async/await, Pydantic validation, OpenAPI auto |
| **ORM** | SQLAlchemy 2.0 | Flexible, versionable, migrations (Alembic) |
| **Validación** | Pydantic v2 | Type-safe, auto-documentación |
| **Auth** | JWT + jose | Stateless, escalable, refresh tokens |
| **Async Tasks** | Celery + Redis | Boletas async, notificaciones sin bloquear |
| **Testing** | pytest | Coverage, fixtures, mocking |

### Frontend — Vue 3

| Aspecto | Elección | Por qué |
|---------|----------|---------|
| **Framework** | Vue 3 | Stack del equipo, Composition API modern |
| **State** | Pinia | Simpler que Vuex, TypeScript friendly |
| **HTTP** | Axios + TanStack Query | Real-time sync, caching automático |
| **WebSocket** | Socket.io con fallback | Reconnection automática, broadcast |
| **Styling** | Tailwind + shadcn-vue | Rápido, componentes reutilizables |
| **Build** | Vite | Rápido en desarrollo, optimizado en prod |

### Base de Datos — PostgreSQL

| Aspecto | Elección | Por qué |
|---------|----------|---------|
| **Engine** | PostgreSQL 15 | ACID, constraints (PK/FK), índices avanzados |
| **Hosting** | Cloud SQL | Managed, backups automáticos, alta disponibilidad |
| **Migraciones** | Alembic | Versionable, reversible, documented |
| **Auditoría** | Tabla audit_logs + Triggers | Inmutable, quién-qué-cuándo |

### Infraestructura — VPS Hetzner (Con opción de migración a GCP futuro)

| Componente | Tecnología | Por qué |
|-----------|-----------|---------|
| **Hosting** | VPS Hetzner CX31 (2vCPU, 4GB RAM, 40GB SSD) | Costo bajo ($3.60 USD/mes), full control, escalable |
| **Orquestación** | Docker + Docker Compose | Reproducible, portable, fácil de migrar a GCP |
| **Base de datos** | PostgreSQL 15 (Docker) | ACID, RLS para multi-tenant, managed backups local |
| **Caché/Pub-Sub** | Redis (Docker) | WebSocket, Celery queue, persistencia local |
| **CI/CD** | GitHub Actions + Script deploy | Testing + deploy automático al VPS |
| **Logs** | ELK Stack (opcional) o archivo local | Centralización sin costo |
| **Secretos** | Archivo `.env` en servidor (producción: variables seguros) | Alternativa future: GCP Secret Manager |
| **Backups** | Cron scripts → almacenamiento local | Manual o B2 (cheap object storage) |

**Migración Futura a GCP:**
- Cloud Run reemplaza Docker
- Cloud SQL reemplaza PostgreSQL local
- Memorystore reemplaza Redis local
- Cloud Storage reemplaza almacenamiento local
- Secret Manager para credenciales
- Zero downtime: setup paralelo + DNS switch

### Herramientas de Apoyo

| Herramienta | Caso de Uso |
|-------------|------------|
| **n8n** | Alertas de stock bajo, webhooks SII, notificaciones WhatsApp |
| **Metabase** | Dashboards gerenciales sin código adicional |
| **Sentry** | Monitoreo de errores en producción |
| **GitHub Actions** | CI/CD: test, lint, build, deploy |

---

## ⚡ Decisiones de Arquitectura Clave

### 1. ¿Por qué WebSocket y no polling HTTP?
- **WebSocket:** Latencia ~100ms, bidireccional, escalable con Redis Pub/Sub
- **Polling HTTP:** Latencia ~1-2s, muchas requests, menos escalable
- **Decisión:** WebSocket para sincronización balanza ↔ caja en tiempo real

### 2. ¿Por qué Redis Pub/Sub y no solo WebSocket en memoria?
- **En memoria:** Pierde datos si backend reinicia
- **Redis:** Persistente, broadcast a múltiples clientes, Celery queue
- **Decisión:** Redis Pub/Sub para confiabilidad + escalabilidad

### 3. ¿Por qué Celery para boletas SII?
- **Síncrono:** Bloquea la confirmación de venta si SII es lento (~5s)
- **Asíncrono:** Confirma venta al instante, emite boleta en background
- **Decisión:** Celery para mejor UX (venta rápida) + confiabilidad (retry)

### 4. ¿Por qué Metabase y no construir dashboards propios?
- **Dashboard hecho a mano:** 3-4 semanas de desarrollo
- **Metabase:** Configuración en horas, SQL queries sin UI custom
- **Decisión:** Metabase open-source self-hosted (costo ~$0)

### 5. ¿Por qué VPS Hetzner ahora y GCP Cloud Run en futuro?
- **GCP Cloud Run:** Pay-per-use, scaling automático, pero requiere arquitectura específica ($75-130/mes esperado)
- **VPS Hetzner:** Costo fijo bajo ($3.60/mes), full control, Docker permite migración sin cambios de código
- **Decisión:** Hetzner VPS para MVP/piloto (máximo $30/mes infra), arquitectura preparada para migración a GCP cuando escale
- **Beneficio:** Si llegamos a 10 locales y el VPS se satura, migramos a GCP sin re-arquitecturar

---

## 🛡️ Trade-offs & Riesgos

| Decisión | Pro | Con | Mitigación |
|----------|-----|-----|------------|
| **WebSocket en VPS** | Real-time, bajo costo | Conexiones largas en servidor | Reconexión automática, fallback HTTP (polling) |
| **Redis local en Docker** | Pub/Sub escalable, costo cero | Pérdida si reinicia (mitigado: persistencia RDB/AOF) | Almacenamiento persistente activado |
| **Celery async boletas** | UX rápido, no bloquea venta | Complejidad (retry, dead letter queue) | Monitoring + Sentry, tests exhaustivos |
| **PostgreSQL única DB** | ACID, auditoría, RLS multi-tenant | Sin particionamiento (escalable hasta 10M registros) | Índices agresivos, caché Redis, particionamiento futuro |
| **SII proveedor externo** | No mantenemos DTE | Dependencia externa, caída SII = no boleta | **Cola offline:** boletas pendientes se guardan en DB, se reintentan cada 5min |
| **VPS single-instance** | Bajo costo, full control | Sin HA, downtime = downtime | Upgrade futuro a multi-zone o GCP Cloud Run |

---

## 📋 Checklist Pre-Sprint 0

- [x] Stack aprobado: Python + Vue + PostgreSQL + VPS Hetzner
- [x] Hardware especificado: Digi SM-110, Scan lux desktop 2D, MercadoPago
- [x] Infraestructura decidida: VPS Hetzner CX31 ($3.60/mes) + Docker
- [x] Modo offline documentado: Cola de boletas + reintentos automáticos
- [x] Multi-tenant con RLS: Row-level security para aislamiento store_id
- [ ] Repositorios GitHub creados (4: backend, frontend, infra, docs)
- [ ] Dockerfile + docker-compose.yml (PostgreSQL, Redis, Backend, Frontend)
- [ ] GitHub Actions workflow (test, lint, build, deploy a VPS)
- [ ] Base de datos schema Alembic inicial (migrations/versions/001_initial.py)
- [ ] VPS Hetzner provisioned + Docker instalado
- [ ] Proveedor SII confirmado + sandbox access (Bsale/Acepta)
- [ ] `.env.example` plantilla con secrets (DB_URL, REDIS_URL, SII_KEY, JWT_SECRET)

---

**Versión:** 0.2  
**Última actualización:** 20 de abril 2026  
**Cambios principales:** VPS Hetzner confirmado, Hardware specs, Modo Offline, Multi-tenant RLS documentado
