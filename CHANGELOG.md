# CHANGELOG
## Sistema de Inventario Dinámico - Locales Comerciales Chile

Todas las cambios notables en este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto sigue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2] - 2026-04-12

### Agregado (Added)
- `comerciales-backend/docker-compose.yml` — orquestación completa con 6 servicios (PostgreSQL, Redis, API, Worker, Beat, Flower)
- `comerciales-backend/.env` — variables de entorno para desarrollo local
- `docs/SPRINT0_BACKEND_SETUP.md` — documentación completa del setup Docker: archivos creados, problemas encontrados, soluciones, validación final, comandos de referencia
- `docs/BACKEND_PROXIMOS_PASOS.md` — hoja de ruta técnica: 5 pasos priorizados para optimizar el desarrollo backend (auth JWT, tests, CI, seed, seguridad .env)

### Cambios (Changed)
- `alembic/versions/1c293d396139_initial.py` — fix bug SQLAlchemy 2.x: reemplazado `sa.Enum(..., create_type=False)` por `postgresql.ENUM(name=..., create_type=False)` en las 7 columnas enum de la migración inicial
- `INDICE_DOCUMENTACION.md` — referencias actualizadas, convención de nombres aplicada, nuevos docs agregados
- Convención de nombres aplicada: todos los docs de backend llevan prefijo `BACKEND_`, frontend llevan `FRONTEND_`
  - `MODELO_DATOS.md` → `BACKEND_MODELO_DATOS.md`
  - `GCP_SETUP_COMPLETADO.md` → `BACKEND_GCP_SETUP_COMPLETADO.md`
  - `INFRAESTRUCTURA_ECONOMICA.md` → `BACKEND_INFRAESTRUCTURA_ECONOMICA.md`
  - `SETUP_GCP_VSCODE.md` → `BACKEND_SETUP_GCP_VSCODE.md`
  - `DIAGRAMA_FLUJO_INFRA.md` → `BACKEND_DIAGRAMA_FLUJO_INFRA.md`
  - `ESTRATEGIA_HIBRIDA.md` → `BACKEND_ESTRATEGIA_HIBRIDA.md`
  - `UI_GERENTE.md` → `FRONTEND_UI_GERENTE.md`

### Bugs Arreglados (Fixed)
- Migración Alembic fallaba con `psycopg2.errors.DuplicateObject: type already exists` al levantar la DB por primera vez. Causa: SQLAlchemy 2.x ignora `create_type=False` en `sa.Enum` con valores posicionales durante el evento `_on_table_create`. Fix: usar `postgresql.ENUM(name=..., create_type=False)`.

### Infraestructura
- WSL2 kernel instalado en máquina de desarrollo (`wsl --update`)
- Docker Desktop 29.3.1 operativo con backend WSL2

---

## [0.3] - 2026-04-12

### Convención de nombres — Documentación técnica

Establecida la convención de prefijos para identificar el dominio de cada documento técnico:

| Prefijo | Dominio | Ejemplo |
|---------|---------|---------|
| `BACKEND_` | Documentos técnicos de backend | `BACKEND_MODELO_DATOS.md` |
| `FRONTEND_` | Documentos técnicos de frontend | `FRONTEND_UI_GERENTE.md` |
| _(sin prefijo)_ | Documentos generales o de operaciones | `ARQUITECTURA.md`, `FLUJO_OPERACIONAL.md` |

### Cambios (Changed) — Renombrado de documentos existentes

Aplicada la convención retroactivamente con `git mv` (historial preservado):

| Nombre anterior | Nombre nuevo |
|-----------------|--------------|
| `docs/MODELO_DATOS.md` | `docs/BACKEND_MODELO_DATOS.md` |
| `docs/GCP_SETUP_COMPLETADO.md` | `docs/BACKEND_GCP_SETUP_COMPLETADO.md` |
| `docs/INFRAESTRUCTURA_ECONOMICA.md` | `docs/BACKEND_INFRAESTRUCTURA_ECONOMICA.md` |
| `docs/SETUP_GCP_VSCODE.md` | `docs/BACKEND_SETUP_GCP_VSCODE.md` |
| `docs/DIAGRAMA_FLUJO_INFRA.md` | `docs/BACKEND_DIAGRAMA_FLUJO_INFRA.md` |
| `docs/ESTRATEGIA_HIBRIDA.md` | `docs/BACKEND_ESTRATEGIA_HIBRIDA.md` |
| `docs/UI_GERENTE.md` | `docs/FRONTEND_UI_GERENTE.md` |

### Agregado (Added) — Registro central de variables

Creada carpeta `variables/` con los registros de todas las variables de entorno del proyecto,
usando prefijos únicos por dominio para identificación rápida:

**`variables/BKND_VARIABLES.env`** — Backend (16 variables, prefijo `BKND_`)

| Grupo | Variables |
|-------|-----------|
| App | `BKND_APP_NAME`, `BKND_API_KEY` |
| Base de datos | `BKND_DATABASE_URL` |
| Redis / Celery | `BKND_REDIS_URL` |
| SMTP | `BKND_SMTP_HOST`, `BKND_SMTP_PORT`, `BKND_SMTP_USER`, `BKND_SMTP_PASSWORD`, `BKND_SMTP_FROM` |
| Alertas | `BKND_EMAIL_GERENCIA`, `BKND_EMAIL_ADMIN`, `BKND_EMAIL_SUPERVISOR`, `BKND_ALERTA_VENTA_ALTA_CLP` |
| AI | `BKND_MISTRAL_API_KEY`, `BKND_GOOGLE_API_KEY`, `BKND_OPENAI_API_KEY` |

**`variables/FRNT_VARIABLES.env`** — Frontend (6 variables, prefijo `FRNT_`)

| Grupo | Variables |
|-------|-----------|
| API / Backend | `FRNT_API_BASE_URL`, `FRNT_WS_URL` |
| App | `FRNT_APP_TITLE`, `FRNT_APP_VERSION` |
| Feature Flags | `FRNT_ENABLE_ANALYTICS`, `FRNT_ENABLE_MOCK_DATA` |

Cada archivo incluye:
- Descripción de cada variable
- Ejemplos de valor para dev local, staging y producción
- Indicador de si la variable es requerida u opcional
- Tabla de correspondencia entre nombre `BKND_`/`FRNT_` y nombre real en `.env`

### Cambios (Changed) — INDICE_DOCUMENTACION.md
- Agregada sección "Registro Central de Variables" con enlaces a ambos archivos
- Actualizadas todas las referencias a los documentos renombrados
- Actualizado onboarding de Backend Dev y Frontend Dev con nuevas rutas

---

## [0.1] - 2026-04-05

### Agregado (Added)
- ✅ **README.md** - Overview general del proyecto con descripción de problema, solución, equipo, estructura
- ✅ **PRESENTACION.md** - Documento ejecutivo para PM con métricas, ROI, presupuesto, riesgos
- ✅ **ARQUITECTURA.md** - Diagramas C4 completos, stack tecnológico, decisiones, flujo end-to-end
- ✅ **MODELO_DATOS.md** - Esquema de base de datos con 11 tablas, relaciones, índices, constraints, triggers
- ✅ **FLUJO_OPERACIONAL.md** - Guía paso a paso para operadores, cajeros, gerentes con situaciones especiales
- ✅ **PROXIMOS_PASOS.md** - Roadmap inmediato con reunión martes, Sprint 0, checklist
- ✅ **RESUMEN_ENTREGA.md** - Status de qué se entregó, métricas, próximos hitos
- ✅ **INDICE_DOCUMENTACION.md** - Tabla de contenidos central y guía de navegación
- ✅ **CHANGELOG.md** - Este archivo (historial de cambios)
- ✅ **Plan detallado** (`/plans/swirling-knitting-hickey.md`) - 6 Sprints, arquitectura, análisis costos (APROBADO)
- ✅ **Memory system** - Contexto del proyecto guardado para futuras conversaciones

### Cambios (Changed)
- N/A (primer release)

### Eliminado (Removed)
- N/A (primer release)

### Bugs Arreglados (Fixed)
- N/A (primer release)

### Deprecado (Deprecated)
- N/A (primer release)

### Seguridad (Security)
- Matriz de autenticación/autorización documentada (4 roles)
- Auditoría completa diseñada (tabla audit_logs)
- SII integration con secret management planeada

---

## [0.2] - 2026-04-05 (Mismo día - REVISIÓN DE COSTOS)

### Agregado
- ✅ **INFRAESTRUCTURA_ECONOMICA.md** - Replanteamiento completo de costos
  - VPS Hetzner self-hosted en lugar de GCP managed
  - Costo reducido: $125-185 USD/mes → $33.60 USD/mes
  - Aceptados trade-offs: Self-hosted + sin redundancia automática
  - Detalle: Setup, Nginx, Supervisor, backup strategy

### Cambios
- ✅ **README.md** - Actualizar costos a $33.60 USD/mes
- ✅ **PRESENTACION.md** - Actualizar análisis ROI con nuevos costos
- ✅ **RESUMEN_ENTREGA.md** - Actualizar tabla de inversión
- ✅ **Plan detallado** - Actualizar sección 6 de costos
- ✅ **INDICE_DOCUMENTACION.md** - Agregar nuevo doc INFRAESTRUCTURA_ECONOMICA.md

### Decisiones Confirmadas
- ✅ Hetzner CX31 como VPS principal
- ✅ PostgreSQL + Redis self-hosted en VPS
- ✅ Nginx como reverse proxy + SSL via Cloudflare
- ✅ Backup a B2 (10GB gratis/mes)
- ✅ Allan responsable de DevOps inicial
- ✅ Payback period sigue siendo 2-3 meses

---

## [0.3] - ⏳ TBD (Después de reunión martes 9 abril)

### Planeado Agregar
- [ ] **docs/hardware/** - Especificaciones exactas de scanner, balanza, caja (post-reunión)
- [ ] **docs/hardware/scanner.md** - Marca, modelo, protocolo, SDK
- [ ] **docs/hardware/balanza.md** - Especificaciones técnicas balanza 4 estaciones
- [ ] **docs/hardware/caja_pos.md** - Sistema POS actual, specs, integración
- [ ] Actualización **ARQUITECTURA.md** - Diagrama físico de hardware en local
- [ ] Actualización **PROXIMOS_PASOS.md** - Confirmaciones post-martes

### Planeado Cambiar
- [ ] MODELO_DATOS.md - Posibles ajustes si hardware requiere campos adicionales
- [ ] PROXIMOS_PASOS.md - Actualizar con decisiones post-reunión

---

## [0.3] - ⏳ TBD (Sprint 0 - Semana del 14 abril)

### Planeado Agregar
- [ ] **docs/api-reference/openapi.yml** - API specification auto-generada (FastAPI)
- [ ] **docs/onboarding/dev-setup.md** - Setup ambiente de desarrollo local
- [ ] **docs/onboarding/env-variables.md** - Variables de entorno necesarias
- [ ] **docs/onboarding/first-run.md** - Primer run del proyecto
- [ ] **ARQUITECTURA.md** - Actualizar con decisiones finales post-hardware

### Planeado Cambiar
- [ ] Plan detallado - Ajustes basados en reunión martes

---

## [0.4-1.0] - ⏳ TBD (Sprints 1-6)

### Planeado Agregar por Sprint
- [ ] **docs/runbooks/deploy.md** - Procedimiento de deployment a producción
- [ ] **docs/runbooks/backup.md** - Estrategia de backup y recovery
- [ ] **docs/runbooks/troubleshooting.md** - Guía de troubleshooting operacional
- [ ] **docs/runbooks/oncall.md** - Procedimientos de on-call
- [ ] **API_REFERENCE.md** - Documentación completa de todos los endpoints
- [ ] **RELEASE_NOTES.md** - Notas de cada release
- [ ] **presentacion.pptx** - PPT ejecutiva (Sprint 6)

### Planeado Cambiar
- [ ] Toda la documentación será versionada y actualizada con cambios en arquitectura/decisiones

---

## Estructura de Versiones

```
0.1 → Documentación base + Plan aprobado
0.2 → Specs hardware confirmadas
0.3 → Sprint 0 completado (infra funcional)
0.4-0.9 → Sprints 1-5 (features)
1.0 → MVP en producción (Sprint 6 completado)
```

---

## Notas Importantes

### Como Actualizar Este Archivo
1. Cada cambio importante → Agregar línea a sección correspondiente
2. Al finalizar sprint → Crear nueva sección [X.Y]
3. Mantener formato Markdown claro
4. Incluir emojis para fácil escaneo

### Como Leer Este Archivo
- **Agregado:** Nuevos documentos, funcionalidades
- **Cambios:** Modificaciones a documentos existentes
- **Eliminado:** Documentos/funcionalidades removidas
- **Bugs Arreglados:** Correcciones
- **Deprecado:** Cosas que van a desaparecer pronto
- **Seguridad:** Cambios relacionados a seguridad

### Responsables por Sección
- **Plan:** Giuliano (PM)
- **Arquitectura/Backend:** Allan
- **Frontend/UX:** Jonathan
- **Operacional/Runbooks:** Todo el equipo

---

## Historial de Decisiones

### 5 de Abril 2026
✅ **Decisión:** Usar WebSocket para sincronización en tiempo real (vs polling HTTP)  
✅ **Decisión:** PostgreSQL como BD principal (vs MongoDB/NoSQL)  
✅ **Decisión:** GCP Cloud Run como infraestructura (vs EC2/K8s)  
✅ **Decisión:** Vue 3 + FastAPI como stack principal  
✅ **Decisión:** n8n + Metabase para automatización y analytics  

### 9 de Abril 2026 (Post-Reunión Hardware)
⏳ **Decisión pendiente:** Confirmar protocolo de integración con balanza/scanner  
⏳ **Decisión pendiente:** Seleccionar proveedor SII (Bsale vs Acepta)  
⏳ **Decisión pendiente:** Arquitectura de pantallas (¿cuántas y dónde?)  

---

## Estado Actual

| Componente | Status | Nota |
|-----------|--------|------|
| Plan arquitectónico | ✅ Aprobado | Listo para implementación |
| Documentación base | ✅ Completada | 5 documentos + plan |
| Especificaciones hardware | ⏳ Pendiente | Reunión martes 9 abril |
| GCP setup | ⏳ Pendiente | Sprint 0 (semana 14-18 abril) |
| Repos GitHub | ⏳ Pendiente | Sprint 0 |
| Dev environment | ⏳ Pendiente | Sprint 0 |
| API Reference | ⏳ Pendiente | Sprint 0 |

---

## Próximos Hitos Críticos

1. **9 de abril** - Reunión hardware (recopilación specs)
2. **10 de abril** - Revisión técnica post-hardware
3. **11 de abril** - Preparación Sprint 0 (repos, infra)
4. **14 de abril** - Sprint 0 inicia (infra en vivo)
5. **18 de abril** - Sprint 0 termina
6. **21 de abril** - Sprint 1 inicia

---

**Versión del Changelog:** 0.1  
**Última actualización:** 5 de abril 2026  
**Próxima revisión:** 9 de abril 2026 (post-reunión hardware)
