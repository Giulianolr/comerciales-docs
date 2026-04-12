# Backend — Próximos Pasos
## Sistema de Inventario Dinámico - Locales Comerciales Chile

**Fecha:** 12 de abril de 2026
**Responsable:** Allan (Backend)
**Estado del backend:** Stack corriendo localmente — skeleton validado

---

## Estado Actual

| Item | Estado |
|------|--------|
| Docker compose (6 servicios) | Completado |
| 11 modelos SQLAlchemy | Completado |
| Migración Alembic inicial | Completado |
| Celery Beat (3 tareas programadas) | Completado |
| Routers preboleta (WF03) e invoices (WF05/06) | Completado |
| Autenticación JWT | Pendiente |
| Tests | Pendiente |
| GitHub Actions CI | Pendiente |
| Seed de datos dev | Pendiente |

---

## Paso 1 — Autenticación JWT

**Prioridad: ALTA — Desbloqueante para todo lo demás**

Sin auth ningún endpoint está protegido. Jonathan no puede integrar el frontend con sesiones reales.

### Qué implementar

```
POST /auth/login          → recibe email+password, devuelve access_token
GET  /auth/me             → devuelve usuario autenticado (requiere token)
```

```python
# Dependencia a agregar en todos los routers protegidos
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    ...
```

### Archivos a crear / modificar
- `app/core/security.py` — lógica JWT (crear/verificar tokens con `python-jose`)
- `app/routers/auth.py` — endpoints de login y me
- `app/routers/preboleta.py` — agregar `Depends(get_current_user)`
- `app/routers/invoices.py` — agregar `Depends(get_current_user)`
- `app/main.py` — registrar router de auth

### Notas técnicas
- Usar `passlib[bcrypt]` para hashear passwords (ya en `requirements.txt`)
- Token tipo `Bearer`, expiración sugerida: 8 horas (un turno de trabajo)
- El modelo `User` ya tiene `hashed_password` y `rol` en la DB

---

## Paso 2 — Tests con base de datos real

**Prioridad: ALTA**

No existe ningún test. Sin tests, cualquier refactor puede romper silenciosamente los flujos
críticos (preboleta, venta, DTE).

### Qué implementar

```
tests/
├── conftest.py           — fixture que levanta DB de test y cliente FastAPI
├── test_auth.py          — login válido, login inválido, token expirado
├── test_preboleta.py     — crear, consultar, expirar preboleta
└── test_health.py        — smoke test del /health
```

### Estrategia
- Usar la misma DB PostgreSQL del contenedor con una base de datos separada: `comerciales_test`
- `pytest` + `httpx.AsyncClient` para llamadas a la API
- Fixture de `conftest.py` crea las tablas antes y las limpia después de cada test

### Comando
```bash
docker compose exec api pytest tests/ -v
```

---

## Paso 3 — GitHub Actions CI

**Prioridad: MEDIA**

El pipeline de CI planeado en Sprint 0 aún no existe. Sin él, los errores solo se descubren
en producción.

### Workflow mínimo viable

```yaml
# .github/workflows/ci.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres: postgres:15
      redis: redis:7
    steps:
      - pytest tests/ -v
  build:
    docker build .
```

### Qué cubre
- Corre tests automáticamente en cada push a `main` o `develop`
- Verifica que el Dockerfile construye sin errores
- Bloquea merge de PRs con tests rotos

---

## Paso 4 — Seed de datos para desarrollo

**Prioridad: MEDIA — Desbloqueante para Jonathan**

La DB está vacía. Sin datos Jonathan no puede testear la UI contra endpoints reales.

### Qué crear

```
scripts/seed.py
```

Con datos mínimos funcionales:
- 1 usuario admin + 1 cajero + 1 operador de balanza
- 4 estaciones (2 balanzas + 2 cajas)
- 20-30 productos representativos (con stock, precios, categorías)
- 5 preboletas en distintos estados

### Comando
```bash
docker compose exec api python scripts/seed.py
```

---

## Paso 5 — Verificar `.gitignore` del `.env`

**Prioridad: ALTA (seguridad)**

El archivo `.env` con credenciales locales no debe llegar al repositorio.

### Verificar
```bash
cat .gitignore | grep .env
git status  # confirmar que .env aparece como untracked, no como staged
```

Si no está ignorado:
```bash
echo ".env" >> .gitignore
```

---

## Orden de ejecución recomendado

```
Paso 5 (seguridad)  →  Paso 1 (auth)  →  Paso 2 (tests)  →  Paso 3 (CI)  →  Paso 4 (seed)
  [inmediato]           [1-2 días]         [1 día]            [medio día]      [medio día]
```

El paso 5 se puede hacer en 5 minutos y evita un accidente de seguridad.
El paso 1 desbloquea el trabajo de Jonathan en frontend.
Los pasos 2, 3 y 4 dan estabilidad al desarrollo continuo.

---

## Referencia

- Setup Docker completado: [SPRINT0_BACKEND_SETUP.md](SPRINT0_BACKEND_SETUP.md)
- Arquitectura general: [ARQUITECTURA.md](ARQUITECTURA.md)
- Modelo de datos: [MODELO_DATOS.md](MODELO_DATOS.md)
