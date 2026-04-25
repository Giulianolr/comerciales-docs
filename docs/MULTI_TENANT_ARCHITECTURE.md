# ARQUITECTURA MULTI-TENANT
## Diseño de BD y backend para múltiples locales (SaaS)

**Versión:** 1.0  
**Para:** Allan (Backend) + Jonathan (Frontend)  
**Modelo:** Un dominio (comerciales.cl), múltiples locales, una BD compartida

---

## 🏗️ CONCEPTO GENERAL

```
1 Dominio:           comerciales.cl
│
├─ 1 Base de datos:  comerciales_db
│  ├─ Tabla users (con campo local_id)
│  ├─ Tabla locals (información de cada local)
│  ├─ Tabla products (con local_id)
│  ├─ Tabla transactions (con local_id)
│  ├─ Tabla inventory (con local_id)
│  └─ Tabla invoices (con local_id)
│
├─ 1 Backend:        FastAPI
│  └─ Middleware: filtra por local_id del JWT token
│
├─ 1 Frontend:       Vue 3 build estático
│  └─ Selector de local en login
│
└─ N Locales:        1, 2, 3, ... 10+
   └─ Cada uno con datos aislados pero en la misma BD
```

---

## 📊 ESQUEMA DE BD

### 1. Tabla `locals` (información de cada local)
```sql
CREATE TABLE locals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,                 -- "Local Centro"
    rut VARCHAR(12) NOT NULL UNIQUE,            -- RUT del local
    city VARCHAR(100),
    address TEXT,
    phone VARCHAR(20),
    bsale_account_id VARCHAR(50),               -- Para facturación
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Ejemplo de datos:
INSERT INTO locals (name, rut, city, address, bsale_account_id) VALUES
('Local Plaza Centro', '11.111.111-1', 'Santiago', 'Calle Principal 123', 'BSALE_001'),
('Local Mall Costanera', '22.222.222-2', 'Santiago', 'Av. Costanera 456', 'BSALE_002');
```

### 2. Tabla `users` (usuarios con local_id)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    local_id INTEGER NOT NULL REFERENCES locals(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role ENUM('admin', 'manager', 'cashier', 'scale_operator') DEFAULT 'cashier',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Índice para búsquedas rápidas
CREATE INDEX idx_users_local_id ON users(local_id);
CREATE INDEX idx_users_email ON users(email);

-- Ejemplo:
INSERT INTO users (local_id, email, password_hash, full_name, role) VALUES
(1, 'gerente1@local-centro.cl', 'hash_password', 'Juan García', 'manager'),
(2, 'gerente2@local-costanera.cl', 'hash_password', 'María López', 'manager');
```

### 3. Tabla `products` (productos por local)
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    local_id INTEGER NOT NULL REFERENCES locals(id) ON DELETE CASCADE,
    sku VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price_cost DECIMAL(10,2),
    price_sale DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    unit_measure VARCHAR(20),                   -- kg, L, unidad, etc
    stock_current DECIMAL(10,3),
    stock_min DECIMAL(10,3),
    stock_max DECIMAL(10,3),
    barcode VARCHAR(50),
    supplier_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Índices
CREATE INDEX idx_products_local_id ON products(local_id);
CREATE INDEX idx_products_sku ON products(local_id, sku);
CREATE INDEX idx_products_barcode ON products(local_id, barcode);

-- Ejemplo:
INSERT INTO products (local_id, sku, name, price_sale, category, stock_current, barcode) VALUES
(1, 'PROD001', 'Leche Entera', 3500, 'Lácteos', 50, '7701234567890'),
(1, 'PROD002', 'Pan Francés', 2500, 'Panadería', 120, '7701234567891');
```

### 4. Tabla `transactions` (ventas)
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    local_id INTEGER NOT NULL REFERENCES locals(id) ON DELETE CASCADE,
    invoice_id VARCHAR(50),                     -- Número de factura SII
    user_id INTEGER REFERENCES users(id),
    transaction_date TIMESTAMP NOT NULL,
    total_amount DECIMAL(12,2),
    payment_method VARCHAR(50),                -- efectivo, tarjeta, cheque
    notes TEXT,
    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_transactions_local_id ON transactions(local_id);
CREATE INDEX idx_transactions_date ON transactions(local_id, transaction_date);
CREATE INDEX idx_transactions_invoice ON transactions(local_id, invoice_id);

-- Ejemplo:
INSERT INTO transactions (local_id, transaction_date, total_amount, payment_method, status) VALUES
(1, NOW(), 15000, 'efectivo', 'completed'),
(1, NOW(), 25000, 'tarjeta', 'completed');
```

### 5. Tabla `transaction_items` (detalles de transacción)
```sql
CREATE TABLE transaction_items (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity DECIMAL(10,3) NOT NULL,
    price_unit DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2)
);

-- Índice
CREATE INDEX idx_transaction_items_transaction ON transaction_items(transaction_id);

-- Ejemplo:
INSERT INTO transaction_items (transaction_id, product_id, quantity, price_unit, subtotal) VALUES
(1, 1, 2, 3500, 7000),   -- 2 litros de leche
(1, 2, 3, 2500, 7500);   -- 3 panes
```

### 6. Tabla `inventory_logs` (auditoría de inventario)
```sql
CREATE TABLE inventory_logs (
    id SERIAL PRIMARY KEY,
    local_id INTEGER NOT NULL REFERENCES locals(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    action VARCHAR(50),                        -- sale, adjustment, restock, waste
    quantity_change DECIMAL(10,3),
    reason TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índice
CREATE INDEX idx_inventory_logs_local_id ON inventory_logs(local_id);
CREATE INDEX idx_inventory_logs_product ON inventory_logs(product_id);
```

---

## 🔐 ARQUITECTURA DE SEGURIDAD: AISLAMIENTO POR LOCAL

### JWT Token Strategy
```python
# Cuando un usuario inicia sesión, el token JWT contiene:
{
    "sub": "user_id",
    "local_id": 1,          # ← CRÍTICO: local del usuario
    "role": "manager",
    "exp": 1713576000
}

# El backend SIEMPRE verifica que:
# 1. Token es válido
# 2. local_id en token = local_id en request
# 3. User tiene permisos en ese local
```

### Middleware de FastAPI
```python
# app/middleware/auth.py

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)):
    """Extrae y valida JWT, retorna user_id + local_id"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        local_id: int = payload.get("local_id")
        
        if user_id is None or local_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"user_id": user_id, "local_id": local_id}
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# En cada ruta, usar el middleware:
@app.get("/api/v1/products")
async def get_products(current_user = Depends(get_current_user)):
    """Retorna solo productos del local del usuario"""
    local_id = current_user["local_id"]
    
    # ← CRUCIAL: Filtrar por local_id
    products = db.query(Product).filter(
        Product.local_id == local_id  # Solo datos de su local
    ).all()
    
    return products
```

### Filtración de Queries
**REGLA DE ORO:** Toda query debe incluir `WHERE local_id = current_user.local_id`

```python
# ❌ NUNCA HAGAS ESTO (INSEGURO):
products = db.query(Product).all()  # Retorna productos de TODOS los locales

# ✅ SIEMPRE HAZ ESTO:
products = db.query(Product).filter(
    Product.local_id == current_user["local_id"]
).all()

# Ejemplo en transacciones:
transactions = db.query(Transaction).filter(
    Transaction.local_id == current_user["local_id"],
    Transaction.transaction_date >= start_date,
    Transaction.transaction_date <= end_date
).all()
```

---

## 🎯 FLUJOS PRINCIPALES

### Flujo 1: LOGIN
```
1. Usuario ingresa email + contraseña
2. Backend valida credenciales
3. Query: SELECT * FROM users WHERE email = ? AND is_active = true
4. Verifica local_id del usuario
5. Genera JWT con:
   - sub: user_id
   - local_id: local del usuario
6. Retorna token + info del local
7. Frontend guarda token en localStorage
```

### Flujo 2: VER PRODUCTOS
```
Frontend request:
GET /api/v1/products?category=Lácteos
Authorization: Bearer <JWT_TOKEN>

Backend:
1. Middleware extrae local_id del JWT
2. Query: SELECT * FROM products 
         WHERE local_id = {local_id} AND category = 'Lácteos'
3. Retorna solo productos de ese local
4. Frontend muestra productos
```

### Flujo 3: CREAR TRANSACCIÓN
```
Frontend POST /api/v1/transactions
{
    "items": [
        {"product_id": 1, "quantity": 2},
        {"product_id": 2, "quantity": 3}
    ],
    "payment_method": "efectivo"
}

Backend:
1. Extrae local_id del JWT
2. Valida que products existen en ese local
3. Inserta transaction:
   INSERT INTO transactions (local_id, ...) VALUES ({local_id}, ...)
4. Inserta transaction_items
5. ACTUALIZA inventario:
   UPDATE products SET stock_current = stock_current - quantity
   WHERE local_id = {local_id}
6. Retorna invoice_id para imprimir
```

### Flujo 4: ENVIAR A BSALE (Facturación)
```
Backend cuando transaction.status = 'completed':
1. Obtiene local_id de la transacción
2. Query: SELECT bsale_account_id FROM locals WHERE id = {local_id}
3. Crea documento en Bsale con esa cuenta
4. Retorna número de factura oficial SII
5. UPDATE transactions SET invoice_id = {numero_sii}
```

---

## 📋 CHECKLIST IMPLEMENTACIÓN BACKEND

### Models (ORM SQLAlchemy)
- [ ] Model `Local`
- [ ] Model `User` (con local_id FK)
- [ ] Model `Product` (con local_id FK)
- [ ] Model `Transaction` (con local_id FK)
- [ ] Model `TransactionItem`
- [ ] Model `InventoryLog` (con local_id FK)

### Routes (FastAPI)
- [ ] POST `/auth/login` → retorna JWT con local_id
- [ ] GET `/products?category=?` → filtra por local_id
- [ ] POST `/transactions` → inserta con local_id
- [ ] GET `/transactions?date_from=?&date_to=?` → filtra por local_id
- [ ] GET `/inventory/status` → stock por local
- [ ] POST `/invoices/send-bsale` → envía a Bsale de ese local

### Middleware
- [ ] Middleware `@requires_auth` → valida JWT + extrae local_id
- [ ] Middleware `@check_local_access` → verifica que user tenga acceso al local_id

### Security
- [ ] JWT token generation (con local_id)
- [ ] Password hashing (bcrypt)
- [ ] Rate limiting por endpoint
- [ ] CORS configurado correctamente

---

## 📋 CHECKLIST IMPLEMENTACIÓN FRONTEND

### Authentication
- [ ] Login form (email + password)
- [ ] Guardar JWT en localStorage
- [ ] Middleware HTTP: agregar JWT a todas las requests
- [ ] Logout: limpiar localStorage

### Dashboard
- [ ] Selector de local (si usuario tiene múltiples)
- [ ] Mostrar nombre del local activo
- [ ] Mostrar usuario logueado

### Vistas por Local
- [ ] Productos: mostrar solo del local actual
- [ ] Transacciones: filtrar por local actual
- [ ] Inventario: mostrar solo del local actual
- [ ] Reportes: rangos de fecha, local actual

### Error Handling
- [ ] 401 → redirect a login
- [ ] 403 → mostrar "No tienes acceso a este local"
- [ ] 500 → mostrar error genérico

---

## 🔍 VALIDACIÓN DE INTEGRIDAD

### Test 1: Aislamiento de datos
```bash
# Iniciar sesión como user del local 1
JWT_LOCAL_1="..."

# Intentar acceder a datos del local 2
curl -H "Authorization: Bearer $JWT_LOCAL_1" \
     https://comerciales.cl/api/v1/transactions?local_id=2
# Debería devolver 403 o lista vacía

# Intentar insertar en local 2
curl -X POST -H "Authorization: Bearer $JWT_LOCAL_1" \
     https://comerciales.cl/api/v1/transactions \
     -d '{"local_id": 2, ...}'
# Debería devolver 403
```

### Test 2: Conteo de transacciones por local
```sql
-- Verificar que transacciones están isoladas
SELECT local_id, COUNT(*) as total
FROM transactions
GROUP BY local_id;

-- Local 1: 100 transacciones
-- Local 2: 50 transacciones
-- Total BD: 150 transacciones (correcto)
```

### Test 3: Performance query
```sql
-- Con índice en local_id, esta query debe ser instant
EXPLAIN ANALYZE
SELECT * FROM transactions 
WHERE local_id = 1 AND transaction_date > '2026-04-01';

-- Plan: Index Scan usando idx_transactions_local_id
```

---

## 🚨 ERRORES COMUNES (EVITAR)

### ❌ Error 1: Olvidar filtrar por local_id
```python
# MAL
@app.get("/api/v1/products")
def get_products():
    return db.query(Product).all()  # ← RETORNA TODOS

# BIEN
@app.get("/api/v1/products")
def get_products(current_user = Depends(get_current_user)):
    return db.query(Product).filter(
        Product.local_id == current_user["local_id"]
    ).all()
```

### ❌ Error 2: Confiar en local_id del cliente
```python
# MAL
@app.post("/api/v1/transactions")
def create_transaction(req: TransactionRequest):
    local_id = req.local_id  # ← CLIENTE PUEDE MENTIR

# BIEN
@app.post("/api/v1/transactions")
def create_transaction(req: TransactionRequest, current_user = Depends(get_current_user)):
    local_id = current_user["local_id"]  # ← DEL JWT (seguro)
```

### ❌ Error 3: No validar producto pertenece al local
```python
# MAL
product = db.query(Product).filter(Product.id == req.product_id).first()
# Qué pasa si product.local_id != current_user["local_id"]?

# BIEN
product = db.query(Product).filter(
    Product.id == req.product_id,
    Product.local_id == current_user["local_id"]  # ← Verificar local
).first()
if not product:
    raise HTTPException(404, "Producto no encontrado")
```

---

## 📈 ESCALADO FUTURO

### Cuándo pasar a arquitectura por-tenant (DB separada):
- **Si:** >100 transacciones/día por local
- **Si:** Clientes quieren aislamiento legal de datos
- **Si:** Performance degrada significativamente

### Camino de migración (sin downtime):
1. Mantener BD compartida en paralelo
2. Nuevo tenant → crea BD separada
3. Clientes antiguos pueden migrar gradualmente
4. Desechar BD compartida cuando todos migren

---

## ✅ CHECKLIST DE REVIEW

Antes de ir a producción:

- [ ] Todas las queries filtran por local_id
- [ ] JWT contiene local_id
- [ ] Middleware valida token
- [ ] Requests sin token retornan 401
- [ ] Requests a otro local retornan 403
- [ ] Índices en local_id existen
- [ ] Tests de aislamiento pasan
- [ ] Performance queries < 100ms
- [ ] Logs incluyen local_id

---

**Próximo:** Implementar según este diseño en backend + frontend  
**Documentación relacionada:** VPS_SETUP.md, DEPLOYMENT.md
