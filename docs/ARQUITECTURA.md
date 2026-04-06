# ARQUITECTURA DEL SISTEMA
## Sistema de Inventario Dinámico - Locales Comerciales Chile

**Para:** Equipo técnico (Allan, Jonathan) + PM  
**Versión:** 0.1-MVP  
**Stack:** Python + Vue + PostgreSQL + GCP  

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
                    │   (Cloud SQL + Memorystore)
                    │                           │
                    └─────────────┬─────────────┘
                                  │
┌─────────────────────────────────┼─────────────────────────────────┐
│                      DATOS & PERSISTENCIA                         │
├─────────────────────────────────┼─────────────────────────────────┤
│                                 │                                 │
│  ┌───────────────────────────────▼───────────────────────────┐  │
│  │  PostgreSQL (Cloud SQL)                                   │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  • Tablas: products, stations, orders, transactions,      │  │
│  │           boletas, inventory_movements, audit_logs, users │  │
│  │  • Constraints: FK, NOT NULL, UNIQUE (barcode, UUID)      │  │
│  │  • Indices: para búsquedas rápidas (barcode, UUID)        │  │
│  │  • Migraciones: Alembic (versionadas)                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Redis (Memorystore)                                      │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  • Pub/Sub: WebSocket broadcast (estaciones ↔ caja)       │  │
│  │  • Caché: Productos + precios (TTL 1 hora)                │  │
│  │  • Sessions: Autenticación JWT                            │  │
│  │  • Queues: Celery (tareas asíncronas)                     │  │
│  │  • Rate limiting: API endpoints                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Cloud Storage (GCS)                                      │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  • XML DTE (boletas SII)                                  │  │
│  │  • Backups automáticos DB                                 │  │
│  │  • Logs de auditoría exportados                           │  │
│  │  • Assets de la aplicación                                │  │
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

### Infraestructura — GCP

| Servicio | Razón |
|----------|-------|
| **Cloud Run** | Serverless, escala automática, pay-per-use |
| **Cloud SQL** | PostgreSQL managed, backups automáticos |
| **Memorystore (Redis)** | Pub/Sub, caché, sesiones |
| **Cloud Storage** | XMLs SII, backups, assets |
| **Secret Manager** | Credenciales seguras |
| **Cloud Build** | CI/CD, container registry |
| **Cloud Logging** | Logs centralizados |

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

### 5. ¿Por qué GCP Cloud Run y no EC2/Kubernetes?
- **EC2/K8s:** Costo fijo, requiere ops, scaling manual
- **Cloud Run:** Pay-per-use, scaling automático, no ops
- **Decisión:** Cloud Run para startup/piloto (costo $75-130/mes vs $300+/mes)

---

## 🛡️ Trade-offs & Riesgos

| Decisión | Pro | Con | Mitigación |
|----------|-----|-----|------------|
| **WebSocket en Cloud Run** | Real-time | Conexiones largas = costo | Reconexión automática, fallback HTTP |
| **Redis en Memorystore** | Pub/Sub escalable | Costo extra ($25-40/mes) | Necesario para WebSocket |
| **Celery async boletas** | UX rápido | Complejidad (retry, DLQ) | Monitoring + Sentry |
| **PostgreSQL única DB** | ACID, auditoría | Sin particionamiento | Índices, caché Redis |
| **SII proveedor externo** | No mantenemos DTE | Dependencia externa | Fallback a modo offline |

---

## 📋 Checklist Pre-Sprint 0

- [ ] Stack aprobado por equipo técnico
- [ ] GCP proyecto creado + billing configurado
- [ ] Repositorios GitHub creados
- [ ] Secret Manager en GCP para keys
- [ ] Dockerfile + docker-compose.yml plantillas
- [ ] GitHub Actions workflow templates
- [ ] Especificaciones hardware obtenidas (martes)
- [ ] Proveedor SII confirmado + sandbox access
- [ ] Base de datos schema definida

---

**Versión:** 0.1  
**Últimas actualización:** 5 de abril 2026
