# BACKEND — ESTADO ACTUAL Y ENTREGA A FRONTEND
## Sistema de Inventario Dinámico — Locales Comerciales Chile

**Para:** Equipo Frontend (Jonathan) + PM (Giuliano)
**Preparado por:** Allan (Backend)
**Fecha:** 2026-04-12
**Sprint:** 0 completado / Sprint 1 en definición

---

## 1. STACK TECNOLÓGICO

| Capa | Tecnología | Versión |
|---|---|---|
| Framework API | FastAPI | >= 0.115 |
| Servidor ASGI | Uvicorn | >= 0.30 |
| ORM | SQLAlchemy | >= 2.0 |
| Migraciones | Alembic | >= 1.13 |
| Base de datos | PostgreSQL | 15 |
| Task queue | Celery + Redis | >= 5.4 / >= 5.0 |
| Scheduler | Celery Beat | incluido |
| Monitor tasks | Flower | >= 2.0 |
| Auth (librerías) | python-jose + passlib | instaladas, JWT pendiente |
| OCR / AI | Mistral OCR + Google Gemini | activo |
| OCR / AI alt. | OpenAI GPT-4o Vision | activo |
| Timezone | America/Santiago | configurado |
| Moneda | CLP (pesos chilenos, sin decimales) | en todos los modelos |

---

## 2. ARQUITECTURA DE SERVICIOS

```
┌─────────────────────────────────────────────────────────────┐
│                    comerciales-backend                       │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │  FastAPI     │   │  Celery      │   │  Celery Beat   │  │
│  │  :8000       │   │  Worker      │   │  Scheduler     │  │
│  │  (API REST)  │   │  (tareas bg) │   │  (cron jobs)   │  │
│  └──────┬───────┘   └──────┬───────┘   └───────┬────────┘  │
│         │                  │                    │           │
│         └──────────────────┴────────────────────┘           │
│                            │                                │
│              ┌─────────────┴──────────────┐                │
│              │                            │                │
│        ┌─────▼──────┐            ┌────────▼──────┐        │
│        │ PostgreSQL │            │    Redis       │        │
│        │ :5432      │            │    :6379       │        │
│        │ (datos)    │            │ (broker+cache) │        │
│        └────────────┘            └───────────────┘        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Flower :5555 (monitoreo visual de tareas Celery)   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. MODELOS DE DATOS (IMPLEMENTADOS — MIGRACIÓN APLICADA)

La migración inicial (`1c293d396139_initial.py`) crea **11 tablas** y **7 enums** en PostgreSQL.

### 3.1 Enums PostgreSQL

| Enum | Valores |
|---|---|
| `user_role` | `admin`, `supervisor`, `cajero`, `operador_balanza` |
| `station_type` | `balanza`, `caja` |
| `unidad_type` | `UN`, `KG`, `L`, `PAQ`, `BOL`, `TAB` |
| `preboleta_estado` | `pendiente`, `procesada`, `expirada`, `cancelada` |
| `metodo_pago` | `efectivo`, `debito`, `credito`, `transferencia` |
| `dte_estado` | `pendiente`, `enviado`, `aceptado`, `rechazado`, `retrying` |
| `tipo_dte` | `boleta`, `factura` |

---

### 3.2 Tabla `users`

```
users
├── id               UUID (PK)
├── nombre           VARCHAR(120)
├── email            VARCHAR(200) UNIQUE INDEX
├── rut              VARCHAR(12)  UNIQUE nullable
├── hashed_password  VARCHAR(255)
├── rol              ENUM user_role  [default: cajero]
├── activo           BOOLEAN        [default: true]
├── created_at       TIMESTAMP WITH TIMEZONE
└── updated_at       TIMESTAMP WITH TIMEZONE
```

**Roles y acceso:**
- `admin` — acceso total: ventas, inventario, compras, ERP, usuarios
- `supervisor` — igual a admin, recibe alertas de pre-boletas
- `cajero` — módulo de ventas en caja
- `operador_balanza` — ventas e inventario (solo lectura)

---

### 3.3 Tabla `stations`

```
stations
├── id           UUID (PK)
├── nombre       VARCHAR(80)
├── tipo         ENUM station_type  [balanza | caja]
├── ip_address   VARCHAR(45) nullable  ← IP de la balanza Digi SM-110
├── activo       BOOLEAN
├── created_at   TIMESTAMP WITH TIMEZONE
└── updated_at   TIMESTAMP WITH TIMEZONE
```

**Nota de hardware:** Las 4 balanzas Digi SM-110 se registran como stations de tipo `balanza`.
La caja se registra como station tipo `caja`. El campo `ip_address` permite ubicar cada SM-110 en la red local.

---

### 3.4 Tablas `categories` + `products`

```
categories
├── id           INTEGER (PK, autoincrement)
├── nombre       VARCHAR(100) UNIQUE
├── descripcion  TEXT nullable
├── created_at   TIMESTAMP WITH TIMEZONE
└── updated_at   TIMESTAMP WITH TIMEZONE

products
├── id              UUID (PK)
├── codigo_barras   VARCHAR(50) UNIQUE nullable  INDEX
├── codigo_interno  VARCHAR(50) UNIQUE nullable  INDEX
├── nombre          VARCHAR(200)  INDEX
├── descripcion     TEXT nullable
├── categoria_id    INTEGER FK → categories.id (SET NULL)
├── unidad          ENUM unidad_type  [default: UN]
├── precio_venta    INTEGER (CLP, sin decimales)
├── precio_costo    INTEGER (CLP, sin decimales)
├── stock_actual    NUMERIC(10,3)
├── stock_minimo    NUMERIC(10,3)
├── stock_maximo    NUMERIC(10,3) nullable
├── activo          BOOLEAN
├── created_at      TIMESTAMP WITH TIMEZONE
└── updated_at      TIMESTAMP WITH TIMEZONE
```

**Unidades de medida:**
- `UN` — unidad (pack, caja, bolsa): productos Caso&Cia, Ideal
- `KG` — kilo: cecinas, quesos, fiambres (productos Omeñaca, pesados en SM-110)
- `L`, `PAQ`, `BOL`, `TAB` — otras unidades

---

### 3.5 Tablas `preboletas` + `preboleta_items` + `preboleta_audits`

```
preboletas
├── id            UUID (PK)  ← este UUID es el QR
├── station_id    UUID FK → stations.id  INDEX
├── operator_id   UUID FK → users.id (SET NULL) nullable
├── estado        ENUM preboleta_estado  [default: pendiente]  INDEX
├── total_clp     INTEGER
├── qr_url        TEXT nullable  ← URL/datos del QR impreso
├── expires_at    TIMESTAMP WITH TIMEZONE nullable
├── created_at    TIMESTAMP WITH TIMEZONE
└── updated_at    TIMESTAMP WITH TIMEZONE

preboleta_items
├── id                INTEGER (PK, autoincrement)
├── preboleta_id      UUID FK → preboletas.id CASCADE DELETE  INDEX
├── product_id        UUID FK → products.id (SET NULL) nullable
├── nombre_producto   VARCHAR(200)  ← snapshot al momento de pesar
├── cantidad          NUMERIC
├── precio_unitario   INTEGER (CLP)
└── precio_total      INTEGER (CLP)

preboleta_audits  ← auditoría automática (migrado de WF03 n8n)
├── id             INTEGER (PK)
├── uuid           VARCHAR(36)  INDEX
├── station_id     VARCHAR(36)
├── total_clp      INTEGER
├── total_items    INTEGER
├── flagged        BOOLEAN
├── processed_by   VARCHAR(50)
└── created_at     TIMESTAMP WITH TIMEZONE
```

**Flujo pre-boleta:**
1. Balanza pesa productos → se crea `preboleta` con estado `pendiente`
2. Se genera QR con el UUID de la preboleta
3. Se imprime boucher físico (cliente) + se envía por red a caja
4. Caja escanea QR → recupera preboleta por UUID
5. Caja procesa pago → estado cambia a `procesada`
6. Si nadie la escanea antes de `expires_at` → estado `expirada`

---

### 3.6 Tablas `sales` + `sale_items`

```
sales
├── id             UUID (PK)
├── preboleta_id   UUID FK → preboletas.id (SET NULL) nullable  UNIQUE  INDEX
├── station_id     UUID FK → stations.id  INDEX
├── cajero_id      UUID FK → users.id (SET NULL) nullable
├── metodo_pago    ENUM metodo_pago  [default: efectivo]
├── total_clp      INTEGER (CLP)
├── created_at     TIMESTAMP WITH TIMEZONE
└── updated_at     TIMESTAMP WITH TIMEZONE

sale_items
├── id               INTEGER (PK, autoincrement)
├── sale_id          UUID FK → sales.id CASCADE DELETE  INDEX
├── product_id       UUID FK → products.id (SET NULL) nullable
├── nombre_producto  VARCHAR(200)  ← snapshot al momento de venta
├── cantidad         NUMERIC
├── precio_unitario  INTEGER (CLP)
└── precio_total     INTEGER (CLP)
```

---

### 3.7 Tabla `dte_transactions`

```
dte_transactions
├── id            UUID (PK)
├── sale_id       UUID FK → sales.id CASCADE  UNIQUE  INDEX
├── folio         INTEGER nullable  INDEX  ← número SII
├── tipo_dte      ENUM tipo_dte  [default: boleta]
├── total_clp     INTEGER
├── estado        ENUM dte_estado  [default: pendiente]  INDEX
├── error_msg     TEXT nullable
├── retry_count   INTEGER  [default: 0]
├── sent_at       TIMESTAMP WITH TIMEZONE nullable
├── confirmed_at  TIMESTAMP WITH TIMEZONE nullable
├── created_at    TIMESTAMP WITH TIMEZONE
└── updated_at    TIMESTAMP WITH TIMEZONE
```

**Estados DTE:**
- `pendiente` → recién creado, cola de envío
- `enviado` → transmitido al SII/Bsale
- `aceptado` → confirmado por SII
- `rechazado` → SII rechazó, requiere corrección manual
- `retrying` → en reintento automático (task Celery cada 15 min)

---

### 3.8 Tabla `daily_reports`

```
daily_reports
├── date              DATE (PK)  ← una fila por día
├── total_ventas_clp  INTEGER
├── total_transacciones INTEGER
├── ticket_promedio   NUMERIC(10,2)
├── hora_pico         VARCHAR(5) nullable
├── productos_bajos   INTEGER
├── dte_pendientes    INTEGER
├── created_at        TIMESTAMP WITH TIMEZONE
└── updated_at        TIMESTAMP WITH TIMEZONE
```

---

## 4. ENDPOINTS ACTIVOS

### 4.1 Infraestructura
```
GET  /health
```
Retorna `{"status": "ok"}`. Usado por Docker healthcheck y load balancer.

---

### 4.2 Pre-boletas (auditoría — migrado de WF03 n8n)
```
POST /api/v1/preboleta/created
```
**Body:**
```json
{
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "station_id": "string",
  "total_clp": 15000,
  "items_count": 3
}
```
**Función:** registra auditoría en `preboleta_audits` y envía alerta por email al supervisor si el monto supera `ALERTA_VENTA_ALTA_CLP` (default: $50.000 CLP).

---

### 4.3 Importación de facturas con AI
```
POST /api/v1/inventory/import-invoice?provider=mistral
POST /api/v1/inventory/import-invoice?provider=openai
```
**Body:** `multipart/form-data` — campo `factura` (PDF, JPG, PNG, WebP, máx. 10 MB)

**Respuesta:**
```json
{
  "factura": {
    "numero": "5791166",
    "proveedor": "CASO & CIA.",
    "rut_proveedor": "92.423.000-2",
    "fecha": "2026-04-06",
    "total_neto": 80296
  },
  "items": [
    {
      "codigo_proveedor": "250502",
      "nombre": "OBSESION CLASICA 24X85 GR.",
      "cantidad": 8,
      "unidad": "UN",
      "precio_unitario": 822,
      "precio_neto": 6560
    }
  ],
  "provider_used": "mistral"
}
```

**Proveedores AI disponibles:**
- `mistral` (default) — Mistral OCR → extrae texto → Google Gemini estructura JSON
- `openai` — GPT-4o Vision — OCR + extracción en un paso

**Formatos de factura soportados y probados:**
| Proveedor | Tipo productos | Códigos | Descuentos | Pago |
|---|---|---|---|---|
| Caso & Cia. | Unidades (UN/PAQ/BOL) | 6 dígitos col. separada | Sí (%DBA + global) | Contado |
| Omeñaca S.A. | Kilos (KG) | 3-4 dígitos col. separada | No | 7 días |
| Ideal S.A. | Unidades | Embebido en descripción | No | Contado |

---

## 5. TAREAS CELERY AUTOMATIZADAS

### 5.1 Programación (Celery Beat — timezone: America/Santiago)

| Task | Archivo | Frecuencia | Función |
|---|---|---|---|
| `check_low_stock` | `app/tasks/stock.py` | Cada 30 min | Detecta productos con stock ≤ stock_mínimo × 1.5 → email gerencia |
| `daily_sales_report` | `app/tasks/reports.py` | 23:00 diario | Genera KPIs del día → email gerencia + guarda `DailyReport` |
| `monitor_dte` | `app/tasks/sii.py` | Cada 15 min | Detecta DTEs fallidos/viejos → email admin + reintento automático |

### 5.2 Alertas por email

| Evento | Destinatario | Cuándo |
|---|---|---|
| Stock bajo | `EMAIL_GERENCIA` | Stock actual ≤ stock_mínimo × 1.5 |
| Venta alta | `EMAIL_SUPERVISOR` | Monto preboleta > `ALERTA_VENTA_ALTA_CLP` |
| DTE fallido | `EMAIL_ADMIN` | DTE con estado `rechazado` o `retrying` |
| Reporte diario | `EMAIL_GERENCIA` | 23:00 todos los días |

---

## 6. VARIABLES DE ENTORNO

Archivo: `comerciales-backend/.env` (no se sube a git)
Plantilla: `comerciales-backend/.env.example`

| Variable | Tipo | Requerida | Descripción |
|---|---|---|---|
| `DATABASE_URL` | string | **Sí** | `postgresql://user:pass@host:5432/comerciales` |
| `REDIS_URL` | string | **Sí** | `redis://localhost:6379/0` |
| `API_KEY` | string | **Sí** | Clave interna para endpoints protegidos |
| `SMTP_HOST` | string | No | Default: `smtp.gmail.com` |
| `SMTP_PORT` | integer | No | Default: `587` |
| `SMTP_USER` | string | No | Cuenta remitente |
| `SMTP_PASSWORD` | string | No | Contraseña de aplicación Gmail |
| `SMTP_FROM` | string | No | Default: `noreply@comerciales.cl` |
| `EMAIL_GERENCIA` | string | No | Destinatario alertas gerencia |
| `EMAIL_ADMIN` | string | No | Destinatario alertas sistema |
| `EMAIL_SUPERVISOR` | string | No | Destinatario alertas operacionales |
| `ALERTA_VENTA_ALTA_CLP` | integer | No | Default: `50000` |
| `MISTRAL_API_KEY` | string | * | Requerida si `provider=mistral` |
| `GOOGLE_API_KEY` | string | * | Requerida si `provider=mistral` |
| `OPENAI_API_KEY` | string | * | Requerida si `provider=openai` |

---

## 7. CÓMO LEVANTAR EL BACKEND (DEV LOCAL)

### Prerrequisito: Docker Desktop instalado

```bash
# 1. Levantar infraestructura (PostgreSQL + Redis + Adminer)
cd comerciales-infra
docker compose up -d
# PostgreSQL → localhost:5432  (user: comerciales / pass: comerciales2026)
# Redis      → localhost:6379
# Adminer    → http://localhost:8080

# 2. Aplicar migración de base de datos
cd ../comerciales-backend
alembic upgrade head

# 3. Levantar servicios (3 terminales separadas)
start_api.bat       # FastAPI   → http://localhost:8000
start_worker.bat    # Celery worker (pool=solo para Windows)
start_beat.bat      # Celery scheduler (cron jobs)

# 4. Opcional — monitor de tareas
start_flower.bat    # Flower    → http://localhost:5555

# 5. Documentación interactiva
# http://localhost:8000/docs   (Swagger UI)
# http://localhost:8000/redoc  (ReDoc)
```

---

## 8. FLUJO COMPLETO DEL NEGOCIO

```
[Balanza Digi SM-110]                [Backend]              [Caja — misma PC]
        |                                |                          |
  Operador pesa                         |                          |
  productos                             |                          |
        |                               |                          |
  Selecciona producto              POST /preboleta                 |
  Ingresa cantidad/peso    ──────────────────────────────►  PreBoleta creada
        |                               |                   (estado: pendiente)
  Imprime boucher físico               |                          |
  (cliente lo lleva a caja)            |                          |
        |                               |                          |
  Envía por red              WebSocket/polling ──────────► Caja recibe alerta
  (push automático)                    |                   de preboleta nueva
                                       |                          |
                              GET /preboleta/{uuid}               |
                              (cajero escanea QR)   ◄────── Cajero escanea QR
                                       |                          |
                              Retorna items + total               |
                                       |                          |
                                       |              Cajero puede modificar items
                                       |                          |
                              POST /sales                         |
                              {uuid, metodo_pago}  ◄────── Confirma pago
                                       |
                              - PreBoleta → procesada
                              - Stock descontado
                              - Sale + SaleItems creados
                              - DTETransaction creado (pendiente)
                                       |
                              [Celery task cada 15min]
                              - Envía DTE a SII/Bsale
                              - Actualiza estado: enviado/aceptado
```

---

## 9. GAPS IDENTIFICADOS — PENDIENTES PARA SPRINT 1

### 9.1 Endpoints faltantes (bloqueantes para el frontend)

| Endpoint | Método | Módulo | Prioridad |
|---|---|---|---|
| `/api/v1/auth/login` | POST | Auth | CRÍTICA |
| `/api/v1/auth/me` | GET | Auth | CRÍTICA |
| `/api/v1/products` | GET, POST | Inventario | CRÍTICA |
| `/api/v1/products/{id}` | GET, PUT, DELETE | Inventario | CRÍTICA |
| `/api/v1/preboleta` | POST | Balanza→Caja | CRÍTICA |
| `/api/v1/preboleta/{uuid}` | GET | Caja | CRÍTICA |
| `/api/v1/sales` | POST | Caja | CRÍTICA |
| `/api/v1/sales` | GET | Reportes | Alta |
| `/api/v1/categories` | GET, POST, PUT, DELETE | Inventario | Alta |
| `/api/v1/stations` | GET, POST, PUT | Admin | Media |
| `/api/v1/users` | GET, POST, PUT, DELETE | Admin | Media |
| `/api/v1/reports/daily` | GET | ERP | Media |
| `/api/v1/dte` | GET | ERP/SII | Baja |

### 9.2 Autenticación JWT (no implementada)

Las librerías están instaladas (`python-jose`, `passlib`) pero no hay endpoints de login ni middleware de autenticación. El frontend NO puede integrarse sin esto.

**Lo que falta:**
- `POST /api/v1/auth/login` → recibe `{email, password}` → retorna JWT
- `GET /api/v1/auth/me` → retorna datos del usuario autenticado
- Dependency `get_current_user` en FastAPI para proteger todos los endpoints
- Middleware que valide el token en cada request

### 9.3 WebSocket / Real-time (no implementado)

Para que la caja reciba pre-boletas en tiempo real sin que el cajero busque manualmente, se necesita:
- `WS /ws/station/{station_id}` — conexión persistente de la caja
- Al crear una pre-boleta, hacer `broadcast` al WebSocket de la caja correspondiente

Alternativa más simple: polling desde el frontend cada 5 segundos a `GET /preboleta?estado=pendiente&station_id=...`

### 9.4 Modelos faltantes para módulo de Compras

Identificados al analizar las facturas de proveedores reales. **No existen en la migración actual.**

```
Supplier (Proveedor)
├── id             UUID (PK)
├── nombre         VARCHAR(200)
├── rut            VARCHAR(12) UNIQUE
├── email          VARCHAR(200) nullable
├── telefono       VARCHAR(20) nullable
├── condicion_pago INTEGER  ← días de plazo (0 = contado)
├── activo         BOOLEAN
└── timestamps

SupplierProduct (Mapeo código proveedor → producto interno)
├── id                   INTEGER (PK)
├── supplier_id          UUID FK → suppliers
├── product_id           UUID FK → products
├── codigo_proveedor     VARCHAR(50)  ← ej: "250502" (Caso&Cia), "16" (Omeñaca)
├── descripcion_proveedor VARCHAR(200) nullable
├── precio_costo_ultimo  INTEGER (CLP)
└── fecha_ultimo_precio  DATE

PurchaseOrder (Factura de compra)
├── id                UUID (PK)
├── supplier_id       UUID FK → suppliers
├── numero_factura    VARCHAR(50)
├── fecha_emision     DATE
├── fecha_vencimiento DATE nullable  ← para cuentas por pagar
├── condicion_pago    INTEGER  ← días
├── subtotal_neto     INTEGER (CLP)
├── descuento_total   INTEGER (CLP)
├── iva               INTEGER (CLP)
├── total             INTEGER (CLP)
├── estado            ENUM [pendiente_pago | pagada | vencida]
├── provider_ai       VARCHAR(20) nullable  ← "mistral" | "openai"
└── timestamps

PurchaseOrderItem (Línea de la factura)
├── id                   INTEGER (PK)
├── purchase_order_id    UUID FK → purchase_orders CASCADE
├── product_id           UUID FK → products (SET NULL) nullable
├── codigo_proveedor     VARCHAR(50) nullable
├── descripcion_raw      VARCHAR(200)  ← texto exacto de la factura
├── unidad               ENUM unidad_type
├── cantidad             NUMERIC(10,3)
├── precio_unitario      INTEGER (CLP)
├── descuento_pct        NUMERIC(5,2)  [default: 0]
└── precio_neto          INTEGER (CLP)
```

**Por qué es necesario:**
- El endpoint `/import-invoice` ya extrae los datos pero no los persiste — retorna JSON y nada más
- Sin `Supplier` y `PurchaseOrder`, el módulo de Compras en el frontend no puede guardar nada
- Sin `SupplierProduct`, los códigos de proveedor (ej: `250502` de Caso&Cia) no se pueden mapear a productos del inventario
- Sin `fecha_vencimiento`, no hay módulo de cuentas por pagar

---

## 10. RESUMEN DE ESTADO

| Componente | Estado |
|---|---|
| Modelos de datos (11 tablas) | COMPLETO |
| Migración Alembic inicial | COMPLETO |
| Tareas Celery (stock, reporte, DTE) | COMPLETO |
| Alertas por email | COMPLETO |
| Importación facturas con AI | COMPLETO |
| Auditoría pre-boletas | COMPLETO |
| Autenticación JWT | PENDIENTE |
| Endpoints CRUD productos | PENDIENTE |
| Endpoint crear pre-boleta | PENDIENTE |
| Endpoint procesar venta (POST /sales) | PENDIENTE |
| WebSocket / real-time pre-boletas | PENDIENTE |
| Modelos Supplier / PurchaseOrder | PENDIENTE |
| Integración Bsale (DTE real) | PENDIENTE |
| Frontend Vue 3 | PENDIENTE |

---

**Repositorio:** `comerciales-backend`
**Docs API (cuando el backend está corriendo):** http://localhost:8000/docs
