# Resumen E2E Local Setup — Sistema de Inventario Dinámico

**Fecha**: 21 Abril 2026
**Objetivo**: Levantar un entorno E2E local completo (PostgreSQL, Redis, datos de prueba)

---

## 📦 Archivos Creados

### 1. **docker-compose.yml** (raíz del proyecto)
```yaml
- PostgreSQL 15 (puerto 5432)
- Redis 7 (puerto 6379)
- Volumes persistentes para datos
- Healthchecks configurados
```

**Uso**:
```bash
docker compose up -d      # Levantar
docker compose down       # Parar
docker compose logs -f    # Ver logs
```

---

### 2. **comerciales-backend/scripts/seed_db.py**
Script Python asincrónico que:
1. ✅ Ejecuta `alembic upgrade head` (crea esquema)
2. ✅ Crea **1 Admin** (dueño del store):
   - Email: `admin@omsai.cl`
   - Password: `admin123`
   - PIN: `0000`
   - Rol: `ADMIN`

3. ✅ Crea **1 Store**: "Sucursal Central"
   - RUT: 76123456-7
   - Dirección: Av. Principal 123, Santiago, Chile

4. ✅ Crea **1 Cajero** asociado al store:
   - Email: `cajero@omsai.cl`
   - Password: `123`
   - PIN: `1234`
   - Rol: `CAJERO`

5. ✅ Crea **2 Categorías**:
   - Quesos
   - Fiambres

6. ✅ Crea **5 Productos** reales:
   | Nombre | Categoría | Precio | Stock | Barcode |
   |--------|-----------|--------|-------|---------|
   | Queso Fresco Artesanal | Quesos | $8,500 | 50 kg | 7700001 |
   | Queso Gouda Importado | Quesos | $12,000 | 25 kg | 7700002 |
   | Jamón Serrano Premium | Fiambres | $15,000 | 15 kg | 7700003 |
   | Pechuga de Pavo | Fiambres | $9,500 | 40 kg | 7700004 |
   | Salami Picante | Fiambres | $7,500 | 60 kg | 7700005 |

---

### 3. **scripts/setup-e2e.sh** (raíz del proyecto)
Script bash automatizado que:
1. Verifica Docker está disponible
2. Levanta contenedores con `docker compose up -d`
3. Espera a que PostgreSQL esté listo (max 60s)
4. Instala dependencias del backend si es necesario
5. Ejecuta seed_db.py
6. Muestra resumen con credenciales

**Uso**:
```bash
bash scripts/setup-e2e.sh
```

---

### 4. **scripts/README_E2E.md**
Documentación completa con:
- Instrucciones paso a paso (manual y automático)
- Credenciales de acceso
- Datos de prueba creados
- Comandos útiles de troubleshooting
- Verificación de que todo funciona

---

## 🚀 Quick Start

### En tu máquina LOCAL (con Docker):

```bash
# 1. Levantar todo automáticamente
bash scripts/setup-e2e.sh

# ó hacerlo manualmente:

# 1. Levantar contenedores
docker compose up -d

# 2. Esperar a que PostgreSQL esté listo
docker exec comerciales-postgres pg_isready -U comerciales -d comerciales

# 3. Instalar dependencias
cd comerciales-backend
python3 -m pip install -e .

# 4. Poblar BD
python3 -m scripts.seed_db
```

---

## 📊 Credenciales Finales

### Base de Datos
```
Host:     localhost
Puerto:   5432
Usuario:  comerciales
Password: comerciales2026
Database: comerciales
```

### Admin
```
Email:    admin@omsai.cl
Password: admin123
PIN:      0000
Rol:      ADMIN
```

### Cajero
```
Email:    cajero@omsai.cl
Password: 123
PIN:      1234
Rol:      CAJERO
Store:    Sucursal Central
```

---

## 🔗 Verificación Post-Setup

```bash
# 1. Conectar a PostgreSQL
psql -h localhost -U comerciales -d comerciales
# Contraseña: comerciales2026

# 2. Listar tablas
\dt

# 3. Ver datos creados
SELECT COUNT(*) FROM stores;      -- Debería ser 1
SELECT COUNT(*) FROM users;       -- Debería ser 2
SELECT COUNT(*) FROM products;    -- Debería ser 5
SELECT COUNT(*) FROM categories;  -- Debería ser 2

# 4. Verificar Redis
redis-cli ping                     -- Debería responder: PONG
```

---

## 🛑 Parar el Entorno

```bash
# Detener contenedores (preserva datos)
docker compose down

# Detener y eliminar volúmenes (borra datos)
docker compose down -v
```

---

## 📝 Notas Técnicas

### Migraciones Alembic
- Ubicación: `comerciales-backend/alembic/versions/`
- Migración actual: `001_initial_schema.py`
- Comando: `alembic upgrade head`

### Modelos SQLAlchemy
- Base ORM: `app/models/base.py`
- Core models: `app/models/core.py` (Store, User, Category, Product)
- Transaction models: `app/models/transaction.py`
- All imports in: `app/models/models.py`

### Database Configuration
- URL: `postgresql+asyncpg://comerciales:comerciales2026@localhost:5432/comerciales`
- Config file: `app/core/database.py`
- Async engine con pool_size=10, max_overflow=20

### Security
- Hash function: `app/core/security.py` → `hash_password()`
- Algorithm: bcrypt (via passlib)
- JWT ready (imported in security.py)

---

## ✅ Checklist Post-Setup

- [ ] Docker compose levantó PostgreSQL (puerto 5432)
- [ ] Docker compose levantó Redis (puerto 6379)
- [ ] Migraciones Alembic se ejecutaron
- [ ] Store "Sucursal Central" creado
- [ ] Admin user creado (admin@omsai.cl)
- [ ] Cajero user creado (cajero@omsai.cl)
- [ ] 5 productos creados con categorías
- [ ] Datos persistentes en volumen PostgreSQL
- [ ] `psql` conecta exitosamente
- [ ] `redis-cli ping` responde PONG

---

## 🎯 Próximos Pasos

1. **Levantar FastAPI Backend**:
   ```bash
   cd comerciales-backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Levantar Frontend React**:
   ```bash
   cd comerciales-frontend
   npm run dev    # ó similar según configuración
   ```

3. **Probar flujo de Caja**:
   - Login: `cajero@omsai.cl` / `123`
   - PIN: `1234`
   - Ver productos, registrar transacciones

4. **Integración E2E**:
   - Backend en puerto 8000
   - Frontend en puerto 3000 (típico)
   - Redis en puerto 6379 (caché)
   - PostgreSQL en puerto 5432 (persistencia)

