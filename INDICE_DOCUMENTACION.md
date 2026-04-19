# ÍNDICE CENTRAL DE DOCUMENTACIÓN
## Sistema de Inventario Dinámico - Locales Comerciales Chile

**Última actualización:** 5 de abril de 2026  
**Versión del documento:** 0.1

---

## 🎯 COMIENZA AQUÍ (Para nuevas personas)

### Si eres **PM/Cliente**
1. [README.md](README.md) — Overview general (10 min)
2. [PRESENTACION.md](docs/PRESENTACION.md) — Ejecutivo + ROI (15 min)
3. [RESUMEN_ENTREGA.md](RESUMEN_ENTREGA.md) — Status actual (5 min)

### Si eres **Developer Backend (Allan)**
1. [README.md](README.md) — Context (10 min)
2. [ARQUITECTURA.md](docs/ARQUITECTURA.md) — Full architecture (30 min)
3. [BACKEND_MODELO_DATOS.md](docs/BACKEND_MODELO_DATOS.md) — Database schema (20 min)
4. [SPRINT0_BACKEND_SETUP.md](docs/SPRINT0_BACKEND_SETUP.md) — Levantar entorno local Docker (10 min)
5. [BACKEND_PROXIMOS_PASOS.md](docs/BACKEND_PROXIMOS_PASOS.md) — Qué hacer ahora (5 min)
6. [Plan detallado](/plans/swirling-knitting-hickey.md) — Sprints (15 min)

### Si eres **Developer Frontend (Jonathan)**
1. [README.md](README.md) — Context (10 min)
2. [FRONTEND_UI_GERENTE.md](docs/FRONTEND_UI_GERENTE.md) — Mockups + componentes dashboard (25 min)
3. [FLUJO_OPERACIONAL.md](docs/FLUJO_OPERACIONAL.md) — User flows (30 min)
4. [ARQUITECTURA.md](docs/ARQUITECTURA.md) — Tech stack + decisiones (20 min)
5. **Código base:** `npm install && npm run dev` en repo comerciales-frontend
6. [Plan detallado](/plans/swirling-knitting-hickey.md) — Sprints (15 min)

### Si eres **Operario/Capacitador**
1. [FLUJO_OPERACIONAL.md](docs/FLUJO_OPERACIONAL.md) — Step by step (30 min)
2. [README.md](README.md) — General overview (10 min)

---

## 📑 ÍNDICE COMPLETO

### 📋 Documentos Principales

| Documento | Tipo | Audiencia | Contenido | Estado |
|-----------|------|-----------|-----------|--------|
| [README.md](README.md) | Overview | Todos | Descripción proyecto, flujos, hitos, costos | ✅ |
| [PRESENTACION.md](docs/PRESENTACION.md) | Ejecutivo | PM, Cliente | Problema, solución, ROI, presupuesto, riesgos | ✅ |
| [RESUMEN_ENTREGA.md](RESUMEN_ENTREGA.md) | Status | Todos | Qué se entregó, métricas, próximos hitos | ✅ |
| [PROXIMOS_PASOS.md](PROXIMOS_PASOS.md) | Roadmap | PM, Devs | Plan inmediato, reunión martes, Sprint 0 | ✅ |
| [CAMBIOS_INFRAESTRUCTURA.md](CAMBIOS_INFRAESTRUCTURA.md) | Decisión | PM, Devs | Cambio: GCP → VPS (73% reducción costos) | ✅ NUEVO |
| [INDICE_DOCUMENTACION.md](INDICE_DOCUMENTACION.md) | Navegación | Todos | Éste: tabla de contenidos (Ahora lees) | ✅ |

### 🏗️ Documentación Técnica

| Documento | Enfoque | Audiencia | Contenido | Estado |
|-----------|---------|-----------|-----------|--------|
| [ARQUITECTURA.md](docs/ARQUITECTURA.md) | Técnica General | Devs, Tech Lead | Diagramas C4, stack, decisiones, trade-offs, flujo E2E | ✅ |
| [BACKEND_MODELO_DATOS.md](docs/BACKEND_MODELO_DATOS.md) | Backend — Base de Datos | Backend Dev | 11 tablas, relaciones, índices, constraints, triggers | ✅ |
| [BACKEND_INFRAESTRUCTURA_ECONOMICA.md](docs/BACKEND_INFRAESTRUCTURA_ECONOMICA.md) | Backend — Infraestructura | PM, Backend Dev | VPS self-hosted, costos bajos ($33.60/mes), trade-offs | ✅ |
| [BACKEND_GCP_SETUP_COMPLETADO.md](docs/BACKEND_GCP_SETUP_COMPLETADO.md) | Backend — Infra | Backend Dev | Cloud SQL, Redis, Storage activos en GCP | ✅ |
| [BACKEND_SETUP_GCP_VSCODE.md](docs/BACKEND_SETUP_GCP_VSCODE.md) | Backend — Dev Setup | Backend Dev | Vincular GCP a VSCode para desarrollo local | ✅ |
| [BACKEND_DIAGRAMA_FLUJO_INFRA.md](docs/BACKEND_DIAGRAMA_FLUJO_INFRA.md) | Backend — Infra | Backend Dev, PM | Diagramas ASCII de infraestructura GCP | ✅ |
| [BACKEND_ESTRATEGIA_HIBRIDA.md](docs/BACKEND_ESTRATEGIA_HIBRIDA.md) | Backend — Infra | Backend Dev, PM | GCP Free Trial + VPS, estrategia de costos | ✅ |
| [SPRINT0_BACKEND_SETUP.md](docs/SPRINT0_BACKEND_SETUP.md) | Backend — DevOps | Backend Dev | Docker compose, fix migración Alembic, validación stack local | ✅ |
| [BACKEND_PROXIMOS_PASOS.md](docs/BACKEND_PROXIMOS_PASOS.md) | Backend — Roadmap | Backend Dev | 5 pasos priorizados: auth JWT, tests, CI, seed, seguridad | ✅ |
| [FLUJO_OPERACIONAL.md](docs/FLUJO_OPERACIONAL.md) | Operaciones | Frontend Dev, Operarios | Paso a paso, pantallas, situaciones especiales | ✅ |
| [FRONTEND_UI_GERENTE.md](docs/FRONTEND_UI_GERENTE.md) | Frontend — Interfaz | Frontend Dev, PM | Mockups ASCII 7 vistas, componentes Vue3, dark theme, palette | ✅ |
| [Plan detallado](/plans/swirling-knitting-hickey.md) | Implementación | Devs, PM | 6 Sprints, tareas, timeline, análisis costos (REVISADO) | ✅ |

### 🔧 Registro Central de Variables

| Archivo | Prefijo | Repo origen | Variables |
|---------|---------|-------------|-----------|
| [variables/BKND_VARIABLES.env](variables/BKND_VARIABLES.env) | `BKND_` | comerciales-backend | App, DB, Redis, SMTP, Alertas, AI (16 vars) |
| [variables/FRNT_VARIABLES.env](variables/FRNT_VARIABLES.env) | `FRNT_` | comerciales-frontend | API URL, WS, App config, Feature flags (6 vars) |
| [variables/PROVISIONAL_DB_VARIABLES.md](variables/PROVISIONAL_DB_VARIABLES.md) | — | Análisis UI | Gap analysis UI vs backend: 23 variables faltantes, 5 tablas nuevas |

### 🗄️ Modelo Relacional y ERD

| Documento | Contenido |
|-----------|-----------|
| [BACKEND_ERD_MODELO_RELACIONAL.md](docs/BACKEND_ERD_MODELO_RELACIONAL.md) | ERD Mermaid completo + DDL PostgreSQL de las 16 tablas del sistema |

### 📁 Carpetas de Documentación (Por llenar)

| Carpeta | Propósito | Contenido | Timeline |
|---------|-----------|-----------|----------|
| `/docs/hardware/` | Especificaciones hardware | Scanner, balanza, caja specs | Post-martes 9 |
| `/docs/runbooks/` | Operaciones | Deploy, backup, troubleshooting | Sprints 1-6 |
| `/docs/api-reference/` | API docs | OpenAPI specs (auto-generado) | Sprint 0 |
| `/docs/onboarding/` | Capacitación | Guías dev, setup local | Sprint 0-1 |

---

## 🔍 BÚSQUEDA POR TEMA

### Arquitectura & Diseño
- **¿Cómo es la arquitectura general?** → [ARQUITECTURA.md](docs/ARQUITECTURA.md) - Sección 1
- **¿Cuál es el diagrama de datos?** → [MODELO_DATOS.md](docs/MODELO_DATOS.md) - Sección ER
- **¿Cómo se comunican los sistemas?** → [ARQUITECTURA.md](docs/ARQUITECTURA.md) - Sección Flujo E2E
- **¿Qué tecnologías usamos y por qué?** → [ARQUITECTURA.md](docs/ARQUITECTURA.md) - Sección 6-7

### Implementación & Roadmap
- **¿Cuál es el plan detallado?** → [Plan](/plans/swirling-knitting-hickey.md)
- **¿Qué hacer ahora (esta semana)?** → [PROXIMOS_PASOS.md](PROXIMOS_PASOS.md)
- **¿Cuál es el timeline completo?** → [Plan](/plans/swirling-knitting-hickey.md) - Sección 5

### Base de Datos
- **¿Cuál es el schema de DB?** → [BACKEND_MODELO_DATOS.md](docs/BACKEND_MODELO_DATOS.md) - Sección 2
- **¿Qué tablas existen?** → [BACKEND_MODELO_DATOS.md](docs/BACKEND_MODELO_DATOS.md) - Sección 3
- **¿Cómo se auditan los datos?** → [BACKEND_MODELO_DATOS.md](docs/BACKEND_MODELO_DATOS.md) - Sección 11
- **¿Cuál es el ERD completo actualizado?** → [BACKEND_ERD_MODELO_RELACIONAL.md](docs/BACKEND_ERD_MODELO_RELACIONAL.md)
- **¿Qué le falta al backend vs el frontend?** → [variables/PROVISIONAL_DB_VARIABLES.md](variables/PROVISIONAL_DB_VARIABLES.md)

### Operaciones & UX
- **¿Cómo se ve el dashboard del gerente?** → [FRONTEND_UI_GERENTE.md](docs/FRONTEND_UI_GERENTE.md) - Mockups ASCII
- **¿Qué componentes Vue3 hay?** → [FRONTEND_UI_GERENTE.md](docs/FRONTEND_UI_GERENTE.md) - Sección Estructura
- **¿Cuál es el flujo de una venta?** → [FLUJO_OPERACIONAL.md](docs/FLUJO_OPERACIONAL.md) - Sección 3
- **¿Qué hace cada rol?** → [FLUJO_OPERACIONAL.md](docs/FLUJO_OPERACIONAL.md) - Sección 1
- **¿Cómo manejo situaciones especiales?** → [FLUJO_OPERACIONAL.md](docs/FLUJO_OPERACIONAL.md) - Sección 4

### Negocio & Financiero
- **¿Cuál es el ROI?** → [PRESENTACION.md](docs/PRESENTACION.md) - Sección ROI
- **¿Cuánto cuesta?** → [PRESENTACION.md](docs/PRESENTACION.md) - Sección 4 & [README.md](README.md) - Inversión
- **¿Cuáles son los riesgos?** → [PRESENTACION.md](docs/PRESENTACION.md) - Sección Riesgos

### Seguridad
- **¿Cómo está asegurado el sistema?** → [ARQUITECTURA.md](docs/ARQUITECTURA.md) - Sección 7
- **¿Qué roles y permisos existen?** → [ARQUITECTURA.md](docs/ARQUITECTURA.md) - Matriz Autenticación
- **¿Cómo se audita?** → [MODELO_DATOS.md](docs/MODELO_DATOS.md) - Tabla audit_logs

---

## 📊 ESTRUCTURA DE CARPETAS (Proyecto Completo)

```
Proyecto Locales Comerciales/
├── 📄 README.md                      ← START HERE
├── 📄 PRESENTACION.md
├── 📄 RESUMEN_ENTREGA.md
├── 📄 PROXIMOS_PASOS.md
├── 📄 INDICE_DOCUMENTACION.md        ← Eres aquí
├── 📄 CHANGELOG.md                   (Por crear)
│
├── 📁 docs/                          ← Documentación técnica
│   ├── 📄 ARQUITECTURA.md
│   ├── 📄 MODELO_DATOS.md
│   ├── 📄 FLUJO_OPERACIONAL.md
│   ├── 📁 hardware/                  (Post-martes)
│   │   ├── scanner.md
│   │   ├── balanza.md
│   │   └── caja_pos.md
│   ├── 📁 runbooks/                  (Sprints 1+)
│   │   ├── deploy.md
│   │   ├── backup.md
│   │   ├── troubleshooting.md
│   │   └── oncall.md
│   ├── 📁 api-reference/             (Sprint 0)
│   │   └── openapi.yml               (auto-generado)
│   └── 📁 onboarding/                (Sprint 0-1)
│       ├── dev-setup.md
│       ├── env-variables.md
│       └── first-run.md
│
├── 📁 plans/
│   └── 📄 swirling-knitting-hickey.md ← Plan detallado aprobado
│
├── 📁 repos/                         (Estructura para GitHub)
│   ├── comerciales-backend/
│   ├── comerciales-frontend/
│   ├── comerciales-infra/
│   └── comerciales-docs/
│
└── 📄 presentacion.pptx              (Se crea Sprint 6)
```

---

## 🎯 MAPEO: DOCUMENTO → PERSONA → ACCIÓN

```
PM/Giuliano
├── Lee: README + PRESENTACION + RESUMEN_ENTREGA
├── Usa: PROXIMOS_PASOS (reunión martes)
├── Cuando martes: Crea docs/hardware/
└── Mantiene: Plan general, stakeholder alignment

Backend/Allan
├── Lee: ARQUITECTURA + MODELO_DATOS + Plan
├── Setup: GCP, Cloud SQL, Alembic migrations
├── Crea: Repositorio backend
├── Cuando Sprint 0: Setup infraestructura
└── Mantiene: API, DB, deployment

Frontend/Jonathan
├── Lee: FLUJO_OPERACIONAL + ARQUITECTURA + Plan
├── Crea: Vue 3 componentes, pantallas
├── Repositorio: Frontend
├── Cuando Sprint 0: Setup UI mockups
└── Mantiene: UX, hardware integration

Operarios/Capacitador
├── Lee: FLUJO_OPERACIONAL (paso a paso)
├── Imprime: Mockups de pantallas (para capacitación)
├── Practica: Con sistema en piloto
└── Mantiene: Feedback para mejoras
```

---

## 🚀 CÓMO NAVEGAR ESTE WIKI

### Opción 1: Por Rol (Recomendado)
- Si eres PM → Lee sección "Si eres PM"
- Si eres Dev Backend → Lee sección "Si eres Dev Backend"
- Si eres Dev Frontend → Lee sección "Si eres Dev Frontend"

### Opción 2: Por Tema
- Usa la tabla "BÚSQUEDA POR TEMA" más arriba

### Opción 3: Lectura Secuencial
1. README.md
2. PRESENTACION.md
3. ARQUITECTURA.md
4. MODELO_DATOS.md
5. FLUJO_OPERACIONAL.md
6. Plan detallado
7. PROXIMOS_PASOS.md

---

## 📋 DOCUMENTACIÓN POR SPRINT

### Sprint 0 (Semana 1)
- ✅ Documentos base (este índice completo)
- ⏳ Reunión martes (specs hardware)
- ⏳ Crear: API reference (OpenAPI)
- ⏳ Crear: Dev onboarding

### Sprint 1-6 (Semanas 2-12)
- Crear runbooks (deploy, backup, troubleshooting)
- Actualizar MODELO_DATOS si cambios en schema
- Agregar ejemplos de uso real (cuando operativo)
- Crear presentación final (PPT - Sprint 6)

---

## ✅ CHECKLIST: "¿He leído lo que necesito?"

### Para PM:
- [ ] README.md
- [ ] PRESENTACION.md
- [ ] PROXIMOS_PASOS.md
- [ ] RESUMEN_ENTREGA.md
- [ ] (Opcional) ARQUITECTURA.md secciones 1-2

### Para Backend Dev:
- [ ] README.md
- [ ] ARQUITECTURA.md (completo)
- [ ] MODELO_DATOS.md (completo)
- [ ] Plan detallado (Sprints 0-2)

### Para Frontend Dev:
- [ ] README.md
- [ ] FLUJO_OPERACIONAL.md (completo)
- [ ] ARQUITECTURA.md secciones 1-3, 6
- [ ] Plan detallado (Sprints 0-2)

### Para Operarios:
- [ ] FLUJO_OPERACIONAL.md (completo)
- [ ] README.md (breve)

---

## 🤝 CONTRIBUIR A LA DOCUMENTACIÓN

### Quién actualiza qué:
- **Arquitectura/Decisiones:** PM + Allan
- **Implementación/APIs:** Allan
- **UI/UX:** Jonathan
- **Operaciones/Runbooks:** Todos (cuando se estabiliza)

### Cómo actualizar:
1. Actualiza el documento relevant (ej: MODELO_DATOS.md)
2. Actualiza CHANGELOG.md con cambios
3. Commit a rama develop (no main)
4. PR review antes de merge
5. Informa a equipo en daily standup

---

## 📞 ¿No encuentras lo que buscas?

| Pregunta | Responde |
|----------|----------|
| ¿Cuál es el flujo de una venta? | FLUJO_OPERACIONAL.md |
| ¿Cómo funciona X módulo? | ARQUITECTURA.md |
| ¿Cuál es el schema de X tabla? | MODELO_DATOS.md |
| ¿Cuáles son los próximos pasos? | PROXIMOS_PASOS.md |
| ¿Cuál es el timeline? | Plan detallado |
| ¿Cuánto cuesta esto? | PRESENTACION.md o README.md |
| ¿Cuál es el ROI? | PRESENTACION.md |
| ¿Cómo configuro el dev env? | docs/onboarding/dev-setup.md (Sprint 0) |
| ¿Cómo deployamos? | docs/runbooks/deploy.md (Sprints 1+) |
| ¿Qué hacer si X falla? | docs/runbooks/troubleshooting.md (Sprints 1+) |

---

## 🎓 ONBOARDING RÁPIDO (15 MINUTOS)

Si tienes 15 minutos solamente:
1. Lee [README.md](README.md) (10 min)
2. Hojea [PRESENTACION.md](docs/PRESENTACION.md) sección "Solución Propuesta" (5 min)
3. Pregunta dudas

Si tienes 30 minutos:
1. Lee [README.md](README.md) (10 min)
2. Lee [PRESENTACION.md](docs/PRESENTACION.md) (15 min)
3. Hojea [RESUMEN_ENTREGA.md](RESUMEN_ENTREGA.md) (5 min)

---

## 🎬 CONCLUSIÓN

Esta documentación es tu **fuente única de verdad (SSOT)** para el proyecto. Está diseñada para ser:
- ✅ Completa (nada falta)
- ✅ Navegable (fácil encontrar lo que necesitas)
- ✅ Versionada (CHANGELOG.md)
- ✅ Mantenible (actualizada en cada sprint)

**Úsala como referencia constante durante el desarrollo.**

---

**Versión:** 0.1  
**Última actualización:** 5 de abril 2026  
**Próxima actualización:** Post-reunión martes 9 (agregar specs hardware)  

**¡Bienvenido al proyecto! 🚀**
