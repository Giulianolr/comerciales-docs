# Contexto del Proyecto — Sistema Comerciales

> Documento de knowledge base para Claude.ai Projects.
> Última actualización: 2026-04-24

---

## Descripción General

Sistema de gestión integral para **locales comerciales en Chile** (supermercados, negocios multicategoría).
Moderniza el flujo actual **Balanza → Pre-boleta → Caja** en un ecosistema conectado en tiempo real,
con inventario automático y boletas electrónicas SII.

**Estado:** En desarrollo — Sprint 0 completado (infraestructura Docker lista)
**Timeline:** 8–12 semanas
**Mercado objetivo:** Locales comerciales Chile, cumplimiento tributario SII

---

## Equipo

| Rol | Nombre | Responsabilidades |
|-----|--------|-------------------|
| PM / Arquitecto | Giuliano | Visión, requerimientos, roadmap, stakeholders |
| Dev Full-Stack | Allan | Backend (FastAPI), infraestructura, DevOps |
| Dev Full-Stack | Jonathan | Frontend (Vue 3), UI/UX, integraciones hardware |

---

## Problema que Resuelve

- Balanza desconectada de caja (pre-boleta solo muestra total, no detalle)
- Inventario no se actualiza automáticamente al vender
- Mucho trabajo manual después de cada venta
- Sin visibilidad de stock en tiempo real
- Difícil auditoría y trazabilidad de movimientos

## Solución

- Sincronización en tiempo real (WebSocket) entre balanza ↔ caja
- Pre-boleta con detalle completo + QR único
- Inventario descuenta automáticamente al confirmar venta
- Integración directa con SII (boleta electrónica DTE)
- Auditoría completa e inmutable
- Dashboard gerencial en tiempo real
- Alertas automáticas de stock bajo

---

## Stack Tecnológico

### Backend
- **Framework:** FastAPI (Python)
- **Base de datos:** PostgreSQL 16
- **Cache / Cola:** Redis 7
- **Workers asíncronos:** Celery (worker + beat scheduler)
- **Monitoreo Celery:** Flower
- **ORM:** SQLAlchemy (mapped_column style)
- **Validación:** Pydantic v2 + pydantic-settings
- **Migraciones:** Alembic

### Frontend
- **Framework:** Vue 3 + TypeScript
- **Build:** Vite
- **Estilos:** Tailwind CSS
- **State management:** Pinia
- **Router:** Vue Router

### Infraestructura
- **Contenedores:** Docker Compose (dev y prod)
- **Reverse proxy / TLS:** Caddy 2 (TLS automático vía Cloudflare)
- **VPS:** Hetzner CX31 (2 vCPU, 4 GB RAM, 40 GB SSD)
- **DNS / CDN:** Cloudflare
- **Automatización:** n8n (workflows)
- **Backups:** Backblaze B2 (10 GB free tier)

### Integraciones externas
- **SII Chile:** Emisión DTE (boleta electrónica) vía Bsale (~$28 USD/mes)
- **SMTP:** Gmail para alertas automáticas
- **AI / OCR:** Mistral (OCR), Google Gemini, OpenAI Vision — usados en workflows n8n

---

## Estructura de Repositorios

```
comerciales-infra/       → Docker Compose dev + prod, Caddyfile, n8n
comerciales-backend/     → FastAPI + modelos DB + tareas Celery
comerciales-frontend/    → Vue 3 SPA
comerciales-docs/        → Documentación técnica y ejecutiva
```

---

## Arquitectura de Producción (Hetzner VPS)

```
Internet
   │
   ▼
Caddy (80/443) — TLS automático
   │
   ├── api.dominio.cl       → FastAPI (puerto 8000, 2 workers uvicorn)
   └── flower.dominio.cl    → Flower (puerto 5555, basicauth)

Servicios internos (red Docker privada):
   ├── comerciales-api
   ├── comerciales-worker   (Celery worker, concurrency=2)
   ├── comerciales-beat     (Celery beat scheduler)
   ├── comerciales-postgres (PostgreSQL 16)
   └── comerciales-redis    (Redis 7, maxmemory 256mb)
```

---

## Dominio del Negocio — Modelos de Datos

### Usuario (`users`)
Roles: `admin`, `supervisor`, `cajero`, `operador_balanza`
Campos clave: `nombre`, `email`, `rut`, `hashed_password`, `rol`, `activo`, `ultimo_login_at`

### Producto (`products`)
- Identificación: `codigo_barras`, `codigo_interno`, `nombre`
- Unidades: `UN`, `KG`, `L`, `PAQ`, `BOL`, `TAB`
- Precios en CLP (enteros, sin decimales): `precio_venta`, `precio_costo`
- Stock: `stock_actual`, `stock_minimo`, `stock_critico`, `stock_maximo`
- Relaciones: categoría, proveedor

### Estación (`stations`)
Tipos: `balanza`, `caja`
Estados: `activa`, `inactiva`, `error`
Campos: `nombre`, `tipo`, `ip_address`, `operador_actual_id`, `ultimo_evento_at`

### Pre-boleta
Generada en balanza. Contiene detalle completo + QR con UUID único.
Alerta automática a supervisor si `total_clp >= 50.000 CLP`.

### Venta (`sales`)
Métodos de pago: `efectivo`, `debito`, `credito`, `transferencia`
Estados: `completada`, `anulada`, `pendiente`, `error`
Referencia a pre-boleta (1:1), estación, cajero.
Al completarse: descuenta inventario + genera DTE SII.

### Cierre de caja (`cierres_caja`)
Registro de cierre por estación y cajero.

### DTE
Boleta electrónica SII. Vinculada a la venta.

### Proveedor (`proveedores`)
Gestión de proveedores de productos.

---

## API Backend — Routers Activos

| Prefix | Tag | Descripción |
|--------|-----|-------------|
| `/api/v1` | `preboleta` | Evento de creación de pre-boleta (WF03), auditoría y alertas |
| `/api/v1` | `invoices` | Gestión de facturas / DTE |
| `/health` | `infra` | Health check |

---

## Tareas Celery

| Módulo | Descripción |
|--------|-------------|
| `tasks.reports` | Generación de reportes gerenciales |
| `tasks.sii` | Emisión DTE al SII |
| `tasks.stock` | Alertas y actualización de stock |

---

## Frontend — Vistas

| Vista | Descripción |
|-------|-------------|
| `LoginView` | Autenticación |
| `DashboardView` | Métricas gerenciales en tiempo real |
| `CajaView` | Operación de caja (lectura QR, confirmación venta) |
| `CierreView` | Cierre de caja por turno |
| `InventoryView` | CRUD productos y stock |
| `StationsView` | Gestión y monitoreo de estaciones |
| `TransactionsView` | Historial de ventas |
| `ReportsView` | Reportes descargables |
| `UsersView` | Administración de usuarios |

## Frontend — Stores (Pinia)

`auth`, `caja`, `cierre`, `dashboard`, `inventory`, `reportes`, `turno`, `alerts`, `theme`, `zoom`

---

## Flujo Operacional Principal

```
1. Operador en balanza
   → Escanea código de barras
   → Sistema identifica producto + precio
   → Genera pre-boleta con detalle + QR único
   → [opcional] Alerta supervisor si total > $50.000 CLP

2. Cliente va a caja
   → Cajero escanea QR de la pre-boleta
   → Sistema recupera detalle completo
   → Cajero confirma método de pago

3. Confirmación de venta
   → Inventario descuenta automáticamente
   → Se emite DTE (boleta electrónica SII)
   → Auditoría registra el movimiento completo
```

---

## Costos de Infraestructura

| Concepto | USD/mes | CLP/mes |
|----------|---------|---------|
| VPS Hetzner CX31 | $3.60 | ~3.240 |
| Dominio .cl | $2.00 | ~1.800 |
| Cloudflare DNS+SSL | $0 | — |
| Backblaze B2 (backups) | $0 | — |
| SII / Bsale | $28.00 | ~25.200 |
| **TOTAL** | **$33.60** | **~30.240** |

Escalado a 10 locales: ~$328 USD/mes (~$32.80 por local).

---

## Roadmap de Sprints

| Sprint | Semanas | Objetivo |
|--------|---------|----------|
| Sprint 0 | 1 | Setup infraestructura Docker — ✅ Completado |
| Sprint 1-2 | 2-4 | CRUD productos, API estaciones, WebSocket, QR |
| Sprint 3-4 | 5-8 | Lectura QR, confirmación venta, integración SII |
| Sprint 5 | 9-10 | Dashboards, reportes gerenciales, alertas stock |
| Sprint 6 | 11-12 | QA, deploy producción, capacitación, documentación |

---

## Seguridad

- JWT + roles (admin, supervisor, cajero, operador_balanza)
- Auditoría completa: quién, qué, cuándo
- HTTPS (Caddy + Cloudflare)
- Secretos via variables de entorno (`.env`, no en repo)
- Rate limiting + validación de inputs
- Red Docker interna para servicios no expuestos

---

## Configuración Clave del Backend

```python
alerta_venta_alta_clp = 50_000   # Umbral para alerta supervisor (CLP)
smtp_from = "noreply@comerciales.cl"
email_gerencia / email_admin / email_supervisor  # Destinatarios de alertas
```

---

## Notas para Diseño Web

- Colores sugeridos: azul corporativo + blanco + gris neutro (negocio formal)
- Tono: profesional, confiable, orientado a negocios chilenos
- Idioma: español (Chile)
- Términos clave a usar: "inventario en tiempo real", "boleta electrónica SII",
  "trazabilidad completa", "gestión de caja", "múltiples estaciones"
- Público objetivo: dueños y administradores de locales comerciales / supermercados
- El sistema reemplaza procesos manuales y desconectados — ese es el dolor principal
