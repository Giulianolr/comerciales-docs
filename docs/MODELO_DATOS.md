# MODELO DE DATOS
## Sistema de Inventario Dinámico - Locales Comerciales Chile

**Para:** Equipo técnico + PM  
**Versión:** 0.1-MVP  
**Base de datos:** PostgreSQL 15 (Cloud SQL)  

---

## 📊 Diagrama ER (Entity-Relationship)

```sql
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CORE INVENTORY MANAGEMENT                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐                      ┌──────────────┐                     │
│  │   USERS      │                      │   STORES     │                     │
│  ├──────────────┤                      ├──────────────┤                     │
│  │ id (PK)      │                      │ id (PK)      │                     │
│  │ name         │                      │ name         │                     │
│  │ email        │◄─────────────────────│ owner_id (FK)│                     │
│  │ pin          │                      │ address      │                     │
│  │ role         │                      │ phone        │                     │
│  │ password     │                      │ sii_info     │                     │
│  │ created_at   │                      │ created_at   │                     │
│  │ updated_at   │                      │ updated_at   │                     │
│  └──────────────┘                      └──────────────┘                     │
│         ▲                                     │                              │
│         │ (ADMIN, GERENTE, CAJERO, OPERADOR) │                              │
│         │                                     │                              │
│  ┌──────┴──────────────────────────────────────┴───────┐                    │
│  │                                                      │                    │
│  ┌──────────────────┐         ┌──────────────────┐     │                    │
│  │   CATEGORIES     │         │   PRODUCTS       │     │                    │
│  ├──────────────────┤         ├──────────────────┤     │                    │
│  │ id (PK)          │◄────────│ id (PK)          │     │                    │
│  │ store_id (FK)    │         │ store_id (FK)    │     │                    │
│  │ name             │         │ barcode (UNIQUE) │     │                    │
│  │ description      │         │ name             │     │                    │
│  │ created_at       │         │ category_id (FK) │     │                    │
│  └──────────────────┘         │ unit (kg/unit)   │     │                    │
│                                │ price            │     │                    │
│                                │ stock_quantity   │     │                    │
│                                │ min_stock        │     │                    │
│                                │ created_at       │     │                    │
│                                │ updated_at       │     │                    │
│                                └──────────────────┘     │                    │
│                                       ▲                 │                    │
│                                       │                 │                    │
│  ┌──────────────────┐     ┌───────────┴───────────┐    │                    │
│  │   STATIONS       │     │  ORDER PROCESSING     │    │                    │
│  ├──────────────────┤     ├───────────────────────┤    │                    │
│  │ id (PK)          │     │                       │    │                    │
│  │ store_id (FK)    │─┐   │                       │    │                    │
│  │ number (1-4)     │ │   │                       │    │                    │
│  │ status           │ │   │                       │    │                    │
│  │ current_order_id │ │   │  ┌──────────────────┐│   │                    │
│  │ created_at       │ │   │  │     ORDERS       ││   │                    │
│  └──────────────────┘ │   │  ├──────────────────┤│   │                    │
│                       │   │  │ id (PK)          ││   │                    │
│                       └─► │  │ uuid (UNIQUE)    ││   │                    │
│                           │  │ store_id (FK)    ││   │                    │
│                           │  │ station_id (FK)  ││   │                    │
│                           │  │ status (PENDING,││   │                    │
│                           │  │    CONFIRMED)    ││   │                    │
│                           │  │ total            ││   │                    │
│                           │  │ created_at       ││   │                    │
│                           │  └──────────────────┘│   │                    │
│                           │         │             │    │                    │
│                           │  ┌──────▼──────────┐│   │                    │
│                           │  │  ORDER_ITEMS    ││   │                    │
│                           │  ├──────────────────┤│   │                    │
│                           │  │ id (PK)          ││   │                    │
│                           │  │ order_id (FK)    ││   │                    │
│                           │  │ product_id (FK)  ├┘   │                    │
│                           │  │ quantity         │    │                    │
│                           │  │ unit_price       │    │                    │
│                           │  │ unit (kg/unit)   │    │                    │
│                           │  │ subtotal         │    │                    │
│                           │  │ created_at       │    │                    │
│                           │  └──────────────────┘    │                    │
│                           │                          │                    │
│                           └──────────────────────────┘                    │
│                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────────────┐               │
│  │  TRANSACTIONS        │  │  BOLETAS (SII DTE)           │               │
│  ├──────────────────────┤  ├──────────────────────────────┤               │
│  │ id (PK)              │  │ id (PK)                      │               │
│  │ order_id (FK)────────┼─►│ transaction_id (FK)          │               │
│  │ store_id (FK)        │  │ folio_sii (from SII)         │               │
│  │ user_id (FK)         │  │ xml_dte (full XML content)   │               │
│  │ payment_method       │  │ status (PENDING, EMITTED,    │               │
│  │   (cash/card/         │  │        FAILED)               │               │
│  │    transfer)         │  │ timestamp_sii                │               │
│  │ amount_paid          │  │ created_at                   │               │
│  │ timestamp            │  │ updated_at                   │               │
│  │ created_at           │  └──────────────────────────────┘               │
│  └──────────────────────┘                                                  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────┐                  │
│  │  INVENTORY_MOVEMENTS (AUDIT LOG)                     │                  │
│  ├──────────────────────────────────────────────────────┤                  │
│  │ id (PK)                                              │                  │
│  │ product_id (FK) ◄──────────────────────┐             │                  │
│  │ transaction_id (FK) [nullable]         │             │                  │
│  │ type (SALE, ADJUSTMENT, RESTOCK)       │             │                  │
│  │ quantity_before                        │             │                  │
│  │ quantity_after                         │             │                  │
│  │ delta (-X, +X)                         │             │                  │
│  │ reason (description)                   │             │                  │
│  │ user_id (FK)                           │             │                  │
│  │ timestamp                              │             │                  │
│  └──────────────────────────────────────────────────────┘                  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────┐                  │
│  │  AUDIT_LOGS (SISTEMA - quién hizo qué y cuándo)     │                  │
│  ├──────────────────────────────────────────────────────┤                  │
│  │ id (PK)                                              │                  │
│  │ user_id (FK)                                         │                  │
│  │ action (LOGIN, LOGOUT, CREATE, UPDATE, DELETE, etc) │                  │
│  │ entity_type (products, transactions, users, etc)    │                  │
│  │ entity_id                                            │                  │
│  │ old_values (JSON - para updates)                     │                  │
│  │ new_values (JSON - para updates)                     │                  │
│  │ ip_address                                           │                  │
│  │ timestamp                                            │                  │
│  └──────────────────────────────────────────────────────┘                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

RELACIONES:
• 1 STORE → múltiples USERS
• 1 STORE → múltiples CATEGORIES
• 1 STORE → múltiples PRODUCTS
• 1 STORE → múltiples STATIONS (4 máximo)
• 1 STATION → múltiples ORDERS (pre-órdenes)
• 1 ORDER → múltiples ORDER_ITEMS
• 1 ORDER → 1 TRANSACTION (al confirmar)
• 1 TRANSACTION → 1 BOLETA (al emitir)
• 1 PRODUCT → múltiples INVENTORY_MOVEMENTS (auditoría)
• Todas las tablas → AUDIT_LOGS (trazabilidad)
```

---

## 📋 Definición Detallada de Tablas

### 1. `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    pin VARCHAR(4) NOT NULL,  -- 4 dígitos para acceso rápido en caja
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt
    role VARCHAR(50) NOT NULL CHECK (role IN ('ADMIN', 'GERENTE', 'CAJERO', 'OPERADOR')),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX (store_id),
    INDEX (email),
    INDEX (role)
);
```

### 2. `stores`
```sql
CREATE TABLE stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_id UUID NOT NULL REFERENCES users(id),  -- Gerente/dueño
    address TEXT NOT NULL,
    phone VARCHAR(20),
    sii_rut VARCHAR(20),  -- RUT del local para SII
    sii_config JSONB,  -- {"provider": "bsale", "api_key": "...", "cert_path": "..."}
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX (owner_id),
    UNIQUE (sii_rut)
);
```

### 3. `categories`
```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX (store_id),
    UNIQUE (store_id, name)
);
```

### 4. `products`
```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(id),
    barcode VARCHAR(50) NOT NULL,  -- EAN-13 u otro formato
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id UUID NOT NULL REFERENCES categories(id),
    unit VARCHAR(20) NOT NULL CHECK (unit IN ('kg', 'unit', 'L', 'ml')),
    price DECIMAL(10, 2) NOT NULL CHECK (price > 0),
    stock_quantity DECIMAL(10, 3) NOT NULL DEFAULT 0,  -- 3 decimales para kg
    min_stock DECIMAL(10, 3) NOT NULL DEFAULT 0,  -- Nivel para alertas
    reorder_quantity DECIMAL(10, 3),  -- Cantidad a reabastecer
    supplier_id UUID REFERENCES suppliers(id),  -- Para futuro
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX (store_id),
    INDEX (barcode),
    INDEX (category_id),
    UNIQUE (store_id, barcode)  -- Barcode único por local
);
```

### 5. `stations`
```sql
CREATE TABLE stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(id),
    number INTEGER NOT NULL CHECK (number BETWEEN 1 AND 4),  -- 4 estaciones
    status VARCHAR(50) NOT NULL DEFAULT 'idle' 
        CHECK (status IN ('idle', 'active', 'maintenance')),
    current_order_id UUID REFERENCES orders(id),  -- Pre-orden activa
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX (store_id),
    UNIQUE (store_id, number)
);
```

### 6. `orders` (Pre-órdenes)
```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    uuid VARCHAR(36) NOT NULL UNIQUE,  -- UUID para QR (sin guiones)
    store_id UUID NOT NULL REFERENCES stores(id),
    station_id UUID NOT NULL REFERENCES stations(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'confirmed', 'cancelled')),
    total DECIMAL(10, 2) NOT NULL DEFAULT 0,
    item_count INTEGER DEFAULT 0,
    qr_code BYTEA,  -- PNG binario del código QR
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX (store_id),
    INDEX (station_id),
    INDEX (uuid),
    INDEX (created_at)
);
```

### 7. `order_items`
```sql
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity DECIMAL(10, 3) NOT NULL CHECK (quantity > 0),  -- kg o unidades
    unit_price DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL,  -- Copia del unit del producto (normalización)
    subtotal DECIMAL(10, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX (order_id),
    INDEX (product_id)
);
```

### 8. `transactions`
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id),
    store_id UUID NOT NULL REFERENCES stores(id),
    user_id UUID NOT NULL REFERENCES users(id),  -- Cajero que confirma
    payment_method VARCHAR(50) NOT NULL 
        CHECK (payment_method IN ('cash', 'debit_card', 'credit_card', 'transfer')),
    amount_paid DECIMAL(10, 2) NOT NULL,
    change_amount DECIMAL(10, 2),
    status VARCHAR(50) NOT NULL DEFAULT 'completed'
        CHECK (status IN ('completed', 'voided', 'refunded')),
    boleta_id UUID REFERENCES boletas(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX (store_id),
    INDEX (user_id),
    INDEX (order_id),
    INDEX (created_at),
    UNIQUE (order_id)  -- Una transacción por orden
);
```

### 9. `boletas` (Boletas SII DTE)
```sql
CREATE TABLE boletas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL UNIQUE REFERENCES transactions(id),
    folio_sii INTEGER,  -- Número asignado por SII
    xml_dte TEXT,  -- XML completo del DTE
    status VARCHAR(50) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'emitted', 'rejected', 'cancelled')),
    emission_timestamp TIMESTAMP,  -- Hora que SII procesó
    error_message TEXT,  -- Si rejected, motivo
    provider VARCHAR(50),  -- 'bsale', 'acepta', etc
    external_reference VARCHAR(255),  -- ID del proveedor
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX (transaction_id),
    INDEX (folio_sii),
    INDEX (status)
);
```

### 10. `inventory_movements` (Auditoría de Stock)
```sql
CREATE TABLE inventory_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id),
    transaction_id UUID REFERENCES transactions(id),  -- Nullable para ajustes manuales
    type VARCHAR(50) NOT NULL CHECK (type IN ('sale', 'adjustment', 'restock', 'loss')),
    quantity_before DECIMAL(10, 3) NOT NULL,
    quantity_after DECIMAL(10, 3) NOT NULL,
    delta DECIMAL(10, 3) GENERATED ALWAYS AS (quantity_after - quantity_before) STORED,
    reason TEXT NOT NULL,  -- "QR-ORD-123", "Manual adjustment", etc
    user_id UUID NOT NULL REFERENCES users(id),  -- Quién realizó el movimiento
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX (product_id),
    INDEX (transaction_id),
    INDEX (type),
    INDEX (created_at),
    INDEX (user_id)
);
```

### 11. `audit_logs` (Auditoría Sistema Completa)
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),  -- NULL para operaciones del sistema
    action VARCHAR(50) NOT NULL,  -- LOGIN, LOGOUT, CREATE, UPDATE, DELETE, CONFIRM_SALE, etc
    entity_type VARCHAR(50) NOT NULL,  -- 'product', 'transaction', 'user', etc
    entity_id UUID,  -- ID de la entidad afectada
    old_values JSONB,  -- Estado anterior (para updates)
    new_values JSONB,  -- Estado nuevo (para updates)
    ip_address INET,
    user_agent TEXT,
    status VARCHAR(50) DEFAULT 'success',  -- success, error
    error_message TEXT,  -- Si hay error
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX (user_id),
    INDEX (action),
    INDEX (entity_type),
    INDEX (created_at)
);
```

---

## 🔑 Índices y Constraints Críticos

```sql
-- ÍNDICES PARA PERFORMANCE
CREATE INDEX idx_products_by_barcode ON products(store_id, barcode);
CREATE INDEX idx_orders_by_uuid ON orders(store_id, uuid);
CREATE INDEX idx_orders_by_station ON orders(station_id, created_at DESC);
CREATE INDEX idx_transactions_by_date ON transactions(store_id, created_at DESC);
CREATE INDEX idx_inventory_movements_timeline ON inventory_movements(product_id, created_at DESC);
CREATE INDEX idx_audit_logs_timeline ON audit_logs(created_at DESC);

-- CONSTRAINTS CRÍTICOS
ALTER TABLE products ADD CONSTRAINT check_stock_non_negative 
    CHECK (stock_quantity >= 0);

ALTER TABLE orders ADD CONSTRAINT check_total_positive 
    CHECK (total > 0 OR status = 'pending');

-- TRIGGER: Actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_users BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_update_products BEFORE UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- TRIGGER: Registrar cambios en audit_logs
CREATE OR REPLACE FUNCTION audit_log_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, old_values, new_values)
    VALUES (
        current_user_id(),  -- Función custom para obtener user_id de contexto
        TG_ARGV[0],  -- action type
        TG_TABLE_NAME,  -- entity_type
        NEW.id,  -- entity_id
        row_to_json(OLD),  -- old_values
        row_to_json(NEW)   -- new_values
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## 💡 Consideraciones de Diseño

### Normalización
- ✅ **3NF:** Todas las tablas normalizadas, sin redundancia
- ✅ **Store-Scoped:** Todas tienen `store_id` para multi-tenant future-proof

### Performance
- ✅ **Índices en PK, FK, barcode, uuid, timestamps**
- ✅ **Particionamiento futuro:** `transactions` y `inventory_movements` por mes/año
- ✅ **Archivado:** Transacciones older de 2 años → table archive

### Integridad
- ✅ **Foreign Keys:** Relaciones aseguradas
- ✅ **Constraints:** Validaciones en DB (no solo app)
- ✅ **Triggers:** Auditoría automática + updated_at
- ✅ **ACID:** PostgreSQL transacciones en operaciones críticas

### Seguridad
- ✅ **Passwords:** Nunca en plaintext, solo hash bcrypt
- ✅ **Audit Log:** Inmutable (INSERT only, nunca UPDATE/DELETE)
- ✅ **Row-level security:** Para multi-tenant (future)

---

## 🚀 Migraciones (Alembic)

```bash
# Sprint 0
alembic revision -m "initial_schema"
# Crear todas las tablas + índices + triggers

# Sprint 1
alembic revision -m "add_categories"
# Puede haber ajustes menores

# Sprint 4
alembic revision -m "add_sii_integration"
# Cambios en boletas, transacciones

# Aplicar migraciones
alembic upgrade head

# Rollback si es necesario (desarrollo solo)
alembic downgrade -1
```

---

**Versión:** 0.1  
**Última actualización:** 5 de abril 2026
