# Sistema de Inventario Dinámico - Locales Comerciales Chile 🏪

**Versión:** 0.1-MVP | **Estado:** En Desarrollo (Sprint 0) | **Timeline:** 8-12 semanas

---

## 📋 Descripción del Proyecto

Sistema integral de inventario dinámico para locales comerciales (supermercados, multicategoría) que moderniza el flujo actual: **Balanza (4 estaciones) → Pre-boleta → Caja** en un **ecosistema conectado en tiempo real** con inventario actualizado automáticamente y boletas electrónicas SII integradas.

### Problema que Resuelve
- ❌ Balanza desconectada de caja (pre-boleta solo muestra TOTAL, no detalle)
- ❌ Inventario no actualiza automáticamente al vender
- ❌ Mucho trabajo manual después de cada venta
- ❌ Sin visibilidad de stock en tiempo real
- ❌ Difícil auditoría y trazabilidad de movimientos

### Solución Propuesta
✅ Sincronización en tiempo real (WebSocket) entre balanza ↔ caja  
✅ Pre-boleta con detalle completo + QR único (no solo total)  
✅ Inventario descuenta automáticamente al confirmar venta  
✅ Integración directa con SII (boleta electrónica DTE)  
✅ Auditoría completa e inmutable de todos los movimientos  
✅ Analytics gerencial en tiempo real (dashboard)  
✅ Alertas automáticas de stock bajo  

---

## 👥 Equipo

| Rol | Nombre | Responsabilidades |
|-----|--------|------------------|
| **PM / Arquitecto** | Giuliano | Visión, requerimientos, roadmap, stakeholders |
| **Dev Full-Stack** | Allan | Backend (FastAPI), infraestructura GCP, DevOps |
| **Dev Full-Stack** | Jonathan | Frontend (Vue 3), UI/UX, integraciones HW |

**Stack:** Python (FastAPI) + Vue 3 + PostgreSQL + GCP

---

## 🏗️ Estructura del Proyecto

```
📦 Proyecto Locales Comerciales
├── 📁 docs/                          # Documentación completa
│   ├── 📄 PRESENTACION.md           # Ejecutivo para PM
│   ├── 📄 ARQUITECTURA.md           # Diagramas C4 y decisiones técnicas
│   ├── 📄 MODELO_DATOS.md           # Esquema DB y relaciones
│   ├── 📄 API_REFERENCE.md          # OpenAPI auto-generado
│   ├── 📄 FLUJO_OPERACIONAL.md      # Paso a paso para operarios
│   ├── 📁 runbooks/                 # Procedimientos operacionales
│   │   ├── deploy.md
│   │   ├── backup.md
│   │   └── troubleshooting.md
│   └── 📁 hardware/                 # Especificaciones y protocolos
│       ├── scanner.md
│       ├── balanza.md
│       └── caja_pos.md
├── 📁 repos/                         # Repositorios GitHub (estructura)
│   ├── comerciales-backend/          # FastAPI + DB models
│   ├── comerciales-frontend/         # Vue 3 + Tailwind
│   ├── comerciales-infra/            # Terraform + GCP configs
│   └── comerciales-docs/             # Documentación (este repo)
├── 📄 PRESENTACION.md                # Documento ejecutivo (user-friendly)
├── 📄 presentacion.pptx              # PPT ejecutiva (se genera en Sprint 6)
└── 📄 CHANGELOG.md                   # Historial de cambios

```

---

## 📊 Flujo Operacional Mejorado

```
┌─────────────────────────────────────────────────────────────────┐
│ OPERADOR EN BALANZA (4 estaciones)                              │
├─────────────────────────────────────────────────────────────────┤
│ 1. Escanea código de barras del producto                        │
│    ↓ [WebSocket] → API Backend                                  │
│ 2. Sistema identifica producto + precio + categoría            │
│    ↓ [Redis] → Pantalla cliente (tiempo real)                  │
│ 3. Operador especifica cantidad (kg, unidades)                 │
│    ↓ [Pre-orden COMPLETA generada]                             │
│ 4. Se genera QR único con UUID + detalle completo             │
│    ↓ Cliente ve su QR en pantalla (pagar en caja)             │
└─────────────────────────────────────────────────────────────────┘
                            ↓↓↓
┌─────────────────────────────────────────────────────────────────┐
│ CAJERO EN CAJA/POS                                              │
├─────────────────────────────────────────────────────────────────┤
│ 1. Escanea QR del cliente                                       │
│    ↓ [API] → Backend recupera UUID                             │
│ 2. Sistema OBTIENE DETALLE COMPLETO (no solo total)           │
│    ↓ [Pantalla caja] → muestra productos + precios           │
│ 3. Cajero confirma venta (efectivo/tarjeta/transferencia)     │
│    ↓ [Celery task] → Actualiza inventario -X unidades         │
│ 4. Sistema emite boleta electrónica vía SII                   │
│    ↓ [Webhook SII] → Recibe folio + XML DTE                  │
│ 5. Auditoría registra: QR UUID, items, usuario, timestamp    │
│    ↓ Cliente recibe boleta (impresa o por email)              │
└─────────────────────────────────────────────────────────────────┘
                            ↓↓↓
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND (Sincronización + Logística)                            │
├─────────────────────────────────────────────────────────────────┤
│ • PostgreSQL: datos persistentes + audit log                   │
│ • Redis: caché + pub/sub WebSocket                             │
│ • Celery: tareas asíncronas (boletas, notificaciones)         │
│ • n8n: orquestación (alertas stock, notificaciones)            │
│ • Metabase: dashboards analytics gerenciales                  │
│ • SII: boleta electrónica integrada                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Hitos Principales

### Sprint 0 — Setup & Arquitectura (Semana 1)
- [ ] Setup GCP proyecto + Cloud SQL + Cloud Run
- [ ] Repositorios GitHub + GitHub Actions
- [ ] Scaffolding backend (FastAPI) + frontend (Vue 3)
- [ ] **REUNIÓN MARTES:** Especificaciones hardware
- [ ] Confirmación proveedor SII

### Sprint 1-2 — Módulos Inventario + Balanza (Semana 2-4)
- [ ] CRUD productos (barcode, categoría, precio, stock)
- [ ] API de estaciones (4 estaciones activas)
- [ ] WebSocket sincronización operador ↔ pantalla cliente
- [ ] Generación QR con UUID + detalle completo

### Sprint 3-4 — Caja + SII (Semana 5-8)
- [ ] Lectura QR → recupera detalle
- [ ] Confirmación venta → descuento automático inventario
- [ ] Integración SII (boleta electrónica)
- [ ] Sistema de auditoría completo

### Sprint 5 — Analytics (Semana 9-10)
- [ ] Dashboards Metabase
- [ ] Reportes gerenciales
- [ ] Alertas stock bajo

### Sprint 6 — QA & Deploy (Semana 11-12)
- [ ] Testing end-to-end
- [ ] Deploy producción
- [ ] Capacitación operadores
- [ ] Documentación + Presentación final

---

## 💰 Inversión Estimada

### Infraestructura Mensual (REVISADA - Costo Bajo)
| Concepto | Costo USD | Costo CLP |
|----------|-----------|-----------|
| VPS Hetzner CX31 (2vCPU, 4GB, 40GB SSD) | $3.60 | 3,240 |
| Dominio (.cl) | $2.00 | 1,800 |
| Cloudflare (DNS + SSL) | $0.00 | - |
| B2 Backups (10GB free) | $0.00 | - |
| SII (Bsale) | $28.00 | 25,200 |
| **TOTAL INFRAESTRUCTURA** | **$33.60/mes** | **~30,240 CLP/mes** |

### Desarrollo (Estimado)
- 2 devs x 10-12 semanas (dentro de presupuesto $15k-$40k)
- Design/UX: ~$1-2k
- Documentación + Presentación: incluido en timeline

### Escalado (Cuando llegues a 10 locales)
- VPS upgrade (si necesario): +$4.40 USD/mes
- SII × 10 locales: $280 USD/mes
- **Total para 10 locales:** ~$328 USD/mes (~$32.80 por local)

---

## 🔐 Seguridad & Cumplimiento

- **JWT + Roles:** ADMIN, GERENTE, CAJERO, OPERADOR
- **Auditoría completa:** Quién hizo qué, cuándo y por qué
- **SII (DTE):** Boletas electrónicas legales en Chile
- **HTTPS + Secret Manager:** Datos sensibles protegidos
- **Rate limiting + Input validation:** Protección contra ataques

---

## 📚 Documentación

Ver carpeta `/docs/` para:
- **PRESENTACION.md** — Resumen ejecutivo (este documento amplificado)
- **ARQUITECTURA.md** — Diagramas C4, decisiones técnicas, trade-offs
- **MODELO_DATOS.md** — Esquema DB, relaciones, constraints
- **API_REFERENCE.md** — Endpoints (auto-generado por FastAPI)
- **FLUJO_OPERACIONAL.md** — Paso a paso para operarios
- **runbooks/** — Procedimientos: deploy, backup, troubleshooting

---

## 🚀 Próximos Pasos

1. **Hoy:** Aprobación de esta arquitectura ✅
2. **Martes:** Reunión en local → especificaciones hardware exactas
3. **Miércoles:** Sprint 0 → Setup GCP + repos GitHub
4. **Semana 2:** Sprint 1 → Primer módulo (inventario) operativo

---

## 📞 Contacto & Escalamiento

- **PM (Decisiones):** Giuliano
- **Backend (GCP, APIs):** Allan
- **Frontend (UI/UX, Hardware):** Jonathan
- **Escalamientos:** Ver PRESENTACION.md

---

**Última actualización:** 5 de abril de 2026  
**Próxima revisión:** Después de reunión martes (especificaciones hardware)
