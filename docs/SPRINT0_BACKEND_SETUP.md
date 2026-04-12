# Sprint 0 — Setup Backend Local con Docker
## Sistema de Inventario Dinámico - Locales Comerciales Chile

**Fecha:** 12 de abril de 2026
**Responsable:** Allan (Backend)
**Estado:** Completado

---

## Contexto

El skeleton del backend fue completado en el commit `b708560` (Sprint 0). Este documento registra
el proceso de levantar el entorno Docker local por primera vez, incluyendo los problemas encontrados,
cómo se resolvieron, y el estado final del sistema.

---

## Archivos Creados / Modificados

### Nuevos archivos

| Archivo | Descripción |
|---------|-------------|
| `comerciales-backend/docker-compose.yml` | Orquestación completa: 6 servicios (db, redis, api, worker, beat, flower) |
| `comerciales-backend/.env` | Variables de entorno para desarrollo local (NO commitear a git) |

### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `alembic/versions/1c293d396139_initial.py` | Fix bug de SQLAlchemy 2.x en creación de ENUMs (ver sección Bug) |

---

## Docker Compose — Servicios

```yaml
# Resumen de la configuración final
services:
  db:      postgres:15-alpine  — puerto 5432
  redis:   redis:7-alpine      — puerto 6379
  api:     comerciales-backend — puerto 8000 (FastAPI + uvicorn --reload)
  worker:  comerciales-backend — celery worker (concurrency=2)
  beat:    comerciales-backend — celery beat (tareas programadas)
  flower:  comerciales-backend — puerto 5555 (monitor visual de tareas)
```

**Healthchecks configurados** en `db` y `redis` — los servicios `api`, `worker` y `beat`
esperan que ambos estén healthy antes de iniciar.

**Volumen persistente:** `postgres_data` — los datos de PostgreSQL sobreviven reinicios del contenedor.

---

## Variables de Entorno (`.env` local)

El archivo `.env` apunta a los nombres de servicio Docker (no `localhost`):

```env
DATABASE_URL=postgresql://comerciales:comerciales_dev@db:5432/comerciales
REDIS_URL=redis://redis:6379/0
```

> Si se conecta desde fuera del contenedor (pgAdmin, DBeaver, etc.), usar `localhost:5432`.

El `.env` está incluido en `.gitignore` — **nunca subir credenciales al repo**.

---

## Problemas Encontrados y Soluciones

### 1. Docker Desktop no podía iniciar — faltaba kernel WSL2

**Error:** `Error response from daemon: Docker Desktop is unable to start`

**Causa:** El kernel de WSL2 no estaba instalado en el sistema. Docker Desktop en Windows 10
usa WSL2 como backend de virtualización.

**Solución:**
```bash
wsl --update
```
Reiniciar Docker Desktop después del update.

---

### 2. Bug crítico — Alembic migration fallaba con `DuplicateObject`

**Error:**
```
psycopg2.errors.DuplicateObject: type "user_role" already exists
```

**Causa:** En SQLAlchemy 2.x, `sa.Enum("val1", "val2", ..., name="tipo", create_type=False)`
no respeta completamente `create_type=False` cuando se llama desde el evento `_on_table_create`.
La migración creaba el ENUM manualmente con `op.execute("CREATE TYPE ...")` y luego
`op.create_table()` intentaba crearlo de nuevo.

**Solución:** Reemplazar todas las columnas enum en `create_table` con `postgresql.ENUM(name=..., create_type=False)` — referencia por nombre sin valores posicionales:

```python
# ANTES (buggy con SQLAlchemy 2.x)
sa.Column("rol", sa.Enum("admin", "cajero", name="user_role", create_type=False), ...)

# DESPUÉS (correcto)
sa.Column("rol", postgresql.ENUM(name="user_role", create_type=False), ...)
```

Afectaba las 7 columnas enum de la migración inicial:
`user_role`, `station_type`, `unidad_type`, `preboleta_estado`, `metodo_pago`, `tipo_dte`, `dte_estado`

---

## Estado Final — Validación

### Contenedores
```
NAME                         IMAGE                   STATUS
comerciales-backend-api-1    comerciales-backend-api Up — 0.0.0.0:8000->8000/tcp
comerciales-backend-beat-1   comerciales-backend-beat Up
comerciales-backend-db-1     postgres:15-alpine      Up (healthy) — 0.0.0.0:5432->5432/tcp
comerciales-backend-flower-1 comerciales-backend-flower Up — 0.0.0.0:5555->5555/tcp
comerciales-backend-redis-1  redis:7-alpine          Up (healthy) — 0.0.0.0:6379->6379/tcp
comerciales-backend-worker-1 comerciales-backend-worker Up
```

### Base de Datos — 12 tablas creadas
```
alembic_version   categories       daily_reports    dte_transactions
preboleta_audits  preboleta_items  preboletas       products
sale_items        sales            stations         users
```

### API
```
GET http://localhost:8000/health  → {"status": "ok"}
GET http://localhost:8000/docs    → HTTP 200 (Swagger UI)
GET http://localhost:5555         → Flower (monitor Celery)
```

---

## Comandos de Referencia

```bash
# Desde comerciales-backend/

# Levantar todo
docker compose up -d

# Ver estado
docker compose ps

# Ver logs en tiempo real
docker compose logs -f api
docker compose logs -f worker

# Correr migraciones
docker compose exec api alembic upgrade head

# Acceder a PostgreSQL
docker compose exec db psql -U comerciales

# Detener todo
docker compose down

# Detener y borrar volúmenes (reset completo de DB)
docker compose down -v
```

---

**Próxima acción:** Ver [BACKEND_PROXIMOS_PASOS.md](BACKEND_PROXIMOS_PASOS.md)
