# Base de Datos Provisional de Variables
## Análisis UI → Backend — Sistema Emporio Esperanza

**Fecha de análisis:** 2026-04-19
**Fuente:** Screenshots de vistas activas del frontend (localhost:5173)
**Método:** Extracción visual de variables + contraste con modelos SQLAlchemy actuales

---

## LEYENDA DE ESTADO

| Símbolo | Significado |
|---------|-------------|
| `✅ OK` | Variable existe en el backend exactamente como se necesita |
| `⚠️ PARCIAL` | Existe pero con nombre diferente o falta un campo relacionado |
| `❌ FALTA` | No existe en el backend — debe crearse |
| `🔧 COMPUTED` | No se almacena, se calcula en tiempo real desde otros datos |

---

## 1. CONFIGURACIÓN DEL NEGOCIO

Variables visibles en Login y Header de todas las vistas.

| Variable UI | Valor observado | Estado | Campo backend | Acción |
|-------------|----------------|--------|---------------|--------|
| Nombre del negocio | "Emporio Esperanza" | ❌ FALTA | — | Agregar a Settings o tabla `config` |
| Subtítulo | "Sistema de punto de venta" | ❌ FALTA | — | Agregar a Settings |
| Vendor / Marca | "OptiMind Solutions AI" | ❌ FALTA | — | Agregar a Settings |
| IVA porcentaje | 19% | ❌ FALTA | — | Agregar a Settings como `iva_porcentaje=19` |

**Dependencias:** Todos los cálculos de IVA dependen de `iva_porcentaje`.

---

## 2. AUTENTICACIÓN

Variables de la vista Login (`/login`).

| Variable UI | Valor observado | Estado | Campo backend | Acción |
|-------------|----------------|--------|---------------|--------|
| email | usuario@comerciales.cl | ✅ OK | `users.email` | — |
| password | (oculto) | ✅ OK | `users.hashed_password` | — |
| access_token | (implícito) | ❌ FALTA | — | Implementar JWT |
| rol_usuario | admin / cajero / supervisor | ⚠️ PARCIAL | `users.rol` | Rol "gerente" en UI vs "admin" en backend |

**Credenciales de prueba detectadas en UI:**
```
admin@comerciales.cl     / admin123     → rol: admin (dueña)
caja@comerciales.cl      / caja123      → rol: cajero (operario)
supervisor@comerciales.cl/ super123     → rol: supervisor
dev@comerciales.cl       / devmaster2024→ rol: dev (acceso total)
```

**Dependencias:** `access_token` → todas las demás vistas protegidas.

---

## 3. PRODUCTOS / INVENTARIO

Variables de la vista Inventario y del POS (Caja).

| Variable UI | Columna UI | Estado | Campo backend | Acción |
|-------------|------------|--------|---------------|--------|
| SKU | CAR-001, VER-001 | ⚠️ PARCIAL | `products.codigo_interno` | Mismo campo, necesita formato SKU con prefijo |
| Nombre | "Pollo entero" | ✅ OK | `products.nombre` | — |
| Categoría | Carnes, Verduras, Frutas, Lácteos | ✅ OK | `categories.nombre` | — |
| Unidad | KG, UNIDAD | ✅ OK | `products.unidad` (Enum) | Agregar UNIDAD al Enum (solo tiene UN) |
| Stock actual | 0, 1, 10, 28 | ✅ OK | `products.stock_actual` | — |
| Stock mínimo | 100, 80, 60, 50 | ✅ OK | `products.stock_minimo` | — |
| Stock crítico | 5, 4, 3, 2 | ❌ FALTA | — | Agregar `products.stock_critico` |
| Precio/unidad | $3.490, $7.990 | ✅ OK | `products.precio_venta` | — |
| Estado stock | ok/low/critical/out_of_stock | 🔧 COMPUTED | — | Calcular desde stock_actual vs umbrales |
| Proveedor | "Omeñaca S.A.", "Ideal S.A." | ❌ FALTA | — | Agregar `products.proveedor_id` FK |

**Variables adicionales del POS:**
| Variable UI | Estado | Campo backend | Acción |
|-------------|--------|---------------|--------|
| Precio por kg ("$10.101/kg") | ✅ OK | `products.precio_venta` | — |
| Nombre proveedor en item | ❌ FALTA | — | Via relación `product → proveedor` |
| Código de barras (escaneo) | ✅ OK | `products.codigo_barras` | — |

**Dependencias:**
```
stock_estado ← stock_actual, stock_minimo, stock_critico
alerta_stock ← stock_actual < stock_minimo
alerta_stock_critica ← stock_actual < stock_critico
precio_total_item ← precio_venta × cantidad
```

---

## 4. PRE-BOLETA / POS (Vista Caja/Operario)

| Variable UI | Valor observado | Estado | Campo backend | Acción |
|-------------|----------------|--------|---------------|--------|
| preboleta_codigo | "9a3f-b821" | ✅ OK | `preboletas.id` (UUID) | Mostrar primeros 8 chars |
| station_nombre | "Balanza 1", "Balanza 3" | ✅ OK | `stations.nombre` | — |
| item_nombre_producto | "Jamón campo mitad" | ✅ OK | `preboleta_items.nombre_producto` | — |
| item_proveedor | "Omeñaca S.A." | ❌ FALTA | — | Via `product → proveedor` |
| item_cantidad | 0.500 kg | ✅ OK | `preboleta_items.cantidad` | — |
| item_unidad | kg, UN | ✅ OK | Via `product.unidad` | — |
| item_precio_unitario | $10.101/kg | ✅ OK | `preboleta_items.precio_unitario` | — |
| item_precio_total | $5.051 | ✅ OK | `preboleta_items.precio_total` | — |
| venta_subtotal | $14.078 | ❌ FALTA | — | Agregar `sales.subtotal_clp` |
| venta_iva_porcentaje | 19% | ❌ FALTA | — | Config global `iva_porcentaje` |
| venta_iva_monto | $2.675 | ❌ FALTA | — | Agregar `sales.iva_clp` |
| venta_total | $16.753 | ✅ OK | `sales.total_clp` | — |
| metodo_pago | efectivo/débito/crédito/transfer | ✅ OK | `sales.metodo_pago` (Enum) | — |
| tabs_multiples_balanzas | "Balanza 1 · $16.753", "Balanza 3 · $3.666" | 🔧 COMPUTED | — | Frontend gestiona múltiples preboletas activas |

**Dependencias:**
```
venta_subtotal ← SUM(item_precio_total)
venta_iva_monto ← venta_subtotal × (iva_porcentaje / 100)
venta_total ← venta_subtotal + venta_iva_monto
```

---

## 5. ESTACIONES / BALANZAS

Variables del Panel General y vista Balanzas.

| Variable UI | Valor observado | Estado | Campo backend | Acción |
|-------------|----------------|--------|---------------|--------|
| station_nombre | "Balanza 1", "Caja" | ✅ OK | `stations.nombre` | — |
| station_tipo | balanza / caja | ✅ OK | `stations.tipo` (Enum) | — |
| station_estado | Activa / Error / Inactiva | ❌ FALTA | — | Agregar `stations.estado` Enum |
| station_operario_nombre | "javiera", "ivan" | ❌ FALTA | — | Agregar `stations.operador_actual_id` FK |
| station_transacciones_hoy | 12, 10, 0, 14, 30 | 🔧 COMPUTED | — | COUNT(sales) WHERE date=hoy |
| station_ventas_hoy | $48.000, $42.000 | 🔧 COMPUTED | — | SUM(sales.total_clp) WHERE date=hoy |
| station_ultimo_evento_at | "13-04-2026, 2:59:59 p.m." | ❌ FALTA | — | Agregar `stations.ultimo_evento_at` |
| station_ip_address | (implícito) | ✅ OK | `stations.ip_address` | — |

**Dependencias:**
```
station_ventas_hoy ← sales WHERE station_id AND date=today
station_transacciones_hoy ← COUNT(sales) WHERE station_id AND date=today
station_ticket_promedio ← station_ventas_hoy / station_transacciones_hoy
station_ultimo_evento_at ← MAX(sales.created_at) WHERE station_id
```

---

## 6. USUARIOS

Variables de la vista Usuarios y del header (usuario logueado).

| Variable UI | Valor observado | Estado | Campo backend | Acción |
|-------------|----------------|--------|---------------|--------|
| user_nombre | "María González" | ✅ OK | `users.nombre` | — |
| user_email | (implícito login) | ✅ OK | `users.email` | — |
| user_rut | 76.543.210-K (proveedores) | ✅ OK | `users.rut` | — |
| user_rol | gerente / operador / cajero / supervisor | ⚠️ PARCIAL | `users.rol` | "gerente" en UI → "admin" en backend |
| user_activo | (implícito) | ✅ OK | `users.activo` | — |
| user_station_asignada | (implícito Caja/Operario) | ❌ FALTA | — | Relación via `stations.operador_actual_id` |
| user_ultimo_login | (implícito) | ❌ FALTA | — | Agregar `users.ultimo_login_at` |

**Mapeo de roles UI → Backend:**
| UI | Backend actual | Acción |
|----|---------------|--------|
| gerente | admin | Renombrar o agregar alias |
| operario | operador_balanza | Renombrar |
| cajero | cajero | OK |
| supervisor | supervisor | OK |

---

## 7. VENTAS / TRANSACCIONES

| Variable UI | Estado | Campo backend | Acción |
|-------------|--------|---------------|--------|
| sale_id / folio | ✅ OK | `sales.id` (UUID) | Generar folio secuencial |
| sale_station_id | ✅ OK | `sales.station_id` | — |
| sale_cajero_id | ✅ OK | `sales.cajero_id` | — |
| sale_metodo_pago | ✅ OK | `sales.metodo_pago` | — |
| sale_subtotal_clp | ❌ FALTA | — | Agregar campo |
| sale_iva_clp | ❌ FALTA | — | Agregar campo |
| sale_total_clp | ✅ OK | `sales.total_clp` | — |
| sale_estado | completada/anulada/pendiente/error | ❌ FALTA | — | Agregar `sales.estado` Enum |
| dte_numero | (número SII) | ✅ OK | `dte_transactions.folio` | — |
| dte_tipo | boleta / factura | ✅ OK | `dte_transactions.tipo_dte` | — |

---

## 8. CIERRE DEL DÍA

Vista con mayor cantidad de variables nuevas detectadas.

| Variable UI | Estado | Campo backend | Acción |
|-------------|--------|---------------|--------|
| cierre_fecha | ✅ OK | `daily_reports.date` | — |
| cierre_turno_tipo | "Turno completo" | ❌ FALTA | — | Agregar `daily_reports.turno_tipo` |
| cierre_hora_inicio | "08:00" | ❌ FALTA | — | Agregar `daily_reports.hora_inicio` |
| cierre_hora_fin | "14:15" | ❌ FALTA | — | Agregar `daily_reports.hora_fin` |
| cierre_horas_activo | "6h 15m" | 🔧 COMPUTED | — | hora_fin - hora_inicio |
| cierre_total_ventas | $1.234.500 | ✅ OK | `daily_reports.total_ventas_clp` | — |
| cierre_total_trans | 42 | ✅ OK | `daily_reports.total_transacciones` | — |
| cierre_ticket_promedio | $29.393 | 🔧 COMPUTED | — | total_ventas / total_trans |
| cierre_trend_ventas_pct | +12% vs ayer | 🔧 COMPUTED | — | Comparar con report día anterior |
| cierre_trend_trans_pct | +8% vs ayer | 🔧 COMPUTED | — | Ídem |
| cierre_trend_ticket_pct | -3% vs ayer | 🔧 COMPUTED | — | Ídem |
| cierre_efectivo | $543.180 (44%) | ❌ FALTA | — | Agregar `daily_reports.total_efectivo_clp` |
| cierre_debito | $432.075 (35%) | ❌ FALTA | — | Agregar `daily_reports.total_debito_clp` |
| cierre_credito | $185.175 (15%) | ❌ FALTA | — | Agregar `daily_reports.total_credito_clp` |
| cierre_transferencia | $74.070 (6%) | ❌ FALTA | — | Agregar `daily_reports.total_transferencia_clp` |
| cierre_por_estacion[] | ventas/trans/ticket por balanza | ❌ FALTA | — | Nueva tabla `daily_report_stations` |
| arqueo_fondo_inicial | $50.000 | ❌ FALTA | — | Nueva tabla `cierre_caja` |
| arqueo_monto_esperado | $543.180 | 🔧 COMPUTED | — | = cierre_efectivo |
| arqueo_monto_contado | $593.180 (input manual) | ❌ FALTA | — | `cierre_caja.monto_contado_fisico` |
| arqueo_diferencia | +$0 / "Caja cuadrada" | 🔧 COMPUTED | — | monto_contado - monto_esperado |
| top5_productos[] | nombre, ventas, trans, unidades | ❌ FALTA | — | Query calculada en endpoint |
| alertas_stock_hoy | 0 alertas | 🔧 COMPUTED | — | COUNT alertas del día |
| cierre_observaciones | (texto libre) | ❌ FALTA | — | Agregar `daily_reports.observaciones` |

---

## 9. PROVEEDORES (Módulo nuevo — no existe en backend)

Vista Reportes muestra un módulo completo de gestión de proveedores.

| Variable UI | Valor observado | Estado | Tabla a crear |
|-------------|----------------|--------|---------------|
| proveedor_nombre | "Carnes del Sur Ltda." | ❌ FALTA | `proveedores` |
| proveedor_rut | "76.543.210-K" | ❌ FALTA | `proveedores` |
| proveedor_contacto_nombre | "Pedro Saavedra" | ❌ FALTA | `proveedores` |
| proveedor_contacto_telefono | "+56 9 8123 4567" | ❌ FALTA | `proveedores` |
| factura_folio | "F-00245871" | ❌ FALTA | `facturas_proveedor` |
| factura_oc_numero | "OC-2026-041" | ❌ FALTA | `facturas_proveedor` |
| factura_fecha_emision | "01/04/2026" | ❌ FALTA | `facturas_proveedor` |
| factura_fecha_vencimiento | "30/04/2026" | ❌ FALTA | `facturas_proveedor` |
| factura_fecha_entrega | "05/04/2026" | ❌ FALTA | `facturas_proveedor` |
| factura_total_clp | $200.000 | ❌ FALTA | `facturas_proveedor` |
| factura_iva_clp | $31.933 | ❌ FALTA | `facturas_proveedor` |
| factura_estado_pago | pendiente/vencida/pagada | ❌ FALTA | `facturas_proveedor` |
| factura_estado_recepcion | completa/parcial/pendiente | ❌ FALTA | `facturas_proveedor` |
| factura_items_count | "3 items" | 🔧 COMPUTED | — |

---

## 10. RESUMEN DE BRECHAS (GAP ANALYSIS)

### Variables que el Frontend necesita y el Backend NO tiene

| Prioridad | Variable | Vista que la usa |
|-----------|----------|-----------------|
| 🔴 CRÍTICA | `access_token` JWT | Todas |
| 🔴 CRÍTICA | `iva_porcentaje` (config global) | POS, Cierre |
| 🔴 CRÍTICA | `sales.subtotal_clp` | POS |
| 🔴 CRÍTICA | `sales.iva_clp` | POS |
| 🔴 CRÍTICA | `products.stock_critico` | Inventario |
| 🔴 CRÍTICA | `stations.estado` Enum | Dashboard, Balanzas |
| 🔴 CRÍTICA | `stations.operador_actual_id` | Dashboard, POS |
| 🔴 CRÍTICA | `stations.ultimo_evento_at` | Dashboard |
| 🟡 ALTA | `products.proveedor_id` FK | POS, Inventario |
| 🟡 ALTA | `daily_reports.total_efectivo_clp` | Cierre |
| 🟡 ALTA | `daily_reports.total_debito_clp` | Cierre |
| 🟡 ALTA | `daily_reports.total_credito_clp` | Cierre |
| 🟡 ALTA | `daily_reports.total_transferencia_clp` | Cierre |
| 🟡 ALTA | `daily_reports.observaciones` | Cierre |
| 🟡 ALTA | `daily_reports.hora_inicio` / `hora_fin` | Cierre |
| 🟡 ALTA | `cierre_caja` (tabla nueva) | Cierre |
| 🟡 ALTA | `daily_report_stations` (tabla nueva) | Cierre, Dashboard |
| 🟠 MEDIA | `sales.estado` Enum | Transacciones |
| 🟠 MEDIA | `proveedores` (tabla nueva) | Reportes |
| 🟠 MEDIA | `facturas_proveedor` (tabla nueva) | Reportes |
| 🟠 MEDIA | `users.ultimo_login_at` | Usuarios |
| 🟠 MEDIA | `negocio_nombre` (config) | Login, Header |
| 🔵 BAJA | `sales.estado` folio secuencial | Transacciones |

### Variables que el Backend tiene y NO se usan en el Frontend actual

| Variable | Tabla | Observación |
|----------|-------|-------------|
| `precio_costo` | `products` | No visible en UI — reservado para análisis de margen |
| `stock_maximo` | `products` | No visible en UI — posible uso futuro |
| `dte_transactions.*` | `dte_transactions` | UI muestra número DTE pero el módulo SII no está en vistas |
| `preboleta_audits.*` | `preboleta_audits` | Auditoría interna, no expuesta al usuario |

---

## 11. DIAGRAMA DE DEPENDENCIAS

```
negocio_nombre ──────────────────→ Header (todas las vistas)
iva_porcentaje ──┬───────────────→ POS: iva_monto
                 └───────────────→ Facturas proveedor: iva_clp

users.email + password
    └─→ access_token (JWT)
            └─→ [TODAS LAS RUTAS PROTEGIDAS]

products.stock_actual
    ├─→ stock_estado (vs stock_minimo, stock_critico)
    ├─→ alerta_stock_bajo
    └─→ alerta_stock_critico

preboleta
    ├─→ preboleta_items → (product → proveedor_nombre)
    ├─→ sale (al confirmar pago)
    │       ├─→ subtotal_clp = SUM(items)
    │       ├─→ iva_clp = subtotal × iva_porcentaje
    │       ├─→ total_clp = subtotal + iva
    │       └─→ dte_transaction
    └─→ station.ultimo_evento_at

station
    ├─→ operador_actual_id → user.nombre
    ├─→ ventas_hoy = SUM(sales.total_clp WHERE date=hoy)
    ├─→ transacciones_hoy = COUNT(sales WHERE date=hoy)
    └─→ ticket_promedio_hoy = ventas_hoy / transacciones_hoy

daily_report
    ├─→ total por metodo_pago (efectivo, debito, credito, transferencia)
    ├─→ daily_report_stations[] → por estación
    ├─→ top5_productos[] → desde sale_items
    └─→ cierre_caja → arqueo (fondo_inicial, monto_contado, diferencia)

proveedores
    └─→ facturas_proveedor[]
            └─→ factura_items[] → products
```

---

## 12. NUEVAS TABLAS REQUERIDAS

```sql
-- 1. Tabla de configuración del negocio
CREATE TABLE config (
    key   VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL
);
-- Registros iniciales:
-- ('negocio_nombre', 'Emporio Esperanza')
-- ('iva_porcentaje', '19')
-- ('fondo_inicial_caja_default', '50000')

-- 2. Cierre de caja diario
CREATE TABLE cierre_caja (
    id              UUID PRIMARY KEY,
    date            DATE NOT NULL,
    station_id      UUID REFERENCES stations(id),
    cajero_id       UUID REFERENCES users(id),
    hora_apertura   TIMESTAMPTZ,
    hora_cierre     TIMESTAMPTZ,
    fondo_inicial   INTEGER NOT NULL DEFAULT 0,
    monto_esperado  INTEGER NOT NULL DEFAULT 0,  -- ventas efectivo del día
    monto_contado   INTEGER,                      -- ingresado manualmente
    diferencia      INTEGER,                      -- monto_contado - monto_esperado
    observaciones   TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Resumen diario por estación
CREATE TABLE daily_report_stations (
    id              SERIAL PRIMARY KEY,
    report_date     DATE REFERENCES daily_reports(date),
    station_id      UUID REFERENCES stations(id),
    operador_nombre VARCHAR(120),
    total_ventas    INTEGER DEFAULT 0,
    total_trans     INTEGER DEFAULT 0
);

-- 4. Proveedores
CREATE TABLE proveedores (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre              VARCHAR(200) NOT NULL,
    rut                 VARCHAR(12) UNIQUE NOT NULL,
    contacto_nombre     VARCHAR(120),
    contacto_telefono   VARCHAR(20),
    activo              BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Facturas de proveedores
CREATE TABLE facturas_proveedor (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proveedor_id            UUID REFERENCES proveedores(id),
    folio                   VARCHAR(20) NOT NULL,
    oc_numero               VARCHAR(20),
    fecha_emision           DATE NOT NULL,
    fecha_vencimiento       DATE,
    fecha_entrega_estimada  DATE,
    fecha_entrega_real      DATE,
    subtotal_clp            INTEGER NOT NULL,
    iva_clp                 INTEGER NOT NULL,
    total_clp               INTEGER NOT NULL,
    estado_pago             VARCHAR(20) DEFAULT 'pendiente', -- pendiente/pagada/vencida
    estado_recepcion        VARCHAR(20) DEFAULT 'pendiente', -- pendiente/parcial/completa
    created_at              TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 13. CAMPOS A AGREGAR EN TABLAS EXISTENTES

```sql
-- products: agregar stock_critico y proveedor_id
ALTER TABLE products ADD COLUMN stock_critico NUMERIC(10,3) DEFAULT 0;
ALTER TABLE products ADD COLUMN proveedor_id UUID REFERENCES proveedores(id);

-- stations: agregar estado y operador actual
ALTER TABLE stations ADD COLUMN estado VARCHAR(20) DEFAULT 'inactiva';
ALTER TABLE stations ADD COLUMN operador_actual_id UUID REFERENCES users(id);
ALTER TABLE stations ADD COLUMN ultimo_evento_at TIMESTAMPTZ;

-- sales: agregar subtotal e iva
ALTER TABLE sales ADD COLUMN subtotal_clp INTEGER;
ALTER TABLE sales ADD COLUMN iva_clp INTEGER;
ALTER TABLE sales ADD COLUMN estado VARCHAR(20) DEFAULT 'completada';

-- daily_reports: agregar campos de cierre completo
ALTER TABLE daily_reports ADD COLUMN hora_inicio TIME;
ALTER TABLE daily_reports ADD COLUMN hora_fin TIME;
ALTER TABLE daily_reports ADD COLUMN turno_tipo VARCHAR(30);
ALTER TABLE daily_reports ADD COLUMN total_efectivo_clp INTEGER DEFAULT 0;
ALTER TABLE daily_reports ADD COLUMN total_debito_clp INTEGER DEFAULT 0;
ALTER TABLE daily_reports ADD COLUMN total_credito_clp INTEGER DEFAULT 0;
ALTER TABLE daily_reports ADD COLUMN total_transferencia_clp INTEGER DEFAULT 0;
ALTER TABLE daily_reports ADD COLUMN observaciones TEXT;

-- users: agregar ultimo login
ALTER TABLE users ADD COLUMN ultimo_login_at TIMESTAMPTZ;
```
