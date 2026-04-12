# 📊 Dashboard Gerente — Diseño de Interfaz Gráfica

**Para:** Jonathan (Frontend Dev)  
**Stack:** Vue 3 + TypeScript + Tailwind CSS + Pinia + TanStack Query + ApexCharts  
**Fecha:** 6 de abril de 2026  
**Versión:** 0.1 (MVP)

---

## 🎨 PALETA DE COLORES

### Dark Theme (primario para condiciones de luz variable en comercios)

```
Backgrounds:
  Canvas (fondo principal):     #0F1117 (casi negro)
  Surface (cards, sidebar):     #1A1D27
  Surface-2 (modales elevados): #22263A
  Border (divisores):           #2E3348

Brand (primary):
  500: #3B82F6 (azul — activo, primario)
  400: #60A5FA (hover)
  600: #2563EB (pressed)

Semantic:
  ✅ Success (stock OK):        #22C55E (verde)
  ⚠️  Warning (bajo stock):    #F59E0B (amarillo)
  🔴 Danger (crítico):         #EF4444 (rojo)
  ℹ️  Info (informacional):    #06B6D4 (cyan)

Text:
  Primary (headings, valores): #F1F5F9 (blanco)
  Secondary (labels):          #94A3B8 (gris claro)
  Muted (deshabilitado):       #475569 (gris)
```

---

## 📐 LAYOUT SHELL

Todas las vistas comparten esta estructura:

```
┌────────────────────────────────────────────────────────────────────┐
│ SIDEBAR (240px fixed)      │ TOP BAR (56px sticky, full width)    │
│                            ├──────────────────────────────────────│
│  📱 Logo                   │ Breadcrumb      🔔 ⏰ 👤 (derecha)   │
│  ─────────────────         ├──────────────────────────────────────│
│  📊 Panel General          │                                      │
│  ⚡ Transacciones          │     <MAIN CONTENT AREA>              │
│  📦 Inventario             │     (scrollable)                     │
│  🖥️  Balanzas              │                                      │
│  📈 Reportes               │                                      │
│  👥 Usuarios               │                                      │
│  🔐 Cierre del Día         │                                      │
│  ─────────────────         │                                      │
│  👤 Giuliano Larosa        │                                      │
│  Gerente                   │                                      │
└────────────────────────────────────────────────────────────────────┘
```

### Sidebar

- **Fondo:** `bg-surface` (#1A1D27)
- **Logo:** "Comerciales" + ícono, 56px alto, clickeable → `/gerente`
- **Nav items:** 7 items con ícono + texto, left border accent (brand-500) cuando activo
- **Usuario:** Profile info al final, logout button

### Top Bar

- **Fondo:** `bg-surface` (#1A1D27)
- **Left:** Breadcrumb (ej: "Inicio > Panel General")
- **Right:** 
  - Notification bell con badge rojo (# de alertas)
  - Hora actual (HH:mm)
  - Avatar del usuario con dropdown menu

---

## 📊 VISTA 1: PANEL GENERAL (DashboardView)

**Ruta:** `/gerente`  
**Prioridad:** P0 (primera pantalla visible)  
**Descripción:** KPIs grandes, estado estaciones, charts ventas, alertas bajo stock

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ PANEL GENERAL                                           🔄 Actualizar│
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┬─────────────────┬──────────────┬──────────┐│
│  │ 💰 Ventas       │ 📊 Transacciones│ 🏷️  Ticket  │ 🖥️ Balanzas│
│  │ $1.234.500      │ 42             │ $29.393      │ 3 / 4    │
│  │ ↑ 12% vs ayer   │ ↑ 8% vs ayer    │ ↓ 3% vs ayer │ ⚠️ 1 OFF │
│  └─────────────────┴─────────────────┴──────────────┴──────────┘│
│                                                                   │
│  ESTADO DE BALANZAS (5 pills horizontales)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│
│  │ Bal. 1   │ │ Bal. 2   │ │ Bal. 3   │ │ Bal. 4   │ │ Caja   ││
│  │ ✅ Activa │ │ ✅ Activa │ │ ⚠️ Error  │ │ ✅ Activa │ │ ✅ OK   ││
│  │ José     │ │ María    │ │ (manual) │ │ Pedro    │ │ Caja 1 ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘│
│                                                                   │
│  VENTAS POR HORA (60%)        │  TOP 5 PRODUCTOS (40%)         │
│  ╔════════════════════════════╗ ╔═════════════════════════════╗ │
│  ║ $ 350k  ╱╲                ║ ║ 1. Pollo (filete)  $125k   ║ │
│  ║         ╱  ╲              ║ ║ 2. Carne (costilla) $89.5k ║ │
│  ║   ╱╲ ╱╲╱    ╲             ║ ║ 3. Pastel (queque)  $65.2k ║ │
│  ║  ╱  ╲╱      ╲╱            ║ ║ 4. Verdura (lechuga) $34.8k║ │
│  ║ 6:00 8:00 10:00 12:00 14:00║ ║ 5. Fruta (plátano)  $28.5k ║ │
│  ╚════════════════════════════╝ ╚═════════════════════════════╝ │
│                                                                   │
│  📢 ALERTAS DE STOCK BAJO (colapsable, aquí expandido)          │
│  ┌───────────────────────────────────────────────────────────────┐│
│  │ ⚠️  CRÍTICO: Pollo (filete) — 2.5kg / 10kg mín              ││
│  │ ⚠️  BAJO: Carne (costilla) — 4kg / 8kg mín                   ││
│  │ ⚠️  BAJO: Pastel (queque) — 3 unid / 5 mín                   ││
│  └───────────────────────────────────────────────────────────────┘│
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### KPI Card (detalle de cada una)

```
┌─────────────────────┐
│ 💰 Ventas del Día   │ ← ícono + label
│                     │
│ $1.234.500          │ ← valor grande (2.5rem, bold)
│ ↑ 12% vs ayer       │ ← trend (verde arriba, rojo abajo)
│ a esta hora         │ ← contexto
└─────────────────────┘
```

**Diseño:** 
- Border radius 8px
- Background: `bg-surface` (#1A1D27)
- Ícono: 32x32px en rounded square (`bg-brand-500/10` con tint del color)
- Fuente valor: `text-3xl font-semibold text-primary`
- Fuente label: `text-sm text-secondary`
- Hover: `shadow-lg` (subtle elevation)

### Station Status Pills

```
┌─────────────┐
│ Balanza 1   │
│ ✅ Activa    │ ← colored badge
│ José        │ ← operador
│ 08:43       │ ← última actividad
└─────────────┘
```

Status colores:
- `✅ Activa` → verde (#22C55E)
- `⚠️  Error` → rojo (#EF4444)
- `🔌 Offline` → gris (#475569)
- `🔧 Mantenimiento` → amarillo (#F59E0B)

---

## ⚡ VISTA 2: TRANSACCIONES EN TIEMPO REAL

**Ruta:** `/gerente/transacciones`  
**Prioridad:** P1  
**Descripción:** Tabla live de todas las ventas del día con modal de detalle

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ TRANSACCIONES EN TIEMPO REAL                🌐 EN VIVO 🔄 Hace 3s│
├─────────────────────────────────────────────────────────────────┤
│ 🔍 Buscar         [Estado▼] [Balanza▼] [Período▼]              │
├──────┬────────┬──────────┬─────────┬────────────┬────────┬──────┤
│Folio │ Hora   │ Balanza  │ Cajero  │ Total      │ Pago   │Estado│
├──────┼────────┼──────────┼─────────┼────────────┼────────┼──────┤
│T-421 │ 14:23  │ Bal. 1   │ José    │ $45.230    │ Débito │ ✅   │
│T-420 │ 14:15  │ Bal. 2   │ María   │ $128.500   │ Efvo   │ ✅   │
│T-419 │ 14:08  │ Caja     │ Pedro   │ $89.750    │ Créd   │ ✅   │
│T-418 │ 13:54  │ Bal. 1   │ José    │ $23.400    │ Tran   │ ✅   │
│T-417 │ 13:42  │ Bal. 3   │ ?       │ $156.200   │ Débito │ ⚠️   │
└──────┴────────┴──────────┴─────────┴────────────┴────────┴──────┘
│ ↓ Anteriores (página 1 de 18)
```

### Features

- **Live indicator:** Punto verde pulsante + "EN VIVO" + "Hace Xs" (actualizado cada 3-5s)
- **Filters:** Search por folio, estado (completada/anulada/pendiente), balanza, rango fecha
- **Pagination:** 25 filas por página, controles abajo
- **Row click:** Abre modal con detalle completo
- **Status badge:** 
  - `✅ Completada` → verde
  - `❌ Anulada` → rojo oscuro
  - `⏳ Pendiente` → amarillo
  - `⚠️ Error` → rojo

### Modal de Detalle Transacción

```
┌────────────────────────────────────────────────────┐
│ Detalle Transacción T-421                    [X]   │
├────────────────────────────────────────────────────┤
│                                                    │
│ Folio:            T-421                           │
│ Hora:             14:23:15 (6 de abril, 2026)     │
│ Balanza:          Bal. 1 (José)                   │
│ Cajero:           Pedro                           │
│                                                    │
│ ─────────────────────────────────────────────────  │
│ ITEMS                                              │
│ ─────────────────────────────────────────────────  │
│ Pollo (filete)      1.5kg x $5.200/kg   $7.800    │
│ Carne (costilla)    2.3kg x $6.500/kg   $14.950   │
│ Pastel (queque)     3 unid x $4.200     $12.600   │
│ Lechuga             0.8kg x $1.500/kg   $1.200    │
│                                         ──────── │
│                                  Subtotal $36.550 │
│                            IVA (19%)      $6.945   │
│                            TOTAL        $43.495   │
│                                                    │
│ ─────────────────────────────────────────────────  │
│ PAGO                                               │
│ ─────────────────────────────────────────────────  │
│ Método:           Débito                          │
│ Cuotas:           1                               │
│ Referencia:       #98765432                       │
│ Monto pagado:     $43.495                         │
│                                                    │
│ ─────────────────────────────────────────────────  │
│ BOLETA ELECTRÓNICA (SII)                          │
│ ─────────────────────────────────────────────────  │
│ Folio SII:        Pendiente...                    │
│ Tipo:             Boleta                          │
│ Estado:           Emitiendo                       │
│ Timestamp:        2026-04-06T14:23:30             │
│                                                    │
│ [Descargar PDF]  [Anular]  [Cerrar]              │
└────────────────────────────────────────────────────┘
```

---

## 📦 VISTA 3: INVENTARIO

**Ruta:** `/gerente/inventario`  
**Prioridad:** P1  
**Descripción:** Stock actual + alertas bajo stock

### Pantalla Stock Actual (Tab 1)

```
┌─────────────────────────────────────────────────────────────────┐
│ INVENTARIO                                                      │
├─────────────────┬───────────────────────────────────────────────┤
│ [Stock Actual] │ [Alertas (5)]                                │
├─────────────────────────────────────────────────────────────────┤
│ Categoría: [Todas ▼]                                            │
│ 🔍 Buscar...                                                    │
├────────┬─────────────────┬──────────┬──────────┬──────────┬─────┤
│SKU     │Producto         │Categoría │Stock Act │Stock Mín │Info │
├────────┼─────────────────┼──────────┼──────────┼──────────┼─────┤
│POL-001 │Pollo (filete)   │Carnes    │████ 2.5k │ 10kg   │ ⚠️ │
│CAR-002 │Carne (costilla) │Carnes    │██████ 4k │ 8kg    │ ⚠️ │
│PAT-001 │Pastel (queque)  │Panadería │████ 3un  │ 5un    │ ⚠️ │
│VER-001 │Lechuga          │Verduras  │███████████ 8kg  │ 5kg  │ ✅ │
│FRU-001 │Plátano          │Frutas    │██████████ 12kg │ 8kg  │ ✅ │
│EMB-001 │Jamón serrano    │Embutidos │████████ 6kg  │ 5kg  │ ✅ │
│LAC-001 │Queso fresco     │Lácteos   │██████ 4.5kg │ 6kg  │ ⚠️ │
│  ...   │                 │          │            │        │    │
└────────┴─────────────────┴──────────┴──────────┴──────────┴─────┘
```

**Stock Level Bar** (barra visual):
- Verde si stock > mín
- Amarillo si stock entre 50% mín y mín
- Rojo si stock < 50% mín

Clicking "Info" o en la fila abre modal para editar stock:

```
┌───────────────────────────────────┐
│ Editar Stock: Pollo (filete)     │
├───────────────────────────────────┤
│ Stock actual:        [2.5] kg     │
│ Stock mínimo:        [10] kg      │
│ Precio/unidad:       $5.200 CLP   │
│                                   │
│ Cambiar stock a (kg): [2.5]       │
│ Razón: [Reconteo ▼]              │
│                                   │
│ [Guardar]  [Cancelar]            │
└───────────────────────────────────┘
```

### Pantalla Alertas (Tab 2)

```
┌─────────────────────────────────────────────────────────────────┐
│ ALERTAS DE STOCK BAJO (5 productos)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 🔴 CRÍTICO (< 50% del mínimo)                                  │
│   ├─ Pollo (filete) — 2.5kg / 10kg mín [Comprar] [Reconocer]  │
│                                                                  │
│ 🟡 BAJO (entre 50%-100% del mínimo)                            │
│   ├─ Carne (costilla) — 4kg / 8kg mín  [Comprar] [Reconocer]  │
│   ├─ Pastel (queque) — 3un / 5un mín   [Comprar] [Reconocer]  │
│   └─ Queso fresco — 4.5kg / 6kg mín    [Comprar] [Reconocer]  │
│                                                                  │
│ ℹ️  A REPONER (próximas 48h)                                    │
│   └─ Jamón serrano — 6kg / 5kg mín     [Comprar]              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ VISTA 4: BALANZAS (ESTADO DE ESTACIONES)

**Ruta:** `/gerente/balanzas`  
**Prioridad:** P2  
**Descripción:** Estado en tiempo real de las 4 balanzas + caja

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ ESTADO DE BALANZAS Y CAJA                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────┐│
│  │ BALANZA 1         │ │ BALANZA 2         │ │ BALANZA 3     ││
│  │ ✅ Activa         │ │ ✅ Activa         │ │ ⚠️ Error      ││
│  │                   │ │                   │ │               ││
│  │ Operador: José    │ │ Operadora: María  │ │ (desconectada)││
│  │ Transacciones: 12 │ │ Transacciones: 10 │ │               ││
│  │ Ventas hoy: $48k  │ │ Ventas hoy: $42k  │ │               ││
│  │                   │ │                   │ │ [Reconectar]  ││
│  │ IP: 192.168.1.10  │ │ IP: 192.168.1.11  │ │               ││
│  │ FW: v2.1.3        │ │ FW: v2.1.3        │ │ IP: 192.1...  ││
│  │ Último evento:     │ │ Último evento:     │ │ FW: v2.1.3    ││
│  │ 14:35 (hace 2min) │ │ 14:32 (hace 5min) │ │ Último evento: ││
│  │                   │ │                   │ │ 12:15 (hoy)   ││
│  └───────────────────┘ └───────────────────┘ └───────────────┘│
│                                                                  │
│  ┌───────────────────┐ ┌───────────────────┐                  │
│  │ BALANZA 4         │ │ CAJA              │                  │
│  │ ✅ Activa         │ │ ✅ OK             │                  │
│  │                   │ │                   │                  │
│  │ Operador: Pedro   │ │ Estado: ✅ Activa │                  │
│  │ Transacciones: 14 │ │ Cajero: Pedro     │                  │
│  │ Ventas hoy: $52k  │ │ Transacciones: 30 │                  │
│  │                   │ │ Ventas hoy: $125k │                  │
│  │ IP: 192.168.1.12  │ │ IP: 192.168.1.13  │                  │
│  │ FW: v2.1.3        │ │ FW: v3.0.1        │                  │
│  │ Último evento:     │ │ Último evento:     │                  │
│  │ 14:40 (ahora)     │ │ 14:41 (ahora)     │                  │
│  └───────────────────┘ └───────────────────┘                  │
│                                                                  │
│ VENTAS POR BALANZA (comparativa)                               │
│ ╔════════════════════════════════════════════════════════════╗ │
│ ║ Bal. 1: ████████████░░  $48k                               ║ │
│ ║ Bal. 2: ██████████░░░░  $42k                               ║ │
│ ║ Bal. 3: ░░░░░░░░░░░░░░  $0                                ║ │
│ ║ Bal. 4: █████████████░  $52k                               ║ │
│ ║ Caja:   ██████████████  $125k                              ║ │
│ ╚════════════════════════════════════════════════════════════╝ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📈 VISTA 5: REPORTES Y ANALÍTICAS

**Ruta:** `/gerente/reportes`  
**Prioridad:** P2  
**Descripción:** Analytics avanzados con filtros y exportación

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ REPORTES Y ANALÍTICAS                                           │
├─────────────────────────────────────────────────────────────────┤
│ Período: [06 abr - 06 abr ▼]  Balanza: [Todas ▼]  [Exportar PDF]│
│                                                                  │
│ ┌─────────────┬─────────────┬──────────────┐                   │
│ │ Ventas      │ Transac.    │ Mejor Día    │                   │
│ │ $1.234.500  │ 42          │ $1.234.500   │                   │
│ └─────────────┴─────────────┴──────────────┘                   │
│                                                                  │
│ COMPARATIVA SEMANAL (esta semana vs semana pasada)             │
│ ╔════════════════════════════════════════════════════════════╗ │
│ ║ $ 350k  ╱╲                ← Semana actual (marca)        ║ │
│ ║         ╱  ╲              ← Semana pasada (tenue)        ║ │
│ ║   ╱╲ ╱╲╱    ╲                                            ║ │
│ ║  ╱  ╲╱      ╲╱             (mejor rendimiento)           ║ │
│ ║ Lun Mar Mié Jue Vie Sáb Dom                             ║ │
│ ╚════════════════════════════════════════════════════════════╝ │
│                                                                  │
│ MOVIMIENTO DE INVENTARIO (entrada vs salida)                   │
│ ╔════════════════════════════════════════════════════════════╗ │
│ ║ kg  50                                                    ║ │
│ ║     ├─ Entradas (verde)  ╱╲                            ║ │
│ ║ 25  │                   ╱  ╲                            ║ │
│ ║     │                  ╱    ╲    ← Salidas (rojo)       ║ │
│ ║  0  └─────────────────╱──────╲────────────────────────║ │
│ ║     Lun  Mar  Mié  Jue  Vie                             ║ │
│ ╚════════════════════════════════════════════════════════════╝ │
│                                                                  │
│ TOP 10 PRODUCTOS (período)                                      │
│ ╔════════════════════════════════════════════════════════════╗ │
│ ║ 1. Pollo (filete)    ██████████████░░  $125k (182 kg)   ║ │
│ ║ 2. Carne (costilla)  ██████████░░░░░░  $89.5k (142 kg)  ║ │
│ ║ 3. Pastel (queque)   ██████░░░░░░░░░░  $65.2k (155 un) ║ │
│ ║ 4. Verdura (lechu.)  ████░░░░░░░░░░░░  $34.8k (58 kg)  ║ │
│ ║ 5. Fruta (plátano)   ███░░░░░░░░░░░░░  $28.5k (48 kg)  ║ │
│ ╚════════════════════════════════════════════════════════════╝ │
│                                                                  │
│ DESGLOSE POR MÉTODO DE PAGO                                     │
│ ╔═════════╦═════════╦═════════╦═════════╗                     │
│ ║ Efectivo║ Débito  ║ Crédito ║ Transf. ║                     │
│ ║ 35%     ║ 40%     ║ 20%     ║ 5%      ║                     │
│ ║ $432k   ║ $494k   ║ $247k   ║ $62k    ║                     │
│ ╚═════════╩═════════╩═════════╩═════════╝                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Export Button

Clickeable "Exportar PDF" genera un reporte de una página con:
- Resumen KPIs del período
- 2-3 gráficos principales
- Detalles de productos top
- Timestamp y firma del gerente

---

## 👥 VISTA 6: GESTIÓN DE USUARIOS

**Ruta:** `/gerente/usuarios`  
**Prioridad:** P3  
**Descripción:** CRUD de usuarios + roles + asignación de balanzas

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ GESTIÓN DE USUARIOS                                             │
├─────────────────────────────────────────────────────────────────┤
│ 🔍 Buscar por nombre/RUT                [+ Agregar Usuario]    │
├────────────┬──────────────┬──────────┬──────────┬──────────┬────┤
│RUT         │Nombre        │Rol       │Balanza   │Últ.Acceso│Acc │
├────────────┼──────────────┼──────────┼──────────┼──────────┼────┤
│12.345.678-9│Giuliano L.   │👑 Gerente│—         │14:50 hoy │ ⚙️  │
│12.345.679-8│José Pérez    │👤 Operador│Bal. 1   │14:35 hoy │ ⚙️  │
│12.345.680-7│María González│👤 Operador│Bal. 2   │14:32 hoy │ ⚙️  │
│12.345.681-6│Pedro López   │💳 Cajero  │Caja     │14:41 hoy │ ⚙️  │
│12.345.682-5│Ana Rodríguez │👤 Operador│Bal. 4   │Nunca     │ ⚙️  │
│12.345.683-4│Carlos Ruiz   │👑 Supervisor│—      │Ayer 09:30│ ⚙️  │
└────────────┴──────────────┴──────────┴──────────┴──────────┴────┘
```

**Rol badges:**
- 👑 Gerente (azul)
- 👤 Operador (verde)
- 💳 Cajero (cyan)
- 📊 Supervisor (púrpura)

### Modal Editar/Crear Usuario

```
┌──────────────────────────────────────────┐
│ Editar Usuario: José Pérez              │
├──────────────────────────────────────────┤
│ RUT:               12.345.679-8          │
│ Nombre:            [José]                │
│ Apellido:          [Pérez]               │
│ Email:             [jose@example.com]    │
│ Contraseña:        [●●●●●●●●] [Cambiar] │
│ Rol:               [Operador ▼]          │
│ Asignar a Balanza: [Balanza 1 ▼]         │
│ Estado:            [✅ Activo]            │
│                                          │
│ [Guardar]  [Desactivar]  [Cancelar]     │
└──────────────────────────────────────────┘
```

---

## 🔐 VISTA 7: CIERRE DEL DÍA

**Ruta:** `/gerente/cierre`  
**Prioridad:** P3  
**Descripción:** Wizard 3 pasos para cerrar el día con reconciliación

### Paso 1: Resumen del Día

```
┌──────────────────────────────────────────────────┐
│ CIERRE DEL DÍA - Paso 1: Resumen                 │
├──────────────────────────────────────────────────┤
│ Fecha: 6 de abril, 2026                          │
│                                                  │
│ ┌─────────────────┬──────────────────────────┐  │
│ │ Ventas del Día  │ $1.234.500               │  │
│ │ Transacciones   │ 42                       │  │
│ │ Boletas Emit.   │ 41                       │  │
│ │ Facturas Emit.  │ 1                        │  │
│ │ Anulaciones     │ 2                        │  │
│ └─────────────────┴──────────────────────────┘  │
│                                                  │
│ Detalles por método de pago:                     │
│ • Efectivo:      $432.500 (35%)                  │
│ • Débito:        $494.000 (40%)                  │
│ • Crédito:       $247.000 (20%)                  │
│ • Transferencia: $62.000  (5%)                   │
│                                                  │
│ [Siguiente →]                                   │
└──────────────────────────────────────────────────┘
```

### Paso 2: Reconciliación de Caja

```
┌──────────────────────────────────────────────────┐
│ CIERRE DEL DÍA - Paso 2: Reconciliación          │
├──────────────────────────────────────────────────┤
│ Esperado (según sistema):  $432.500             │
│ Contado (efectivo físico): [_________]           │
│                                                  │
│ Diferencia:  $ 0                                 │
│ Estado:     ✅ Coincide perfecto                 │
│                                                  │
│ ⚠️ Si hay diferencia > $5.000:                   │
│    Advertencia: "Revisar transacciones"         │
│    Bloquea avance a paso 3 hasta resolver        │
│                                                  │
│ [← Atrás]  [Siguiente →]                        │
└──────────────────────────────────────────────────┘
```

### Paso 3: Confirmación Final

```
┌──────────────────────────────────────────────────┐
│ CIERRE DEL DÍA - Paso 3: Confirmación Final      │
├──────────────────────────────────────────────────┤
│ Fecha:              6 de abril, 2026              │
│ Hora de cierre:     14:50                        │
│ Cerrado por:        Giuliano Larosa              │
│                                                  │
│ Resumen final:                                   │
│ • Ventas:          $1.234.500                    │
│ • Transacciones:   42                            │
│ • Boletas emitidas: 41                           │
│ • Caja balanceada: ✅ Sí                          │
│ • PDF generado:    Sí                            │
│                                                  │
│ ⚠️ CONFIRMACIÓN: Escribe "CONFIRMAR" para        │
│    bloquear este cierre                          │
│    [_________________]                          │
│                                                  │
│ [← Atrás]  [CONFIRMAR CIERRE]                   │
└──────────────────────────────────────────────────┘
```

### Resultado Modal

```
┌──────────────────────────────────────────────────┐
│ ✅ CIERRE COMPLETADO                             │
├──────────────────────────────────────────────────┤
│ Cierre del 6 de abril generado exitosamente      │
│                                                  │
│ PDF disponible para descargar:                   │
│ cierre_2026-04-06_gerente.pdf (142 KB)           │
│                                                  │
│ Los datos están ahora bloqueados y no pueden     │
│ modificarse.                                     │
│                                                  │
│ [Descargar PDF]  [Ir al Panel]                  │
└──────────────────────────────────────────────────┘
```

---

## 🎯 COMPONENTES REUTILIZABLES

### KpiCard.vue
Props: `label`, `value`, `icon`, `trend`, `accentColor`

### StockLevelBar.vue
Props: `current`, `minimum`, `unit` → renderiza barra visual coloreada

### TransactionTable.vue
Props: `transactions`, `filters` → tabla paginada con click handlers

### StatusBadge.vue
Props: `status` → badge coloreado (✅ verde, ❌ rojo, ⚠️ amarillo)

### StationCard.vue
Props: `station` → card con status + info operador

### DateRangePicker.vue
Props: `range`, `onChange` → selector de rango de fechas

---

## 📱 RESPONSIVE DESIGN

- **Mobile (<768px):** 1 columna, sidebar → hamburger drawer, cards stack vertically
- **Tablet (768px-1024px):** 2 columnas, sidebar colapsado a icons
- **Desktop (>1024px):** 3+ columnas, sidebar full

KPI cards:
- Mobile: 4 stacked (fullwidth)
- Tablet: 2x2 grid
- Desktop: 4 en fila

Charts:
- Mobile: 1 col (apiladas)
- Tablet/Desktop: 2 cols

---

## ⚡ COMPORTAMIENTO EN TIEMPO REAL

- **WebSocket:** Conexión en `ManagerLayout.vue` → events a Pinia stores
- **Live indicator:** Pulsing green dot cuando WS conectado
- **Transacciones:** Nueva fila se anima desde arriba (Transition)
- **KPIs:** Se actualizan cada 15 segundos (polling fallback)
- **Alertas:** Aparecen en tiempo real cuando stock cae bajo mínimo

---

## 📚 ESTRUCTURA DE CARPETAS PARA JONATHAN

```
comerciales-frontend/
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/index.ts
│   ├── stores/
│   │   ├── auth.store.ts
│   │   ├── dashboard.store.ts
│   │   ├── transactions.store.ts
│   │   └── ...
│   ├── types/
│   │   ├── index.ts
│   │   ├── kpi.types.ts
│   │   ├── transaction.types.ts
│   │   └── ...
│   ├── services/
│   │   ├── api.client.ts
│   │   ├── websocket.service.ts
│   │   └── ...
│   ├── composables/
│   │   ├── useRealtime.ts
│   │   ├── useKPIs.ts
│   │   └── ...
│   ├── layouts/
│   │   └── ManagerLayout.vue
│   ├── components/
│   │   ├── ui/
│   │   ├── layout/
│   │   ├── kpi/
│   │   ├── charts/
│   │   ├── transactions/
│   │   ├── inventory/
│   │   ├── stations/
│   │   ├── users/
│   │   ├── reports/
│   │   └── cierre/
│   ├── views/
│   │   ├── DashboardView.vue
│   │   ├── TransactionsView.vue
│   │   ├── InventoryView.vue
│   │   ├── StationsView.vue
│   │   ├── ReportsView.vue
│   │   ├── UsersView.vue
│   │   └── CierreView.vue
│   ├── mocks/
│   │   ├── kpis.json
│   │   ├── transactions.json
│   │   ├── products.json
│   │   ├── stations.json
│   │   └── ...
│   └── styles/
│       └── tailwind.css
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── .env
```

---

## 🚀 SIGUIENTE PASO

Jonathan clona el repo, instala dependencias, y ejecuta:

```bash
npm run dev
```

Debería ver:
1. Sidebar con 7 nav items
2. Panel General con KPI cards + charts + alertas
3. Mock data actualizado cada 15s (simulando tiempo real)
4. Routing funcional entre todas las vistas

---

**Versión:** 0.1-MVP  
**Última actualización:** 6 de abril, 2026  
**Siguiente:** Código base Vue 3 en siguiente documento
