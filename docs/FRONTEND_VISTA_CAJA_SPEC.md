# FRONTEND — ESPECIFICACIÓN VISTA CAJA
## Sistema de Inventario Dinámico — Locales Comerciales Chile

**Para:** Equipo Frontend (Jonathan) + PM (Giuliano)
**Fecha:** 2026-04-12
**Estado:** Diseño aprobado — listo para codear
**Demo:** `comerciales-frontend/caja-demo.html` (abrir directo en navegador)

---

## 1. CONTEXTO DE NEGOCIO

### Hardware involucrado
| Dispositivo | Modelo | Rol |
|---|---|---|
| Balanza etiquetadora | Digi SM-110 (×4) | Pesa productos, empuja pre-boletas por red |
| Escáner de códigos | Well2303 Barcode Scanner | Escanea QR de bouchers y EAN-13 de productos |
| Terminal de caja | PC con mouse + teclado | Corre el frontend Vue 3 |

### Flujo core
```
Balanza SM-110
  └─ Operador pesa producto
  └─ Sistema genera PreBoleta (UUID) + imprime boucher físico
  └─ Envía pre-boleta por red → backend → caja recibe notificación

Caja (Well2303 escanea QR del boucher)
  └─ Frontend recupera PreBoleta por UUID
  └─ Muestra ítems al cajero
  └─ Cajero puede modificar ítems + agregar productos por código de barras
  └─ Cajero puede unir múltiples pre-boletas en una sola venta
  └─ Selecciona método de pago → confirma
  └─ Backend: descuenta stock + crea Sale + DTE pendiente SII
```

---

## 2. ARQUITECTURA FRONTEND

### Repositorio: `comerciales-frontend`
**Stack:**
- Vue 3 + Vite + TypeScript
- Pinia (state management) + `pinia-plugin-persistedstate` (offline)
- Vue Router 4 (rutas protegidas por rol)
- TanStack Vue Query (cache + sincronización API)
- Axios (HTTP client + interceptor JWT)
- Tailwind CSS 3 + Radix Vue (componentes)
- ApexCharts (gráficos en dashboard)

### Modelo de acceso — Una sola app, vistas por rol

```
/login                    ← pública
/caja                     ← roles: admin, supervisor, cajero
/gerente/                 ← roles: admin, supervisor
  ├── dashboard
  ├── transacciones
  ├── inventario
  ├── balanzas
  ├── reportes
  ├── usuarios
  └── cierre
```

El rol viene en el JWT. El router guard redirige según `user.rol`:
- `cajero` → `/caja`
- `admin` / `supervisor` → `/gerente` (y puede acceder a `/caja`)
- `operador_balanza` → no existe en el frontend de caja (usa la balanza física)

---

## 3. ESTADOS DE LA VISTA CAJA

La vista caja es una sola pantalla (`/caja`) con 5 estados mutuamente excluyentes:

```
IDLE ──── escanea QR ──────────────────────────────► ACTIVA
  ▲                                                      │
  │        escanea 2° QR mientras hay venta activa       │
  │          ├─ "Unir" ──────── agrega ítems ────────────┤
  │          └─ "Nueva tab" ── abre tab paralelo ─────►  │
  │                                                      │
  │                                            cajero confirma
  │                                                      │
  │                                               PROCESANDO
  │                                                      │
  └──── "Nueva venta" ◄──────────── ÉXITO / ERROR ◄─────┘
```

### Estado 1: IDLE
**Cuándo:** No hay ninguna venta activa en pantalla.

**Elementos:**
- Input de scanner siempre con foco (captura input del Well2303)
- Cola de pre-boletas pendientes de las 4 balanzas (polling cada 5s)
- Cada tarjeta de balanza muestra: nombre, total CLP, cantidad ítems, tiempo de espera
- Tarjetas con espera > 5 min se muestran con borde y texto en `warning-400`
- Clic en tarjeta de balanza → abre esa pre-boleta en estado ACTIVA

**Lógica del scanner input:**
```
Input recibe código + Enter (el Well2303 añade Enter automáticamente)
  ├── Código es UUID (36 chars, formato xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
  │     └─► GET /api/v1/preboleta/{uuid} → abre en estado ACTIVA
  └── Código es EAN-13 (13 dígitos numéricos)
        └─► GET /api/v1/products?codigo_barras={ean} → abre nueva venta con ese producto
```

---

### Estado 2: ACTIVA
**Cuándo:** Hay al menos una pre-boleta cargada y en proceso de cobro.

**Layout:**
```
┌──────────────────────────────────────┬────────────────┐
│  Header: origen + controles          │                │
├──────────────────────────────────────┤  Panel cobro   │
│                                      │  (w-72, fijo)  │
│  Tabla de ítems (scroll)             │                │
│                                      │                │
├──────────────────────────────────────┤                │
│  Footer: agregar producto            │  [COBRAR]      │
└──────────────────────────────────────┴────────────────┘
```

**Header de la venta:**
- Identificador de pre-boleta (UUID parcial), origen (Balanza N), tiempo transcurrido
- Badge "Unidas × N" cuando hay pre-boletas fusionadas (ver sección Merge)
- Botón **"Unir pre-boleta"** — abre modal de merge
- Botón **"Cancelar"** — libera la pre-boleta (estado → `cancelada` en backend) y vuelve a IDLE

**Tabla de ítems:**
- Columnas: Producto | Cant. | P/U | Total | (botón editar — aparece en hover)
- Snapshot del nombre del producto al momento de pesar (no el nombre actual del catálogo)
- Botón editar → abre modal de edición (Estado 2b)

**Panel de cobro (lado derecho):**
- Subtotal (neto), IVA 19%, Total en CLP
- 4 botones de método de pago: Efectivo, Débito, Crédito, Transferencia
- Al seleccionar Efectivo → aparece sub-panel con campo "Monto recibido" + cálculo de vuelto
- Botón COBRAR → pasa a estado PROCESANDO

**Footer:**
- Botón "Agregar producto" → el cajero escanea con el Well2303 o busca por nombre

---

### Estado 2b: EDICIÓN DE ÍTEM (modal sobre ACTIVA)
**Cuándo:** El cajero hace clic en el ícono de editar de un ítem.

**Elementos:**
- Nombre y precio/unidad del producto
- Input de cantidad con botones `+` / `−`
  - Paso: `0.001` para productos KG, `1` para unidades
- Subtotal calculado en tiempo real
- Botón "Eliminar ítem"
- Botón "Guardar cambio"

---

### Estado 3: PROCESANDO
**Cuándo:** El cajero presionó COBRAR, se está enviando la venta al backend.

**Elementos:**
- Spinner centrado
- Texto "Registrando venta..."
- Todo el UI deshabilitado (no se puede interactuar)
- Auto-avanza a ÉXITO cuando el backend responde 200

**En modo offline:**
- No hace llamada al backend
- Guarda la venta en IndexedDB / localStorage
- Auto-avanza a ÉXITO igual (con indicador de "guardado sin conexión")

---

### Estado 4: ÉXITO / ERROR
**Cuándo:** La venta fue procesada (exitosa u offline).

**Éxito con conexión:**
- Checkmark animado
- Resumen: total CLP, método de pago, origen, N° ítems
- Folio DTE: "Pendiente SII" (se confirma cuando Celery procesa la tarea)
- Countdown de 3 segundos → vuelve automáticamente a IDLE
- Botones: "Nueva venta" (inmediato) y "Ver detalle"

**Éxito sin conexión:**
- Mismo layout pero con badge "Guardado sin conexión"
- Texto: "Se sincronizará al recuperar la red"

**Error:**
- Ícono de advertencia
- Mensaje de error del servidor
- Botón "Reintentar" → vuelve a estado PROCESANDO
- Botón "Guardar sin conexión" → guarda en cola local y vuelve a IDLE

---

## 4. SISTEMA DE TABS (MÚLTIPLES VENTAS ACTIVAS)

### Estructura
Cada pre-boleta abierta ocupa un tab. Pueden coexistir varias simultáneamente.

```
[Balanza 1 · $21.350 ●]  [Balanza 3 · $3.200]  [+ Nueva venta]
```

- **Tab activo:** borde inferior `brand-500`, fondo `surface2`
- **Tab inactivo:** sin borde, texto `secondary`; hover sobre tab inactivo → aparece botón `⇄ Unir`
- **`●` indicador:** presente en todos los tabs con ítems pendientes de cobrar
- **`✕` cerrar:** cancela esa pre-boleta y cierra el tab

### Pinia store: `caja.store.ts`
```typescript
interface VentaActiva {
  uuid: string           // UUID de la pre-boleta raíz
  stationName: string    // "Balanza 1"
  items: VentaItem[]
  mergedUuids: string[]  // UUIDs absorbidos si hay unión
  isMerged: boolean
  createdAt: string
}

interface CajaStore {
  ventas: VentaActiva[]   // una por tab abierto
  activeVentaUuid: string | null
  isOffline: boolean
  pendingSync: VentaSinConexion[]
}
```

---

## 5. FLUJO DE UNIÓN DE PRE-BOLETAS (MERGE)

### Cuándo ocurre
Un cliente pasa dos veces por la balanza (olvidó algo). La caja tiene dos bouchers del mismo cliente y el cajero quiere cobrar todo junto en una sola transacción.

### Dos formas de disparar el merge

**Forma A — Escanear 2° QR con venta activa:**
El Well2303 escanea el segundo boucher mientras ya hay una venta en pantalla.
El sistema detecta que el código es un UUID de pre-boleta (no un EAN-13) y pregunta.

**Forma B — Botón "Unir pre-boleta" en el header:**
El cajero tiene dos tabs abiertos manualmente y presiona "Unir" desde el header de la venta activa.
También: hover sobre un tab inactivo → aparece botón `⇄ Unir` directamente en el tab.

### Modal de merge

```
┌─────────────────────────────────────────────────────┐
│  Pre-boleta detectada                          [✕]  │
│  Ya tienes una venta activa. ¿Qué deseas hacer?     │
├──────────────────┬──────────────────────────────────┤
│  Venta activa    │  Nueva pre-boleta                │
│  Balanza 1       │  Balanza 3                       │
│  $21.350 · 4 it. │  $3.200 · 1 ítem                │
├──────────────────┴──────────────────────────────────┤
│  Vista previa si unes:                              │
│  5 ítems · Total $24.550                            │
├─────────────────────────────────────────────────────┤
│  [⇄ Unir a venta actual — $24.550]                  │  ← primario
│  [□ Abrir en pestaña separada]                      │  ← secundario
└─────────────────────────────────────────────────────┘
```

### Qué pasa al confirmar "Unir"

1. Los ítems de la 2ª pre-boleta se agregan al final de la lista de la venta activa
2. Los ítems se mezclan en una sola lista sin distinción de origen
3. El tab de la 2ª pre-boleta desaparece
4. El tab activo cambia de label: `Bal. 1 · $21.350` → `Bal. 1+3 · $24.550`
5. Aparece badge **"Unidas × 2"** en el header de la venta
6. Flash visual en la tabla (fondo `brand-500/10` durante 600ms)
7. La 2ª pre-boleta queda en estado `procesada` en el backend al confirmar la venta

### Qué pasa al "Abrir en pestaña separada"
El tab de la 2ª pre-boleta se crea/activa normalmente. El cajero puede volver al tab 1 y cobrar primero, luego cobrar el tab 2 por separado.

---

## 6. MODO OFFLINE

### Cuándo se activa
- El interceptor Axios detecta error de red (`ERR_NETWORK`) o timeout
- Se muestra banner amarillo en la parte superior: _"Sin conexión — N ventas en cola"_
- Indicador en topbar cambia de `● En línea` a `● Sin conexión`

### Qué funciona sin conexión
| Función | Offline |
|---|---|
| Escanear QR y cargar pre-boleta | ✗ (requiere backend) |
| Ver ítems de pre-boleta ya cargada | ✓ (en memoria) |
| Modificar ítems | ✓ |
| Registrar venta | ✓ (guarda en cola local) |
| Sincronizar al recuperar red | ✓ (automático) |
| Ver cola de pre-boletas pendientes | ✗ (requiere polling) |

### Almacenamiento local
- **`pinia-plugin-persistedstate`** persiste el store de caja en `localStorage`
- Las ventas sin conexión se guardan en `localStorage` bajo la key `caja:pending_sync`
- Al recuperar conexión: TanStack Query reintenta y vacía la cola

---

## 7. COMPONENTES A CONSTRUIR

```
src/
├── views/
│   └── CajaView.vue                ← vista raíz, maneja estado global de la caja
│
├── components/caja/
│   ├── CajaTopbar.vue              ← topbar específico de caja (distinto al de /gerente)
│   ├── PreboletaTabs.vue           ← barra de tabs + botón nueva venta
│   ├── ScannerInput.vue            ← input global, captura QR y EAN-13
│   ├── ItemsList.vue               ← tabla de ítems con botones editar en hover
│   ├── PaymentPanel.vue            ← panel derecho: resumen + método de pago + cobrar
│   ├── CashSubPanel.vue            ← sub-panel de efectivo con vuelto y botones rápidos
│   ├── PreboletaQueue.vue          ← cola de balanzas en estado IDLE
│   ├── SaleResult.vue              ← pantalla éxito/error con countdown
│   ├── EditItemModal.vue           ← modal edición de ítem
│   └── MergeModal.vue              ← modal de unión de pre-boletas
│
├── stores/
│   ├── auth.store.ts               ← usuario, token JWT, logout
│   └── caja.store.ts               ← ventas activas, tabs, offline queue
│
└── api/
    ├── client.ts                   ← instancia axios + interceptor JWT + offline
    ├── auth.ts                     ← login, me
    ├── preboleta.ts                ← get by uuid, create, cancel
    ├── sales.ts                    ← POST /sales
    └── products.ts                 ← get by barcode (para scanner EAN-13)
```

---

## 8. ENDPOINTS QUE CONSUME LA VISTA CAJA

| Acción | Método | Endpoint | Estado backend |
|---|---|---|---|
| Cargar pre-boleta por QR | GET | `/api/v1/preboleta/{uuid}` | PENDIENTE |
| Crear pre-boleta manual | POST | `/api/v1/preboleta` | PENDIENTE |
| Cancelar pre-boleta | PATCH | `/api/v1/preboleta/{uuid}/cancel` | PENDIENTE |
| Buscar producto por EAN | GET | `/api/v1/products?codigo_barras={ean}` | PENDIENTE |
| Confirmar venta | POST | `/api/v1/sales` | PENDIENTE |
| Poll pre-boletas pendientes | GET | `/api/v1/preboleta?estado=pendiente` | PENDIENTE |

**Nota:** Ninguno de estos endpoints existe aún en el backend. El frontend debe ser construido con mocks y conectarse cuando el backend los entregue. Ver `BACKEND_ESTADO_ACTUAL.md` sección 9.

### Body de confirmación de venta (POST /sales)
```json
{
  "preboleta_uuid": "9a3f-b821-...",
  "merged_uuids": ["c7d2-f190-..."],
  "station_id": "uuid-de-la-caja",
  "cajero_id": "uuid-del-cajero",
  "metodo_pago": "debito",
  "items": [
    {
      "product_id": "uuid-o-null",
      "nombre_producto": "Jamón campo mitad",
      "cantidad": 0.500,
      "precio_unitario": 10101,
      "precio_total": 5050
    }
  ],
  "total_clp": 24550
}
```

---

## 9. TIPOS TYPESCRIPT (VISTA CAJA)

Estos tipos reemplazan / complementan los de `src/types/index.ts` actuales, alineados con el backend real:

```typescript
// Roles del backend (reemplaza 'gerente'|'operador' del archivo actual)
export type UserRol = 'admin' | 'supervisor' | 'cajero' | 'operador_balanza'

// Unidades de medida del backend
export type Unidad = 'UN' | 'KG' | 'L' | 'PAQ' | 'BOL' | 'TAB'

// Métodos de pago del backend
export type MetodoPago = 'efectivo' | 'debito' | 'credito' | 'transferencia'

// Estado de pre-boleta
export type PreBoletaEstado = 'pendiente' | 'procesada' | 'expirada' | 'cancelada'

// Ítem de venta en la caja (snapshot)
export interface VentaItem {
  product_id:      string | null
  nombre_producto: string
  cantidad:        number
  unidad:          Unidad
  precio_unitario: number      // CLP entero
  precio_total:    number      // CLP entero
  supplier?:       string      // solo para display
}

// Pre-boleta que llega del backend
export interface PreBoleta {
  id:          string           // UUID = el QR
  station_id:  string
  operator_id: string | null
  estado:      PreBoletaEstado
  total_clp:   number
  expires_at:  string | null
  items:        VentaItem[]
  created_at:  string
}

// Venta activa en el store de caja
export interface VentaActiva {
  uuid:          string         // UUID de la pre-boleta raíz
  stationName:   string
  items:         VentaItem[]
  mergedUuids:   string[]       // UUIDs absorbidos
  isMerged:      boolean
  createdAt:     string
}

// Venta guardada sin conexión
export interface VentaSinConexion {
  localId:      string          // generado localmente
  ventaActiva:  VentaActiva
  metodoPago:   MetodoPago
  totalClp:     number
  savedAt:      string
  synced:       boolean
}
```

---

## 10. ORDEN DE IMPLEMENTACIÓN RECOMENDADO

### Semana 1 — Infraestructura + Auth (sin backend real)
```
1. src/types/index.ts              → actualizar tipos al modelo real del backend
2. src/api/client.ts               → axios instance + interceptor JWT + manejo offline
3. src/api/auth.ts                 → login/me con mock
4. src/stores/auth.store.ts        → usuario, token, logout, persistedstate
5. src/views/LoginView.vue         → formulario email + password
6. src/router/index.ts             → guards por rol, redirect según UserRol
```

### Semana 1-2 — Vista Caja core (con mocks)
```
7.  src/stores/caja.store.ts       → ventas activas, tabs, offline queue
8.  src/api/preboleta.ts           → con datos mock (BASE_ITEMS del demo)
9.  src/views/CajaView.vue         → shell con máquina de estados
10. src/components/caja/ScannerInput.vue
11. src/components/caja/PreboletaTabs.vue
12. src/components/caja/ItemsList.vue
13. src/components/caja/EditItemModal.vue
14. src/components/caja/PaymentPanel.vue + CashSubPanel.vue
15. src/components/caja/MergeModal.vue    ← flujo de unión
16. src/components/caja/SaleResult.vue
17. src/components/caja/PreboletaQueue.vue
```

### Semana 2-3 — Integración con backend + Vista Gerente
```
18. Conectar api/preboleta.ts a endpoints reales (cuando backend los entregue)
19. Conectar api/sales.ts
20. Implementar offline queue real con sync automático
21. Vista Inventario — CRUD de productos
22. Vista Transacciones — listado + detalle
23. Conectar Dashboard a API real
```

---

## 11. DECISIONES DE DISEÑO CONFIRMADAS

| Decisión | Detalle |
|---|---|
| Tema | Dark mode (colores en tailwind.config.js del repo) |
| Resolución objetivo | 1280×800 mínimo, mouse + teclado |
| Múltiples ventas | Sistema de tabs, sin límite definido |
| Merge de pre-boletas | Ítems se mezclan en lista plana, sin distinción de origen |
| Escaneo con venta activa | Modal de decisión: Unir / Nueva tab |
| Cobro efectivo | Campo "Monto recibido" + cálculo de vuelto + botones rápidos |
| Offline | Guarda en cola local, sincroniza automáticamente al reconectar |
| Pre-boletas de balanza | Polling cada 5 segundos a GET /preboleta?estado=pendiente |
| Timeout de pre-boleta | Controlado por `expires_at` del backend |
| Cancelar venta | Libera la pre-boleta (estado → cancelada en backend) |

---

**Demo visual:** `comerciales-frontend/caja-demo.html`
**Spec backend:** `comerciales-docs/docs/BACKEND_ESTADO_ACTUAL.md`
**Próximo paso:** Iniciar Semana 1 del orden de implementación
