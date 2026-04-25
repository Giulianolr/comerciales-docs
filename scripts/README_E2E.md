# Setup E2E Local - Sistema de Inventario Dinámico

Este documento describe cómo levantar el entorno E2E local con PostgreSQL, Redis y datos de prueba.

## Opción 1: Setup Automático (Recomendado)

Ejecuta el script en tu máquina local:

```bash
bash scripts/setup-e2e.sh
```

Este script:
1. ✅ Levanta PostgreSQL y Redis con `docker compose`
2. ✅ Espera a que PostgreSQL esté listo
3. ✅ Instala dependencias si es necesario
4. ✅ Ejecuta migraciones Alembic
5. ✅ Popula la BD con datos de prueba

---

## Opción 2: Setup Manual Paso a Paso

Si prefieres hacerlo manualmente o el script no funciona:

### Paso 1: Levantar Contenedores

```bash
docker compose up -d
```

Verifica que ambos estén corriendo:
```bash
docker compose ps
```

Deberías ver:
- ✅ `comerciales-postgres` corriendo en puerto 5432
- ✅ `comerciales-redis` corriendo en puerto 6379

### Paso 2: Esperar a que PostgreSQL esté Listo

```bash
# Verifica la salud del contenedor
docker exec comerciales-postgres pg_isready -U comerciales -d comerciales
```

Cuando veas `accepting connections`, PostgreSQL está listo.

### Paso 3: Instalar Dependencias del Backend

```bash
cd comerciales-backend
python3 -m pip install -e .
```

### Paso 4: Ejecutar Seed Script

```bash
cd comerciales-backend
python3 -m scripts.seed_db
```

Este script:
1. Ejecuta `alembic upgrade head` (crea tablas)
2. Crea un Store: "Sucursal Central"
3. Crea un User Admin: `admin@omsai.cl` / `admin123`
4. Crea un User Cajero: `cajero@omsai.cl` / `123` (PIN: 1234)
5. Crea 2 categorías: Quesos, Fiambres
6. Crea 5 productos reales (quesos y fiambres)

---

## Verificar que Todo Funciona

### 1. Conectar a PostgreSQL

```bash
psql -h localhost -U comerciales -d comerciales
```

Cuando te pida contraseña, ingresa: `comerciales2026`

Luego puedes listar las tablas:
```sql
\dt
```

### 2. Verificar Redis

```bash
redis-cli ping
```

Deberías ver: `PONG`

### 3. Verificar Datos en la BD

```sql
SELECT * FROM stores;
SELECT * FROM users;
SELECT * FROM products;
```

---

## Credenciales y Datos de Prueba

### BD PostgreSQL
- **Host**: localhost
- **Puerto**: 5432
- **Usuario**: comerciales
- **Contraseña**: comerciales2026
- **Database**: comerciales

### Usuarios Creados

| Email | Contraseña | PIN | Rol | Store |
|-------|-----------|-----|-----|-------|
| admin@omsai.cl | admin123 | 0000 | ADMIN | (N/A) |
| cajero@omsai.cl | 123 | 1234 | CAJERO | Sucursal Central |

### Productos Creados

| Nombre | Categoría | Precio | Stock | Barcode |
|--------|-----------|--------|-------|---------|
| Queso Fresco Artesanal | Quesos | $8,500 | 50 kg | 7700001 |
| Queso Gouda Importado | Quesos | $12,000 | 25 kg | 7700002 |
| Jamón Serrano Premium | Fiambres | $15,000 | 15 kg | 7700003 |
| Pechuga de Pavo | Fiambres | $9,500 | 40 kg | 7700004 |
| Salami Picante | Fiambres | $7,500 | 60 kg | 7700005 |

---

## Parar el Entorno

Cuando termines de desarrollar:

```bash
docker compose down
```

Para borrar también los volúmenes (datos):
```bash
docker compose down -v
```

---

## Troubleshooting

### PostgreSQL no acepta conexiones

1. Verifica que el contenedor está corriendo:
   ```bash
   docker compose ps
   ```

2. Revisa los logs:
   ```bash
   docker compose logs postgres
   ```

3. Si necesitas reiniciar:
   ```bash
   docker compose restart postgres
   ```

### Error: "database does not exist"

La BD debería crearse automáticamente en el docker-compose.yml. Si no, conéctate al servidor:
```bash
psql -h localhost -U postgres
CREATE DATABASE comerciales;
```

### Script seed_db.py no funciona

1. Verifica que estás en el directorio `comerciales-backend`:
   ```bash
   pwd  # Deberías estar en .../comerciales-backend
   ```

2. Verifica que las dependencias están instaladas:
   ```bash
   python3 -c "import sqlalchemy; print('OK')"
   ```

3. Verifica que PostgreSQL está listo:
   ```bash
   psql -h localhost -U comerciales -d comerciales -c "SELECT 1"
   ```

---

## Siguiente Paso

Una vez que todo esté levantado:
1. Levanta el backend FastAPI: `uvicorn app.main:app --reload`
2. Levanta el frontend: `cd ../frontend-code && npm run dev`
3. Abre http://localhost:3000 en tu navegador
