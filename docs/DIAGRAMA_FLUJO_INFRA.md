# DIAGRAMA DE FLUJO - INFRAESTRUCTURA GCP
## Visualización didáctica del sistema en Sprint 0

**Versión:** 0.1  
**Fecha:** 6 de abril de 2026  
**Para:** PM, Devs, Operarios  

---

## 📐 DIAGRAMA 1: FLUJO OPERACIONAL GENERAL

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USUARIO FINAL                             │
│                    (Operador, Cajero, Gerente)                      │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                    BROWSER/TABLET
                         │
                         │ HTTP/HTTPS
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
    ┌─────────────┐              ┌──────────────┐
    │ FRONTEND    │              │  FRONTEND    │
    │ (Vue 3)     │              │  (Static)    │
    │ localhost   │              │  Cloud Run   │
    │ 3000        │              │  /health     │
    └────┬────────┘              └──────┬───────┘
         │                              │
         │ JSON API + WebSocket         │
         │                              │
         └───────────────┬──────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   BACKEND (FastAPI)           │
         │   Cloud Run                   │
         │   :8000                       │
         │                               │
         │  ├─ /api/v1/products          │
         │  ├─ /api/v1/orders            │
         │  ├─ /api/v1/transactions      │
         │  ├─ /api/v1/stations          │
         │  └─ /ws (WebSocket)           │
         └─┬────────────┬───────────┬────┘
           │            │           │
           │            │           │
    ┌──────▼──┐  ┌──────▼─────┐  ┌─▼──────────┐
    │          │  │            │  │            │
    ▼          ▼  ▼            ▼  ▼            │
┌─────────┐ ┌──────────┐ ┌────────────┐       │
│PostgreSQL│ │  Redis   │ │   Cloud    │       │
│(Cloud SQL)│ │ (Memory- │ │  Storage   │       │
│          │ │  store)  │ │ (Backups)  │       │
│ • Datos  │ │          │ │            │       │
│ • Audit  │ │ • Cache  │ │ • XML SII  │       │
│ • Users  │ │ • Pub/Sub│ │ • Logs     │       │
│ • Stock  │ │ • Sessions│ │ • Assets   │       │
└──────────┘ └──────────┘ └────────────┘       │
                                               │
                                    ┌──────────▼──┐
                                    │             │
                                    ▼             │
                              ┌──────────────┐   │
                              │  SII Bsale   │   │
                              │  (Externa)   │   │
                              │              │   │
                              │ Emite boleta │   │
                              │ electrónica  │   │
                              └──────────────┘   │
                                    ▲            │
                                    └────────────┘
```

---

## 📐 DIAGRAMA 2: ARQUITECTURA EN CAPAS (Sprint 0 - GCP)

```
┌──────────────────────────────────────────────────────────────┐
│                     CAPA DE PRESENTACIÓN                      │
│                                                               │
│   ┌──────────┬──────────┬──────────────┐                    │
│   │ Operador │  Cajero  │  Gerente     │ (3 interfaces)     │
│   │ (Balanza)│  (POS)   │  (Dashboard) │                    │
│   └────┬─────┴────┬─────┴──────┬───────┘                    │
│        │          │            │                            │
└────────┼──────────┼────────────┼─────────────────────────────┘
         │ Vue 3    │ Vue 3      │ Vue 3
         │ (Dev)    │ (Prod)     │ (Prod)
         │ http     │ https      │ https
         │
┌────────┴──────────┴────────────┴─────────────────────────────┐
│                   CAPA DE API (FastAPI)                      │
│                                                               │
│           ┌─────────────────────────────────┐               │
│           │    API REST + WebSocket          │               │
│           │                                  │               │
│           │  Routers:                        │               │
│           │  ├─ products.py                  │               │
│           │  ├─ orders.py                    │               │
│           │  ├─ transactions.py              │               │
│           │  ├─ stations.py                  │               │
│           │  └─ ws.py (WebSocket)            │               │
│           │                                  │               │
│           │  Services:                       │               │
│           │  ├─ ProductService               │               │
│           │  ├─ InventoryService             │               │
│           │  ├─ OrderService                 │               │
│           │  └─ SIIService                   │               │
│           └────────┬────────────┬────────────┘               │
│                    │            │                            │
└────────────────────┼────────────┼──────────────────────────────┘
                     │ Async      │ Sync
                     │            │
        ┌────────────▼┐         ┌─▼─────────────┐
        │ Background  │         │   In-Memory   │
        │ Tasks       │         │   Cache       │
        │ (Celery)    │         │   (Redis)     │
        │             │         │               │
        │ • Boletas   │         │ • Sessions    │
        │ • Email     │         │ • Real-time   │
        │ • Reports   │         │ • Rate limits │
        └──────┬──────┘         └─┬─────────────┘
               │                  │
┌──────────────┼──────────────────┼──────────────────────────┐
│              │                  │ CAPA DE DATOS            │
│              │                  │                          │
│              ▼                  ▼                          │
│         ┌─────────────────────────────────┐              │
│         │   POSTGRESQL DATABASE           │              │
│         │   (Cloud SQL)                   │              │
│         │                                 │              │
│         │  Tables:                        │              │
│         │  • products                     │              │
│         │  • stations                     │              │
│         │  • orders                       │              │
│         │  • order_items                  │              │
│         │  • transactions                 │              │
│         │  • boletas                      │              │
│         │  • inventory_movements (audit)  │              │
│         │  • audit_logs                   │              │
│         │  • users                        │              │
│         └──────────────────────────────────┘              │
│                                                          │
│         ┌─────────────────────────────────┐              │
│         │   REDIS CACHE & PUB/SUB         │              │
│         │   (Memorystore)                 │              │
│         │                                 │              │
│         │  Features:                      │              │
│         │  • Session store                │              │
│         │  • WebSocket pub/sub            │              │
│         │  • Rate limiting                │              │
│         │  • Temporary data               │              │
│         └──────────────────────────────────┘              │
│                                                          │
│         ┌─────────────────────────────────┐              │
│         │   CLOUD STORAGE (Backups)       │              │
│         │   (gs://comerciales-backups)    │              │
│         │                                 │              │
│         │  Almacena:                      │              │
│         │  • DB backups (diarios)         │              │
│         │  • XML DTEs (SII)               │              │
│         │  • App logs                     │              │
│         └──────────────────────────────────┘              │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 📐 DIAGRAMA 3: FLUJO DE UNA VENTA (DEL CLIENTE A BD)

```
CLIENTE LLEGA A BALANZA
    │
    ▼
OPERADOR ESCANEA BARCODE (Escáner)
    │
    ▼
    ┌──────────────────────┐
    │  WebSocket           │
    │  (Tiempo Real)       │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────────────────────────┐
    │ FastAPI Backend                          │
    │ POST /api/v1/orders/add_item             │
    │                                          │
    │ 1. Valida barcode en DB                 │
    │ 2. Obtiene producto + precio            │
    │ 3. Crea OrderItem en PostgreSQL         │
    │ 4. Publica en Redis Pub/Sub             │
    └──────────┬──────────────────────────────┘
               │
               ├─────────────────┬───────────────┐
               │                 │               │
               ▼                 ▼               ▼
        ┌────────────┐    ┌──────────┐   ┌──────────────┐
        │PostgreSQL  │    │  Redis   │   │Pantalla      │
        │            │    │Pub/Sub   │   │Cliente       │
        │INSERT INTO │    │PUBLISH   │   │(WebSocket)   │
        │order_items │    │station:1 │   │Se actualiza  │
        └────────────┘    └──────────┘   │en tiempo real│
                                          └──────────────┘

CLIENTE DICE "LISTO"
    │
    ▼
OPERADOR FINALIZA ORDEN
    │
    ▼
    ┌──────────────────────────────────────┐
    │ FastAPI                              │
    │ POST /api/v1/orders/finalize         │
    │                                      │
    │ 1. Genera UUID único                │
    │ 2. Crea QR (UUID + detalle)         │
    │ 3. Guarda en PostgreSQL (orders)    │
    │ 4. Status = "pending"               │
    └──────────┬──────────────────────────┘
               │
               ▼
        ┌────────────────────┐
        │ QR Impreso         │
        │ (UUID + Detalle)   │
        └────────────────────┘

CLIENTE VA A CAJA CON QR
    │
    ▼
CAJERO ESCANEA QR
    │
    ▼
    ┌────────────────────────────────────────┐
    │ FastAPI                                │
    │ GET /api/v1/orders/{uuid}             │
    │                                        │
    │ 1. Busca en PostgreSQL por UUID       │
    │ 2. Recupera DETALLE COMPLETO          │
    │ 3. Retorna JSON con items            │
    └────────────┬─────────────────────────┘
                 │
                 ▼
          ┌─────────────┐
          │Pantalla Caja│
          │Muestra items│
          │y total      │
          └──────┬──────┘
                 │
                 ▼
      CAJERO CONFIRMA PAGO ($$$)
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │ FastAPI (Transacción ACID)             │
    │ POST /api/v1/transactions/complete     │
    │                                        │
    │ 1. Inserta en transactions            │
    │ 2. UPDATE products SET stock -= X     │  ← INVENTARIO AUTOMÁTICO
    │ 3. Inserta en inventory_movements    │
    │ 4. Inserta en audit_logs             │
    │ 5. COMMIT (todo o nada)              │
    │ 6. Dispara Celery task: emitir_boleta│
    └────────────┬──────────────────────────┘
                 │
                 ├──────────────────────────────────┐
                 │                                  │
                 ▼                                  ▼
        ┌──────────────────┐          ┌────────────────────┐
        │PostgreSQL        │          │Celery Task         │
        │UPDATE products   │          │(Background)        │
        │SET stock = stock - X        │                    │
        │                  │          │Emitir Boleta SII  │
        │Tomate: 50 → 48kg │          │mediante Bsale API │
        └──────────────────┘          └────────┬───────────┘
                                               │
                                               ▼
                                        ┌──────────────────┐
                                        │SII (Bsale)       │
                                        │                  │
                                        │Webhook response: │
                                        │- Folio SII       │
                                        │- XML DTE         │
                                        └────────┬─────────┘
                                                 │
                                                 ▼
                                        ┌──────────────────┐
                                        │Cloud Storage     │
                                        │                  │
                                        │Almacenar:        │
                                        │- XML DTE         │
                                        │- Boleta PDF      │
                                        └──────────────────┘

VENTA COMPLETADA ✅
    │
    ▼
PANTALLA CAJA MUESTRA:
  • Folio SII: 000142
  • Monto: $10.11
  • ✓ Boleta emitida
  • ✓ Inventario actualizado
  • ✓ Auditoría registrada
```

---

## 📐 DIAGRAMA 4: COMPONENTES Y COMUNICACIÓN

```
┌───────────────────────────────────────────────────────────────────┐
│                     AMBIENTE DE DESARROLLO                        │
│                   (Sprint 0 - 6 abril - 5 julio)                 │
└───────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │         DESARROLLADOR LOCAL (Allan / Jonathan)           │
    │                                                          │
    │  ┌─────────────────────────────────────────────────┐   │
    │  │  Laptop/Desktop                                │   │
    │  │                                                 │   │
    │  │  ├─ VSCode + Claude Code extension            │   │
    │  │  ├─ Docker (opcional)                         │   │
    │  │  ├─ Python 3.11 / Node.js 18+                │   │
    │  │  ├─ Git client                                │   │
    │  │  └─ gcloud CLI + credenciales                │   │
    │  │                                                 │   │
    │  └─────────┬───────────────────────────────────────┘   │
    │            │                                            │
    │            │ git push origin feature/xxx               │
    │            │ (GitHub)                                   │
    │            │                                            │
    └────────────┼────────────────────────────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────────────────────────────┐
    │              GITHUB (Repositorios)                       │
    │                                                          │
    │  ├─ comerciales-docs (documentación)                    │
    │  ├─ comerciales-backend (FastAPI code)                 │
    │  ├─ comerciales-frontend (Vue code)                    │
    │  └─ comerciales-infra (Terraform/scripts)              │
    │                                                          │
    │  CI/CD: GitHub Actions                                  │
    │  ├─ test.yml (pytest, npm test)                        │
    │  └─ deploy.yml (push a GCP)                            │
    │                                                          │
    └────┬─────────────────────────────────────────────────────┘
         │
         │ git push (trigger)
         │
         ▼
    ┌──────────────────────────────────────────────────────────┐
    │           GOOGLE CLOUD PLATFORM (us-central1)           │
    │                                                          │
    │  ┌────────────────────────────────────────────────┐    │
    │  │  Cloud Run (Backend)                           │    │
    │  │  • FastAPI en contenedor                       │    │
    │  │  • Puerto 8000                                 │    │
    │  │  • Auto-scaling 0-100 instancias              │    │
    │  │  • HTTPS automático                            │    │
    │  │  • $0/mes (free tier)                         │    │
    │  └────────────────────────────────────────────────┘    │
    │                           │                             │
    │                           │ conexión TCP                │
    │                           │                             │
    │    ┌──────────────────────┴───────────────────────┐    │
    │    │                      │                       │    │
    │    ▼                      ▼                       ▼    │
    │  ┌──────────────┐  ┌────────────┐  ┌──────────────┐  │
    │  │ Cloud SQL    │  │ Memorystore│  │Cloud Storage │  │
    │  │(PostgreSQL)  │  │ (Redis)    │  │(Backups)     │  │
    │  │              │  │            │  │              │  │
    │  │db-f1-micro   │  │1GB BASIC   │  │gs://comerc.. │  │
    │  │us-central1   │  │us-central1 │  │Standard      │  │
    │  │              │  │            │  │              │  │
    │  │$0/mes        │  │$0/mes      │  │$0/mes        │  │
    │  └──────────────┘  └────────────┘  └──────────────┘  │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
         │
         │ API calls (saliente)
         │
         ▼
    ┌──────────────────────────────────────────────────────────┐
    │        SERVICIOS EXTERNOS (Fuera de GCP)                 │
    │                                                          │
    │  ┌─────────────────────────────────────────────────┐   │
    │  │ SII Bsale (Boletas Electrónicas)               │   │
    │  │ https://api.bsale.cl/...                       │   │
    │  │                                                 │   │
    │  │ POST: Emitir boleta                            │   │
    │  │ GET: Estado boleta                             │   │
    │  │                                                 │   │
    │  │ Respuesta: XML DTE, Folio SII                 │   │
    │  └─────────────────────────────────────────────────┘   │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
```

---

## 📐 DIAGRAMA 5: FLUJO DE DATOS EN TIEMPO REAL (WebSocket)

```
BALANZA (Operador)                  CAJA (Cajero)
        │                                  │
        │ Escanea barcode                  │
        │                                  │
        ▼                                  │
┌──────────────────┐                      │
│ Navigador/App    │                      │
│ (Vue - Local)    │                      │
└────────┬─────────┘                      │
         │                                │
         │ WebSocket connection           │
         │ (ws://localhost:8000/ws)       │
         │                                │
         └────────────────┬───────────────┘
                          │
                          ▼
                 ┌─────────────────────┐
                 │ FastAPI Backend     │
                 │ WebSocket handler   │
                 │                     │
                 │ 1. Recibe mensaje   │
                 │ 2. Procesa          │
                 │ 3. Actualiza BD     │
                 │ 4. Publica evento   │
                 └────────┬────────────┘
                          │
                    ┌─────┴──────┐
                    │            │
                    ▼            ▼
            ┌──────────────┐  ┌────────────────┐
            │PostgreSQL    │  │Redis Pub/Sub   │
            │              │  │                │
            │INSERT/UPDATE │  │PUBLISH         │
            │              │  │station:1       │
            └──────────────┘  └────────┬───────┘
                                       │
                    ┌──────────────────┴─────────────────┐
                    │                                    │
                    ▼                                    ▼
         ┌─────────────────────┐        ┌─────────────────────┐
         │ Balanza (Operador)  │        │ Caja (Cajero)       │
         │ WebSocket subscribed│        │ WebSocket subscribed│
         │                     │        │                     │
         │ Recibe evento       │        │ Recibe evento       │
         │ Pantalla actualiza  │        │ Pantalla actualiza  │
         │ EN TIEMPO REAL      │        │ EN TIEMPO REAL      │
         │ (<100ms latencia)   │        │ (<100ms latencia)   │
         └─────────────────────┘        └─────────────────────┘
         
         Pre-boleta actualizada
         en ambas pantallas
         al mismo tiempo ✅
```

---

## 📐 DIAGRAMA 6: ARQUITECTURA FINAL (PRODUCCIÓN - Después del 6 julio)

```
┌────────────────────────────────────────────────────────────────┐
│                    PASO A PRODUCCIÓN (VPS)                     │
│                   (6 julio onwards)                            │
└────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────┐
    │  HETZNER VPS CX31                            │
    │  2vCPU, 4GB RAM, 40GB SSD                    │
    │  $3.60 USD/mes                               │
    │                                              │
    │  ┌──────────────────────────────────────┐   │
    │  │ Nginx (reverse proxy + SSL)          │   │
    │  │ :80/:443 → Cloudflare                │   │
    │  └──────────┬───────────────────────────┘   │
    │             │                                │
    │  ┌──────────▼───────────────────────────┐   │
    │  │ FastAPI + Gunicorn (4 workers)       │   │
    │  │ :8000                                │   │
    │  └──────────┬───────────────────────────┘   │
    │             │                                │
    │   ┌─────────┴──────────┬──────────────┐     │
    │   │                    │              │     │
    │   ▼                    ▼              ▼     │
    │ ┌─────────┐  ┌──────────┐  ┌──────────┐   │
    │ │Postgres │  │  Redis   │  │  Backup  │   │
    │ │ (local) │  │ (local)  │  │  Script  │   │
    │ │:5432    │  │:6379     │  │(cron)    │   │
    │ └─────────┘  └──────────┘  └──────────┘   │
    │                                              │
    │ Supervisor (process manager)                │
    │ ├─ FastAPI auto-restart                    │
    │ ├─ Redis auto-restart                      │
    │ └─ Nginx auto-restart                      │
    │                                              │
    └──────────────────────────────────────────────┘
             │
             │ HTTPS (Cloudflare SSL)
             │
             ▼
    ┌──────────────────────────────────────┐
    │  DOMINIO (.cl)                       │
    │  comerciales.tudominio.cl            │
    │                                      │
    │  DNS → Cloudflare (FREE)            │
    │  SSL → Cloudflare (FREE)            │
    │  CDN → Cloudflare (FREE)            │
    └──────────────────────────────────────┘
             │
             │
             ▼
    ┌──────────────────────────────────────┐
    │  BACKUPS (Cloud)                    │
    │                                      │
    │  B2 Backblaze                       │
    │  gs://comerciales-backups (antiguo) │
    │                                      │
    │  • DB dumps diarios                 │
    │  • 10GB gratis/mes                  │
    │  • Versionado                       │
    └──────────────────────────────────────┘
             │
             │
             ▼
    ┌──────────────────────────────────────┐
    │  SII BSALE                           │
    │  (Boletas Electrónicas)              │
    │  $28 USD/mes                         │
    │                                      │
    │  • Emitir DTE                        │
    │  • Recuperar folios                  │
    │  • Validar estado boleta             │
    └──────────────────────────────────────┘

COSTO TOTAL: ~$33.60 USD/mes
```

---

## 📊 TABLA RESUMEN: QUÉ HACE CADA COMPONENTE

| Componente | Función | Ubicación | Costo |
|-----------|---------|-----------|-------|
| **Cloud Run** | Ejecuta backend FastAPI | GCP us-central1 | $0 (dev) |
| **Cloud SQL** | Almacena datos (PostgreSQL) | GCP us-central1 | $0 (dev) |
| **Memorystore Redis** | Caché + WebSocket pub/sub | GCP us-central1 | $0 (dev) |
| **Cloud Storage** | Backups + XML SII | GCP us-central1 | $0 (dev) |
| **GitHub Actions** | CI/CD (test + build) | GitHub | $0 |
| **Cloudflare** | DNS + SSL + CDN | Cloudflare | $0 |
| **SII Bsale** | Boletas electrónicas | Externa (SII) | $28/mes |
| **VPS Hetzner** | Servidor producción | Hetzner eu | $3.60/mes |
| **B2 Backups** | Almacenamiento backups | Backblaze | $0 (10GB) |

---

## 🎯 RESUMEN VISUAL

**Sprint 0 (Desarrollo):**
- Todo en GCP Cloud (serverless)
- Costo: $0 USD
- Sin DevOps manual
- Auto-scaling automático

**Post-5 julio (Producción):**
- Backend en VPS Hetzner
- PostgreSQL + Redis self-hosted
- Costo: $33.60 USD/mes
- DevOps manual (Allen gestiona)
- Escalable verticalemente (upgrade VPS)

---

**Versión:** 0.1  
**Última actualización:** 6 de abril 2026  
**Próxima revisión:** Post Sprint 0
