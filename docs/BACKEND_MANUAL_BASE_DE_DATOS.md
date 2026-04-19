# Manual de Usuario — Base de Datos
## Emporio Esperanza · Sistema de Punto de Venta e Inventario

**Versión:** 1.0  
**Fecha:** 2026-04-19  
**Audiencia:** Desarrolladores, analistas de datos, equipo técnico  
**Base de datos:** PostgreSQL 15

---

## Índice

1. [¿Qué hace esta base de datos?](#1-qué-hace-esta-base-de-datos)
2. [Mapa general de tablas](#2-mapa-general-de-tablas)
3. [Módulo: Configuración](#3-módulo-configuración)
4. [Módulo: Usuarios y Acceso](#4-módulo-usuarios-y-acceso)
5. [Módulo: Estaciones (Balanzas y Caja)](#5-módulo-estaciones-balanzas-y-caja)
6. [Módulo: Productos e Inventario](#6-módulo-productos-e-inventario)
7. [Módulo: Proveedores](#7-módulo-proveedores)
8. [Módulo: Punto de Venta (Flujo completo)](#8-módulo-punto-de-venta-flujo-completo)
9. [Módulo: Reportes y Cierre del Día](#9-módulo-reportes-y-cierre-del-día)
10. [Relaciones entre módulos](#10-relaciones-entre-módulos)
11. [Reglas de negocio importantes](#11-reglas-de-negocio-importantes)
12. [Consultas frecuentes](#12-consultas-frecuentes)
13. [Glosario](#13-glosario)

---

## 1. ¿Qué hace esta base de datos?

Esta base de datos registra toda la operación diaria de un local comercial tipo emporio o almacén. Cubre cuatro procesos principales:

```
PESAJE (Balanza)  →  PRE-BOLETA  →  PAGO (Caja)  →  BOLETA SII
       ↓                                ↓
   Inventario                      Reportes del día
```

| Proceso | Qué registra |
|---------|-------------|
| **Venta** | Cada producto vendido, su precio, cantidad, método de pago e IVA |
| **Inventario** | Stock actual de cada producto y alertas cuando baja del mínimo |
| **Proveedores** | Facturas recibidas y su estado de pago |
| **Cierre** | Resumen diario de caja: dinero recibido, desglose y arqueo |

---

## 2. Mapa general de tablas

El sistema tiene **16 tablas** organizadas en 6 módulos:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CONFIGURACIÓN                             │
│  config                                                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐
│   USUARIOS    │  │  ESTACIONES   │  │  PRODUCTOS/INVENTARIO │
│  users        │  │  stations     │  │  categories           │
└───────┬───────┘  └───────┬───────┘  │  proveedores          │
        │                  │          │  products              │
        └──────────┬────────┘          └───────────────────────┘
                   ▼
        ┌──────────────────────────────┐
        │     PUNTO DE VENTA           │
        │  preboletas                  │
        │  preboleta_items             │
        │  sales                       │
        │  sale_items                  │
        │  dte_transactions            │
        └──────────────────────────────┘
                   │
        ┌──────────┴───────────────────┐
        ▼                              ▼
┌────────────────┐          ┌────────────────────┐
│ REPORTES/CIERRE│          │    PROVEEDORES     │
│ daily_reports  │          │  facturas_proveedor│
│ daily_report_  │          └────────────────────┘
│   stations     │
│ cierre_caja    │
└────────────────┘
```

---

## 3. Módulo: Configuración

### Tabla `config`

Almacena los parámetros globales del negocio como pares **clave → valor**.

| Clave | Valor por defecto | Para qué se usa |
|-------|-------------------|-----------------|
| `negocio_nombre` | Emporio Esperanza | Nombre que aparece en la interfaz y boletas |
| `negocio_subtitulo` | Sistema de punto de venta | Subtítulo del sistema |
| `iva_porcentaje` | 19 | Tasa de IVA aplicada a todas las ventas |
| `fondo_inicial_caja_default` | 50000 | Dinero base con que parte la caja cada día |
| `vendor_nombre` | OptiMind Solutions AI | Nombre del proveedor del sistema |

**Cómo se usa:** Antes de calcular una venta, el sistema consulta `iva_porcentaje` para calcular el IVA. Este valor afecta a todos los módulos que manejan dinero.

```sql
-- Obtener el IVA configurado
SELECT value::numeric FROM config WHERE key = 'iva_porcentaje';
-- Resultado: 19
```

---

## 4. Módulo: Usuarios y Acceso

### Tabla `users`

Registra a todas las personas que pueden operar el sistema.

| Campo | Descripción |
|-------|-------------|
| `id` | Identificador único (UUID) |
| `nombre` | Nombre completo del usuario |
| `email` | Correo de acceso — es el login |
| `rut` | RUT chileno (opcional) |
| `hashed_password` | Contraseña encriptada con bcrypt |
| `rol` | Nivel de acceso (ver tabla de roles) |
| `activo` | Si puede iniciar sesión o no |
| `ultimo_login_at` | Cuándo ingresó al sistema por última vez |

### Roles disponibles

| Rol | Código | Qué puede hacer |
|-----|--------|-----------------|
| Gerente / Dueña | `admin` | Todo: ver reportes, gestionar usuarios, configuración |
| Supervisor | `supervisor` | Ventas, reportes, no puede cambiar configuración |
| Cajero | `cajero` | Procesar pagos en la caja |
| Operador de balanza | `operador_balanza` | Pesar y generar pre-boletas en balanza |

### Relaciones de `users`

```
users (1) ──────────────→ (N) preboletas
              Como operador que pesa los productos

users (1) ──────────────→ (N) sales
              Como cajero que procesa el pago

users (1) ──────────────→ (N) cierre_caja
              Como cajero que realiza el arqueo

users (1) ──────────────→ (0..1) stations
              Como operador actualmente asignado a una estación
```

**Ejemplo práctico:**
> Javiera (cajero) inicia sesión → el sistema registra `ultimo_login_at`. Al procesar ventas, su `id` queda guardado como `cajero_id` en cada venta.

---

## 5. Módulo: Estaciones (Balanzas y Caja)

### Tabla `stations`

Representa cada dispositivo físico del local.

| Campo | Descripción |
|-------|-------------|
| `id` | Identificador único |
| `nombre` | Nombre visible ("Balanza 1", "Caja Principal") |
| `tipo` | `balanza` o `caja` |
| `estado` | `activa`, `inactiva` o `error` |
| `ip_address` | Dirección IP del dispositivo en la red local |
| `activo` | Si la estación está habilitada |
| `operador_actual_id` | Qué usuario está trabajando en esta estación ahora |
| `ultimo_evento_at` | Cuándo fue la última actividad registrada |

### Tipos de estaciones

```
BALANZA                           CAJA
───────                           ────
Pesa productos                    Recibe el pago
Genera pre-boleta                 Escanea QR de la pre-boleta
Imprime QR para el cliente        Emite boleta electrónica
```

### Relaciones de `stations`

```
stations (1) ──→ (N) preboletas          (la balanza que generó la pre-boleta)
stations (1) ──→ (N) sales               (la caja donde se pagó)
stations (1) ──→ (N) cierre_caja         (arqueo diario de esa estación)
stations (1) ──→ (N) daily_report_stations (resumen diario de esa estación)
users    (1) ──→ (0..1) stations          (operador actualmente asignado)
```

---

## 6. Módulo: Productos e Inventario

### Tabla `categories`

Agrupa productos por tipo para facilitar búsquedas y reportes.

| Categoría | Ejemplos |
|-----------|----------|
| Carnes | Pollo, vacuno, cerdo, embutidos |
| Verduras | Papa, cebolla, lechuga, zanahoria |
| Frutas | Manzana, plátano, naranja, uva |
| Lácteos | Leche, queso, yogur, mantequilla |
| Abarrotes | Arroz, fideos, aceite, azúcar |
| Panadería | Pan marraqueta, hallulla, pan molde |

### Tabla `products`

El catálogo completo de productos vendibles.

| Campo | Descripción |
|-------|-------------|
| `id` | Identificador único |
| `codigo_barras` | Para escanear con pistola de código de barras |
| `codigo_interno` | Código propio del local (ej: CAR-001) |
| `nombre` | Nombre del producto |
| `categoria_id` | A qué categoría pertenece |
| `proveedor_id` | Quién lo suministra |
| `unidad` | `KG` (se vende al peso) o `UN` (se vende por unidad) |
| `precio_venta` | Precio actual de venta en CLP |
| `precio_costo` | Precio de compra al proveedor (para calcular margen) |
| `stock_actual` | Cantidad disponible ahora mismo |
| `stock_minimo` | Umbral de alerta baja de stock |
| `stock_critico` | Umbral de alerta crítica (menor que mínimo) |
| `stock_maximo` | Límite superior de almacenamiento |

### Semáforo de stock

```
stock_actual > stock_minimo          → ✅ OK — stock normal
stock_actual ≤ stock_minimo          → 🟡 LOW — generar orden de compra
stock_actual ≤ stock_critico         → 🔴 CRITICAL — urgente
stock_actual = 0                     → ⚫ OUT — sin stock
```

### Regla de integridad
`stock_critico` siempre debe ser **menor o igual** que `stock_minimo`. La base de datos rechaza el registro si se viola esta regla (`chk_stock_umbrales`).

### Productos KG vs Productos UN

```
PRODUCTO KG (por peso)              PRODUCTO UN (por unidad)
─────────────────────               ──────────────────────────
Pollo entero                        Leche entera 1L
stock_actual = 28.500               stock_actual = 60
cantidad en venta = 1.350 kg        cantidad en venta = 2
precio_total = 1.350 × $3.490       precio_total = 2 × $1.090
            = $4.712                            = $2.180
```

### Relaciones de `products`

```
categories  (1) ──→ (N) products           (categoría del producto)
proveedores (1) ──→ (N) products           (quién lo suministra)
products    (1) ──→ (N) preboleta_items    (aparece en pre-boletas)
products    (1) ──→ (N) sale_items         (aparece en ventas)
```

---

## 7. Módulo: Proveedores

### Tabla `proveedores`

Registro de empresas o personas que suministran productos al local.

| Campo | Descripción |
|-------|-------------|
| `id` | Identificador único |
| `nombre` | Nombre de la empresa proveedora |
| `rut` | RUT único del proveedor |
| `contacto_nombre` | Nombre de la persona de contacto |
| `contacto_telefono` | Teléfono directo |
| `activo` | Si se puede seguir comprando a este proveedor |

### Tabla `facturas_proveedor`

Registra cada factura recibida de un proveedor.

| Campo | Descripción |
|-------|-------------|
| `folio` | Número de la factura (ej: F-00245871) |
| `oc_numero` | Número de orden de compra asociada |
| `fecha_emision` | Cuándo emitió la factura el proveedor |
| `fecha_vencimiento` | Fecha límite de pago |
| `fecha_entrega_estimada` | Cuándo se esperaba la mercadería |
| `fecha_entrega_real` | Cuándo llegó realmente |
| `subtotal_clp` | Valor neto de la factura |
| `iva_clp` | IVA de la factura (19%) |
| `total_clp` | Total a pagar (subtotal + IVA) |
| `estado_pago` | `pendiente`, `pagada` o `vencida` |
| `estado_recepcion` | `pendiente`, `parcial` o `completa` |

### Estados de una factura

```
ESTADO DE PAGO          ESTADO DE RECEPCIÓN
──────────────          ───────────────────
pendiente               pendiente   → mercadería aún no llega
   ↓                    parcial     → llegó una parte
pagada                  completa    → todo recibido
vencida (sin pagar)
```

### Relaciones de `proveedores`

```
proveedores (1) ──→ (N) products            (productos que suministra)
proveedores (1) ──→ (N) facturas_proveedor  (facturas emitidas)
```

---

## 8. Módulo: Punto de Venta (Flujo completo)

Este módulo es el núcleo del sistema. Registra cada transacción de venta.

### Flujo de una venta (paso a paso)

```
PASO 1 — PESAJE EN BALANZA
┌────────────────────────────────────────────────────┐
│  Operador pone producto en balanza                 │
│  Sistema crea: preboleta + preboleta_items         │
│  Balanza imprime QR para el cliente                │
└────────────────────────┬───────────────────────────┘
                         │ Cliente lleva QR a caja
                         ▼
PASO 2 — PAGO EN CAJA
┌────────────────────────────────────────────────────┐
│  Cajero escanea QR → recupera la preboleta         │
│  Sistema calcula:                                  │
│    subtotal_clp = suma de todos los items          │
│    iva_clp      = subtotal × 19%                  │
│    total_clp    = subtotal + iva                   │
│  Cliente elige método de pago                      │
│  Sistema crea: sale + sale_items                   │
│  Preboleta cambia estado: pendiente → procesada    │
└────────────────────────┬───────────────────────────┘
                         │
                         ▼
PASO 3 — EMISIÓN DE BOLETA ELECTRÓNICA
┌────────────────────────────────────────────────────┐
│  Sistema envía al SII: dte_transaction             │
│  SII responde con folio (número de boleta)         │
│  Estado DTE: pendiente → enviado → aceptado        │
└────────────────────────────────────────────────────┘
```

### Tabla `preboletas`

Generada por la balanza. Es la "lista de compra" del cliente antes de pagar.

| Campo | Descripción |
|-------|-------------|
| `id` | UUID — los primeros 8 caracteres se codifican en el QR |
| `station_id` | Qué balanza la generó |
| `operator_id` | Quién pesó los productos |
| `estado` | `pendiente` → `procesada` / `expirada` / `cancelada` |
| `total_clp` | Suma de todos los items (sin IVA) |
| `qr_url` | URL del código QR para escanear en caja |
| `expires_at` | Hora de vencimiento (si no se procesa, expira) |

### Estados de una preboleta

```
pendiente ──→ procesada   (la caja la escaneó y generó la venta)
          └─→ expirada    (pasó el tiempo sin ser procesada)
          └─→ cancelada   (el operador la anuló manualmente)
```

### Tabla `preboleta_items`

Cada línea de producto dentro de una pre-boleta.

| Campo | Descripción |
|-------|-------------|
| `preboleta_id` | A qué pre-boleta pertenece |
| `product_id` | Qué producto es (puede ser NULL si el producto fue eliminado) |
| `nombre_producto` | Nombre copiado al momento de crear la pre-boleta (snapshot) |
| `cantidad` | Kilos o unidades |
| `precio_unitario` | Precio al momento de la venta (snapshot) |
| `precio_total` | `cantidad × precio_unitario` |

> **Importante:** `nombre_producto` y `precio_unitario` son **copias** del producto en ese momento. Si el precio del producto cambia después, la pre-boleta queda con el precio original. Esto garantiza integridad histórica.

### Tabla `sales`

La venta confirmada y pagada.

| Campo | Descripción |
|-------|-------------|
| `id` | UUID de la venta |
| `preboleta_id` | Pre-boleta de origen (relación 1:1) |
| `station_id` | Caja donde se procesó el pago |
| `cajero_id` | Usuario que procesó el pago |
| `metodo_pago` | `efectivo`, `debito`, `credito` o `transferencia` |
| `subtotal_clp` | Valor neto (sin IVA) |
| `iva_clp` | IVA calculado (19% del subtotal) |
| `total_clp` | Monto final cobrado al cliente |
| `estado` | `completada`, `anulada`, `pendiente` o `error` |

### Regla de integridad de montos
La base de datos verifica que `total_clp = subtotal_clp + iva_clp`. Si no cuadran, rechaza la venta (`chk_sales_total`).

### Tabla `sale_items`

Los mismos productos de `preboleta_items`, copiados a la venta al momento de pagar. También son snapshots históricos.

### Tabla `dte_transactions`

Registro de cada boleta o factura electrónica enviada al SII.

| Campo | Descripción |
|-------|-------------|
| `sale_id` | A qué venta corresponde (1:1) |
| `folio` | Número de boleta asignado por el SII |
| `tipo_dte` | `boleta` (código 39) o `factura` (código 33) |
| `estado` | Estado del envío al SII |
| `retry_count` | Cuántas veces se intentó reenviar |
| `sent_at` | Cuándo se envió |
| `confirmed_at` | Cuándo el SII confirmó |

### Estados de un DTE

```
pendiente → enviado → aceptado   ✅ (flujo normal)
         └─→ rechazado           ❌ (SII rechazó, requiere corrección)
         └─→ retrying            🔄 (reintento automático en curso)
```

### Relaciones del módulo de ventas

```
stations       (1) ──→ (N) preboletas
users          (1) ──→ (N) preboletas      (operador de balanza)
preboletas     (1) ──→ (N) preboleta_items
products       (1) ──→ (N) preboleta_items

preboletas     (1) ──→ (0..1) sales        (1 preboleta genera 1 venta)
stations       (1) ──→ (N) sales           (caja donde se pagó)
users          (1) ──→ (N) sales           (cajero)
sales          (1) ──→ (N) sale_items
products       (1) ──→ (N) sale_items

sales          (1) ──→ (1) dte_transactions
```

---

## 9. Módulo: Reportes y Cierre del Día

Al finalizar la jornada, el sistema genera un resumen completo.

### Tabla `daily_reports`

Resumen diario calculado por el sistema. Una fila por día.

| Campo | Descripción |
|-------|-------------|
| `date` | Fecha del reporte (clave primaria) |
| `total_ventas_clp` | Total de dinero recaudado en el día |
| `total_transacciones` | Número de ventas realizadas |
| `total_efectivo_clp` | Ventas pagadas en efectivo |
| `total_debito_clp` | Ventas pagadas con débito |
| `total_credito_clp` | Ventas pagadas con crédito |
| `total_transferencia_clp` | Ventas por transferencia |
| `boletas_emitidas` | Cuántas boletas electrónicas se emitieron |
| `hora_inicio` | Hora de apertura del día |
| `hora_fin` | Hora de cierre del día |
| `turno_tipo` | Descripción del turno (ej: "Turno completo") |
| `observaciones` | Notas del día |

### Tabla `daily_report_stations`

Desglosa el reporte diario por cada estación individual.

| Campo | Descripción |
|-------|-------------|
| `report_date` | Fecha del reporte (FK → daily_reports) |
| `station_id` | Estación (FK → stations) |
| `operador_nombre` | Nombre del operador ese día |
| `total_ventas` | Ventas atribuidas a esa estación |
| `total_transacciones` | Transacciones de esa estación |

### Tabla `cierre_caja`

El arqueo físico del efectivo al final del día.

| Campo | Descripción |
|-------|-------------|
| `date` | Fecha del cierre |
| `station_id` | Qué caja se arquea |
| `cajero_id` | Quién realizó el arqueo |
| `hora_apertura` | Cuándo se abrió la caja |
| `hora_cierre` | Cuándo se cerró la caja |
| `fondo_inicial` | Dinero con que partió la caja ($50.000 por defecto) |
| `monto_esperado` | Total en efectivo según el sistema (= ventas en efectivo) |
| `monto_contado` | Dinero contado físicamente |
| `diferencia` | `monto_contado − monto_esperado` (negativo = faltante) |
| `observaciones` | Notas del arqueo |

### Interpretación de la diferencia

```
diferencia = 0           → "Caja cuadrada" ✅
diferencia > 0           → Sobra efectivo (cliente pagó de más o error)
diferencia < 0           → Falta efectivo (posible error o hurto)
```

### Relaciones del módulo de reportes

```
daily_reports     (1) ──→ (N) daily_report_stations
stations          (1) ──→ (N) daily_report_stations
stations          (1) ──→ (N) cierre_caja
users             (1) ──→ (N) cierre_caja
```

---

## 10. Relaciones entre módulos

### Diagrama completo de dependencias

```
config
  └── iva_porcentaje ──────────────────────→ Cálculo en sales
                                             Cálculo en facturas_proveedor

users
  ├── como operador_balanza ───────────────→ preboletas.operator_id
  ├── como cajero ─────────────────────────→ sales.cajero_id
  │                                          cierre_caja.cajero_id
  └── como operador_actual ────────────────→ stations.operador_actual_id

categories ──────────────────────────────→ products.categoria_id
proveedores
  ├────────────────────────────────────→ products.proveedor_id
  └────────────────────────────────────→ facturas_proveedor.proveedor_id

stations
  ├── tipo balanza ──────────────────────→ preboletas.station_id
  ├── tipo caja ────────────────────────→ sales.station_id
  │                                       cierre_caja.station_id
  └────────────────────────────────────→ daily_report_stations.station_id

preboletas
  ├─────────────────────────────────────→ preboleta_items (1:N)
  └─────────────────────────────────────→ sales (1:1)

products
  ├─────────────────────────────────────→ preboleta_items (snapshot)
  └─────────────────────────────────────→ sale_items (snapshot)

sales
  ├─────────────────────────────────────→ sale_items (1:N)
  └─────────────────────────────────────→ dte_transactions (1:1)

daily_reports ────────────────────────→ daily_report_stations (1:N)
```

### Tabla de cardinalidades

| Relación | Tipo | Significado |
|----------|------|-------------|
| category → products | 1 : N | Una categoría tiene muchos productos |
| proveedor → products | 1 : N | Un proveedor suministra muchos productos |
| proveedor → facturas | 1 : N | Un proveedor emite muchas facturas |
| user → preboletas | 1 : N | Un operador puede hacer muchas pre-boletas |
| user → sales | 1 : N | Un cajero puede procesar muchas ventas |
| station → preboletas | 1 : N | Una balanza puede generar muchas pre-boletas |
| station → sales | 1 : N | Una caja puede registrar muchas ventas |
| preboleta → items | 1 : N | Una pre-boleta tiene uno o más productos |
| preboleta → sale | 1 : 0..1 | Una pre-boleta origina máximo una venta |
| sale → items | 1 : N | Una venta tiene uno o más productos |
| sale → dte | 1 : 1 | Cada venta genera exactamente una boleta |
| daily_report → stations | 1 : N | Un reporte tiene detalle por cada estación |

---

## 11. Reglas de negocio importantes

### Regla 1 — Integridad de montos en ventas

```sql
-- La base de datos rechaza si no se cumple:
total_clp = subtotal_clp + iva_clp
```

### Regla 2 — Umbrales de stock coherentes

```sql
-- stock_critico nunca puede ser mayor que stock_minimo:
stock_critico <= stock_minimo
```

### Regla 3 — Integridad de facturas de proveedor

```sql
-- El total siempre debe ser subtotal + IVA:
total_clp = subtotal_clp + iva_clp
```

### Regla 4 — Unicidad de cierre por estación y día

```sql
-- Solo puede haber un cierre por estación por día:
UNIQUE (date, station_id)  -- en cierre_caja
UNIQUE (report_date, station_id)  -- en daily_report_stations
```

### Regla 5 — Snapshots históricos

Los campos `nombre_producto` y `precio_unitario` en `preboleta_items` y `sale_items` son **copias** tomadas en el momento de la venta. Esto garantiza que los reportes históricos sean correctos aunque el precio o el nombre del producto cambie después.

### Regla 6 — Cascada de eliminación

| Si se elimina... | Se eliminan automáticamente... |
|------------------|-------------------------------|
| `preboletas` | sus `preboleta_items` |
| `sales` | sus `sale_items` y su `dte_transaction` |
| `daily_reports` | sus `daily_report_stations` |

### Regla 7 — SET NULL en lugar de eliminar

Si se elimina un `producto`, las referencias en `preboleta_items.product_id` y `sale_items.product_id` quedan en `NULL`, pero el registro de la venta se mantiene gracias al snapshot de `nombre_producto`.

---

## 12. Consultas frecuentes

### ¿Cuánto se vendió hoy?

```sql
SELECT
    SUM(total_clp)        AS total_dia,
    COUNT(*)              AS transacciones,
    AVG(total_clp)        AS ticket_promedio
FROM sales
WHERE created_at::date = CURRENT_DATE
  AND estado = 'completada';
```

### ¿Qué productos tienen stock crítico?

```sql
SELECT nombre, unidad, stock_actual, stock_critico, stock_minimo,
    CASE
        WHEN stock_actual = 0             THEN 'SIN STOCK'
        WHEN stock_actual <= stock_critico THEN 'CRITICO'
        WHEN stock_actual <= stock_minimo  THEN 'BAJO'
    END AS alerta
FROM products
WHERE stock_actual <= stock_minimo AND activo = TRUE
ORDER BY stock_actual ASC;
```

### ¿Cuánto se vendió por método de pago esta semana?

```sql
SELECT
    metodo_pago,
    COUNT(*)       AS transacciones,
    SUM(total_clp) AS total_clp,
    ROUND(100.0 * SUM(total_clp) / SUM(SUM(total_clp)) OVER (), 1) AS porcentaje
FROM sales
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
  AND estado = 'completada'
GROUP BY metodo_pago
ORDER BY total_clp DESC;
```

### ¿Cuál fue el top 5 de productos del mes?

```sql
SELECT
    si.nombre_producto,
    COUNT(DISTINCT si.sale_id)   AS transacciones,
    SUM(si.cantidad)             AS unidades_vendidas,
    SUM(si.precio_total)         AS total_clp
FROM sale_items si
JOIN sales s ON s.id = si.sale_id
WHERE s.created_at >= DATE_TRUNC('month', CURRENT_DATE)
  AND s.estado = 'completada'
GROUP BY si.nombre_producto
ORDER BY total_clp DESC
LIMIT 5;
```

### ¿Cuáles son las facturas de proveedores vencidas?

```sql
SELECT
    p.nombre            AS proveedor,
    fp.folio,
    fp.fecha_vencimiento,
    fp.total_clp,
    CURRENT_DATE - fp.fecha_vencimiento AS dias_vencida
FROM facturas_proveedor fp
JOIN proveedores p ON p.id = fp.proveedor_id
WHERE fp.estado_pago = 'pendiente'
  AND fp.fecha_vencimiento < CURRENT_DATE
ORDER BY dias_vencida DESC;
```

### ¿Cómo cuadró la caja hoy?

```sql
SELECT
    s.nombre                    AS estacion,
    cc.fondo_inicial,
    cc.monto_esperado,
    cc.monto_contado,
    cc.diferencia,
    CASE
        WHEN cc.diferencia = 0   THEN 'Cuadrada ✅'
        WHEN cc.diferencia > 0   THEN 'Sobra ⚠️'
        ELSE                          'Faltante 🔴'
    END AS estado_arqueo
FROM cierre_caja cc
JOIN stations s ON s.id = cc.station_id
WHERE cc.date = CURRENT_DATE;
```

### ¿Qué DTE están pendientes de confirmar?

```sql
SELECT
    dt.folio,
    dt.estado,
    dt.retry_count,
    s.total_clp,
    dt.sent_at
FROM dte_transactions dt
JOIN sales s ON s.id = dt.sale_id
WHERE dt.estado IN ('pendiente', 'enviado', 'retrying')
ORDER BY dt.created_at;
```

---

## 13. Glosario

| Término | Significado |
|---------|-------------|
| **UUID** | Identificador único universal (ej: `a3f2-b821-...`) — garantiza unicidad sin usar números secuenciales |
| **Pre-boleta** | Documento digital generado por la balanza con los productos pesados, antes de pagar |
| **DTE** | Documento Tributario Electrónico — la boleta o factura enviada al SII de Chile |
| **SII** | Servicio de Impuestos Internos de Chile — recibe y valida las boletas electrónicas |
| **Folio** | Número único asignado por el SII a cada boleta electrónica |
| **IVA** | Impuesto al Valor Agregado — 19% en Chile |
| **Snapshot** | Copia del valor en un momento específico, para preservar el historial |
| **Arqueo** | Conteo físico del dinero en caja al final del día |
| **Fondo inicial** | Dinero con que parte la caja al inicio del día ($50.000 por defecto) |
| **Stock crítico** | Cantidad mínima absoluta de un producto — por debajo de este nivel se para la operación |
| **Stock mínimo** | Punto de reorden — cuando se llega aquí hay que pedir al proveedor |
| **FK** | Foreign Key — campo que apunta a un registro de otra tabla |
| **PK** | Primary Key — identificador único e irrepetible dentro de una tabla |
| **ENUM** | Tipo de dato que solo acepta valores de una lista predefinida |
| **CLP** | Peso Chileno — moneda del sistema. Los precios se almacenan en pesos enteros sin decimales |
| **Celery** | Sistema de tareas en background que genera los reportes diarios automáticamente |

---

**Autor:** Allan Luco  
**Última actualización:** 2026-04-19  
**Versión de BD:** Schema v2 (migración b4e7f2a91d30)
