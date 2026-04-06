# GUÍA DE FLUJO OPERACIONAL
## Sistema de Inventario Dinámico - Para Operarios

**Para:** Operadores, Cajeros, Gerentes  
**Versión:** 0.1-MVP  
**Idioma:** Español  
**Última actualización:** 5 de abril 2026  

---

## 👥 ROLES & RESPONSABILIDADES

### 👤 OPERADOR DE BALANZA
**¿Quién?** Persona en la zona de pesaje/balanza (4 estaciones)  
**¿Qué hace?** Escanea productos y agrega a la orden del cliente

**Privilegios:**
- ✅ Ver sus 4 estaciones asignadas
- ✅ Escanear códigos de barra (agregar items)
- ✅ Ver pre-boleta en tiempo real en pantalla
- ✅ Generar QR cuando cliente termina
- ❌ NO puede: ver precios totales, editar inventario, emitir boletas

### 👤 CAJERO
**¿Quién?** Persona en la caja/POS  
**¿Qué hace?** Recibe QR, confirma venta, emite boleta

**Privilegios:**
- ✅ Escanear QR de clientes
- ✅ Ver detalle completo de la compra
- ✅ Seleccionar método de pago
- ✅ Confirmar venta
- ✅ Ver boleta emitida
- ❌ NO puede: editar precios, modificar items ya confirmados

### 👤 GERENTE
**¿Quién?** Dueño o encargado del local  
**¿Qué hace?** Supervisa, ve reportes, toma decisiones basadas en datos

**Privilegios:**
- ✅ Ver dashboard en tiempo real
- ✅ Reportes de ventas
- ✅ Alertas de stock bajo
- ✅ Crear/editar productos
- ✅ Crear usuarios (operadores, cajeros)
- ✅ Ver auditoría de transacciones
- ❌ NO puede: emitir boletas, modificar transacciones confirmadas

---

## 🎯 FLUJO DE VENTA PASO A PASO

### ETAPA 1: CLIENTE LLEGA CON SUS PRODUCTOS

#### Operador de Balanza

**Paso 1: Iniciar nueva orden**
1. Cliente se acerca a la **Estación 1, 2, 3 ó 4** (según disponibilidad)
2. Pantalla muestra: "Estación [N] - Listo para escanear"
3. Operador toca botón **[NUEVA ORDEN]** (si no sale automático)
4. Pantalla se limpia → lista para recibir items

```
┌─────────────────────────────────┐
│   ESTACIÓN 2 - NUEVA ORDEN      │
├─────────────────────────────────┤
│                                 │
│   Escanee primer producto       │
│                                 │
│                                 │
│   [Nueva Orden] [Cancelar]      │
└─────────────────────────────────┘
```

**Paso 2: Escanear primer producto**
1. Operador toma producto
2. Escanea código de barra (con escáner manual o lectora balanza)
3. **Sistema procesa automáticamente** (sin hacer clic)
4. Si balanza está disponible: operador coloca producto en balanza → balanza detecta peso
5. Si es producto simple (sin pesaje): un clic confirma cantidad = 1

```
┌─────────────────────────────────┐
│   ESTACIÓN 2 - TOMATEA          │
├─────────────────────────────────┤
│ Producto: Tomate                │
│ Precio: $2.50 USD / kg          │
│ Peso detectado: 2.3 kg          │
│                                 │
│ Subtotal: $5.75                 │
│                                 │
│ [Aceptar] [Reescanear]          │
└─────────────────────────────────┘
```

**Paso 3: Revisar pantalla del cliente**
- En pantalla cliente paralela, cliente ve su compra actualizada en TIEMPO REAL
- Operador va agregando productos

```
[PANTALLA CLIENTE - Lo que ve el cliente en tiempo real]
┌──────────────────────────────────┐
│   ESTACIÓN 2 - TU COMPRA         │
├──────────────────────────────────┤
│ Tomate × 2.3kg       $5.75       │
│                                  │
│ Subtotal: $5.75                  │
│ Total estimado: $5.75            │
│                                  │
│ [Quiero agregar más] [Listo]     │
└──────────────────────────────────┘
```

**Paso 4: Repetir para cada producto**
1. Operador continúa escaneando productos
2. Sistema suma a la orden
3. Pantalla cliente se actualiza en tiempo real (sin demora)
4. Cliente puede ver su compra actualizada

**Ejemplo: Cliente agrega tomate + pan + leche**

```
Transición 1:
OPERADOR escanea [Tomate] (2.3 kg)
    ↓ WebSocket (< 100ms)
PANTALLA CLIENTE se actualiza → muestra tomate + precio

Transición 2:
OPERADOR escanea [Pan Integral] (1 unit)
    ↓ WebSocket (< 100ms)
PANTALLA CLIENTE se actualiza → muestra tomate + pan + precio

Transición 3:
OPERADOR escanea [Leche] (1 litro)
    ↓ WebSocket (< 100ms)
PANTALLA CLIENTE se actualiza → muestra tomate + pan + leche + precio TOTAL
```

---

### ETAPA 2: CLIENTE DICE "LISTO"

#### Operador de Balanza (continúa)

**Paso 5: Cliente indica que terminó**
1. Cliente toca **[LISTO]** en pantalla
2. O dice "Listo" al operador → operador toca **[FINALIZAR ORDEN]**
3. Sistema genera **QR único** con todos los detalles

```
┌──────────────────────────────────────┐
│   ESTACIÓN 2 - ORDEN FINALIZADA      │
├──────────────────────────────────────┤
│                                      │
│          ┌─────────────┐             │
│          │  ▓▓▓▓▓▓▓▓▓ │  ← QR CODE  │
│          │  ▓▓▓▓▓▓▓▓▓ │             │
│          │  ▓▓▓▓▓▓▓▓▓ │             │
│          │  ▓▓▓▓▓▓▓▓▓ │             │
│          └─────────────┘             │
│                                      │
│   Código: ORD-20260405-000142        │
│   Total: $12.50                      │
│                                      │
│   PASE ESTE CÓDIGO A CAJA            │
│   PARA PAGAR                         │
│                                      │
│   [Imprimir QR] [Nueva Orden]        │
└──────────────────────────────────────┘
```

**Paso 6: Cliente recibe QR**
1. Sistema imprime QR en etiqueta o papel (o cliente fotografía)
2. Cliente lleva QR a la **CAJA** para pagar
3. Operador toca **[NUEVA ORDEN]** para limpiar estación → listo para próximo cliente

---

### ETAPA 3: CLIENTE VA A CAJA (CON QR)

#### Cajero

**Paso 7: Cajero escanea QR**
1. Cliente llega a caja con QR
2. Cajero toma escáner
3. Escanea QR del cliente
4. **Sistema retorna TODOS LOS DETALLES** (Tomate 2.3kg, Pan 1, Leche 1L, etc.)

```
[PANTALLA CAJA - Se despliega al escanear QR]
┌────────────────────────────────────────┐
│   TRANSACCIÓN - Cliente #142           │
├────────────────────────────────────────┤
│ QR: ORD-20260405-000142                │
│                                        │
│ Tomate × 2.3kg        $5.75            │
│ Pan integral × 1      $3.50            │
│ Leche × 1L            $2.50            │
│                                        │
│ Subtotal:             $11.75           │
│ IVA 19%:              $2.23            │
│ TOTAL A PAGAR:       $13.98            │
│                                        │
│ Método de pago:                        │
│ [Efectivo] [Débito] [Crédito] [Transfer]
│                                        │
│ [Confirmar Venta]                      │
└────────────────────────────────────────┘
```

**Paso 8: Cajero selecciona método de pago**
1. Cajero toca botón según tipo de pago:
   - **Efectivo:** Recibe dinero, calcula vuelto
   - **Débito/Crédito:** Pasa tarjeta por lector (si aplica)
   - **Transferencia:** Espera confirmación (puede quedar pendiente)

```
[Si elige EFECTIVO]
┌────────────────────────────────────────┐
│   EFECTIVO                             │
├────────────────────────────────────────┤
│ Total: $13.98                          │
│                                        │
│ Dinero recibido: $20.00                │
│                                        │
│ Vuelto: $6.02                          │
│                                        │
│ [Vuelto correcto - Confirmar]          │
│ [Ajustar monto]                        │
└────────────────────────────────────────┘
```

**Paso 9: Confirmar venta**
1. Cajero verifica vuelto/pago
2. Toca **[CONFIRMAR VENTA]**
3. **SISTEMA REALIZA TODO AUTOMÁTICAMENTE:**
   - ✅ Guarda transacción en base de datos
   - ✅ **DESCUENTA INVENTARIO** (tomate -2.3kg, pan -1, leche -1L)
   - ✅ Genera **boleta electrónica** (SII DTE) automáticamente
   - ✅ Registra auditoría (quién, qué, cuándo)

```
[PANTALLA CAJA - Después de CONFIRMAR]
┌────────────────────────────────────────┐
│   ✓ VENTA COMPLETADA                   │
├────────────────────────────────────────┤
│ Folio SII: 000142                      │
│ Hora: 15:47:23                         │
│ Monto: $13.98                          │
│ Vuelto: $6.02                          │
│                                        │
│ ✓ Boleta emitida                       │
│ ✓ Inventario actualizado               │
│ ✓ Auditoría registrada                 │
│                                        │
│ [Imprimir Boleta] [Email]              │
│ [Nueva Venta]                          │
└────────────────────────────────────────┘
```

**Paso 10: Entregar boleta**
1. Sistema imprime boleta o envía por email
2. Cajero entrega boleta a cliente
3. Cliente se va ✅

---

## 📊 SITUACIONES ESPECIALES

### Situación 1: Cliente quiere agregar MÁS productos (ya en caja)

**Escenario:** Cajero ya escaneó QR y ve detalle. Cliente: "Espera, quiero un producto más"

**Solución:**
1. Cajero toca **[Cancelar esta venta]** o **[Agregar items]**
2. **NO vuelve a estaciones** (innecesario)
3. Cajero puede:
   - Escanear barcode directamente en caja (si scanner permite)
   - O cliente regresa a estación para agregar
4. Sistema actualiza orden
5. Vuelve a escanear QR (mismo UUID) si cambió

**Recomendación:** Capacitar operadores a preguntar "¿Algo más?" antes de generar QR

---

### Situación 2: Error al escanear (código inválido)

**Escenario:** Operador escanea producto que no existe en sistema

**Respuesta del sistema:**
```
┌─────────────────────────────────────┐
│   ⚠️ PRODUCTO NO ENCONTRADO         │
├─────────────────────────────────────┤
│ Código de barra: 999999999          │
│                                     │
│ No existe en la base de datos       │
│                                     │
│ Opciones:                           │
│ [Reintenta escanear]                │
│ [Marca producto como NO PESABLE]    │
│ [Pregunta al gerente]               │
└─────────────────────────────────────┘
```

**¿Qué hacer?**
1. Verificar código de barra en producto (¿está borrado?)
2. Si es nuevo producto: **Gerente** debe agregarlo al sistema (Sprint 1)
3. Mientras tanto: Operador marca como "NO PESABLE" y gerente ajusta después

---

### Situación 3: Balanza se desconecta

**Escenario:** Balanza (hardware) pierde conexión

**Sistema resiliente:**
- ✅ Operador PUEDE continuar escaneando (sin peso automático)
- ✅ Operador ingresa peso **MANUALMENTE** por teclado
- ✅ Cuando balanza se reconecta: sincroniza automáticamente

```
[OPERADOR ve en pantalla]
┌─────────────────────────────────────┐
│   ⚠️ BALANZA DESCONECTADA           │
│   (Ingrese peso manualmente)        │
├─────────────────────────────────────┤
│ Producto: Tomate                    │
│ Precio: $2.50 USD / kg              │
│                                     │
│ Peso (kg): [_______] ← Cajero ingresa
│                                     │
│ [Confirmar peso]                    │
└─────────────────────────────────────┘
```

---

### Situación 4: Venta anulada (después de confirmar)

**Escenario:** Cajero confirma venta, pero cliente se arrepiente (15 min después)

**Reembolso:**
1. **NO** revertir la venta confirmada (auditoría intacta)
2. **Crear nueva transacción** de DEVOLUCIÓN
3. Sistema registra:
   - Transacción original: $13.98 (SALE)
   - Transacción devolución: -$13.98 (REFUND)
   - Neto: $0
   - Auditoría: ambas transacciones visibles

```
[GERENTE ve en auditoría]
15:47 - ORD-000142 - Cliente vendió - $13.98
16:02 - ORD-000142 - Cliente devolvió - -$13.98 (Razón: arrepentimiento)
       Inventario: Restaurado (tomate +2.3kg, pan +1, leche +1L)
```

---

### Situación 5: Stock bajo detectado (ALERTA)

**Escenario:** Sistema detecta que "Lechuga" está por debajo de stock mínimo

**¿Qué sucede?**
1. **Automáticamente:** Sistema genera alerta
2. **Gerente recibe notificación:**
   - 📧 Email: "ALERTA: Lechuga en stock bajo (2/10 unidades)"
   - 📱 WhatsApp (si configurado): "⚠️ Lechuga - compra hoy"
3. **Dashboard gerencial:** Muestra rojo "LECHUGA BAJO STOCK"

**¿Qué hace el gerente?**
1. Contacta proveedor
2. Cuando llega reabastecimiento: registra en sistema
   - Toca **[Ajustar Stock]** → Lechuga: +20 unidades (entrada manual)
   - Razón: "Reabastecimiento de proveedor X"
3. Sistema registra movimiento en auditoría

---

### Situación 6: Falla de conexión (SII o Internet)

**Escenario:** Local pierde internet (≠ balanza desconectada)

**Sistema resiliente:**
- ✅ **Operador y Cajero pueden continuar** (sin SII en background)
- ✅ Boleta se guarda en **"Cola de pendientes"** en local
- ✅ Cuando Internet regresa: sistema intenta nuevamente
- ⚠️ Boleta no se emite hasta que SII confirme

```
[CAJERO ve en pantalla]
┌──────────────────────────────────────┐
│   ✓ VENTA GUARDADA (Offline)         │
├──────────────────────────────────────┤
│ Status: Esperando conexión SII       │
│                                      │
│ La boleta se emitirá cuando la      │
│ conexión se restaure (~5 min)       │
│                                      │
│ ID temporal: TXN-20260405-000142    │
│                                      │
│ [Reintentar ahora] [OK]             │
└──────────────────────────────────────┘
```

---

## 📱 DASHBOARD GERENCIAL (Pantalla de Dueño/Gerente)

### Vista en Tiempo Real

```
┌────────────────────────────────────────────────────────────┐
│          DASHBOARD GERENCIAL - HOY 5 de Abril              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  RESUMEN DEL DÍA                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐       │
│  │ Ventas totales       │  │ Transacciones        │       │
│  │ $247.50 USD (↑8%)    │  │ 24 ventas            │       │
│  └──────────────────────┘  └──────────────────────┘       │
│                                                            │
│  ┌──────────────────────┐  ┌──────────────────────┐       │
│  │ Ticket promedio      │  │ Estaciones activas   │       │
│  │ $10.31 USD           │  │ 4/4 (100%)           │       │
│  └──────────────────────┘  └──────────────────────┘       │
│                                                            │
│  ALERTAS DE INVENTARIO                                   │
│  ⚠️ Lechuga: 2 unid (Mínimo: 10)      [COMPRAR HOY]     │
│  ⚠️ Leche: 3L (Mínimo: 5L)            [COMPRAR HOY]     │
│                                                            │
│  TOP 5 PRODUCTOS (Por cantidad vendida)                  │
│  1. Pan integral:    12 unidades    🥐                   │
│  2. Tomate:          8 kg           🍅                   │
│  3. Lechuga:         5 bundles      🥬                   │
│  4. Leche:           6L             🥛                   │
│  5. Aceite:          2 botellas     🍶                   │
│                                                            │
│  PRODUCTOS MÁS RENTABLES (Mayor ganancia)                │
│  1. Queso especial:      $45.50 USD                       │
│  2. Frutos secos:        $38.20 USD                       │
│  3. Aceite oliva prem:   $32.10 USD                       │
│                                                            │
│  [Ver más detalles] [Exportar PDF] [Cerrar día]          │
└────────────────────────────────────────────────────────────┘
```

### Reportes

Gerente puede generar:
- **Venta por hora:** Gráfico de transacciones a lo largo del día
- **Venta por categoría:** Qué categorías venden más
- **Inventario:** Qué productos están bajos
- **Rentabilidad:** Margen por producto/categoría
- **Auditoría:** Quién vendió qué, cuándo

---

## ⚙️ MANTENIMIENTO & PROCEDIMIENTOS

### Cierre de Caja (Al final del día)

**Gerente o Cajero Senior:**
1. Caja "cierra" automáticamente a hora definida (ej: 21:00)
2. Sistema muestra resumen:
   - Total de transacciones
   - Total de dinero esperado
   - Diferencia (si las hay)
3. Gerente verifica dinero físico vs sistema
4. Toca **[CERRAR DÍA]**
5. Sistema genera reporte del día
6. Datos listos para auditoría/impuestos

---

### Reinicio / Reset del Sistema

**ADMIN SOLO:**
1. ⚠️ Este botón existe pero **NO se debe usar** en operación normal
2. Usado solo en caso de corrupción de datos
3. Crea backup automático antes de hacer reset
4. Requiere confirmación en 2 pasos

---

## 🎓 CAPACITACIÓN RECOMENDADA

### Operador de Balanza (2 horas)
1. Encender/apagar estación
2. Escanear productos (10-15 intentos prácticos)
3. Revisar pantalla en tiempo real
4. Generar QR (finalizar orden)
5. Situaciones especiales (producto no existe, desconexión)
6. Preguntas frecuentes

### Cajero (2 horas)
1. Login en sistema
2. Escanear QR (10-15 intentos prácticos)
3. Ver detalles de compra
4. Métodos de pago
5. Confirmar venta (respetar ACID)
6. Devoluciones / cancelaciones
7. Boleta (impresión, email)
8. Situaciones especiales

### Gerente (3 horas)
1. Creación de usuarios (operadores, cajeros)
2. Creación/edición de productos
3. Dashboard y reportes
4. Alertas de stock
5. Cierre de caja
6. Auditoría y cumplimiento
7. Escalamientos/problemas

---

## 📞 SOPORTE & AYUDA

### Problemas Comunes & Soluciones Rápidas

| Problema | Solución |
|----------|----------|
| "Sistema lento" | Reiniciar aplicación (no pc) |
| "QR no escanea" | Limpiar lente del scanner |
| "Producto desaparece" | Verificar barcode (¿está registrado?) |
| "Stock negativo" | Contactar gerente (ajuste manual) |
| "Boleta no llega" | Revisar email/configuración |
| "No puedo loguearme" | Verificar PIN/password (máx 3 intentos = reset) |

### Escalamiento
1. **Problema técnico:** Contactar Allan (Backend)
2. **Problema operacional:** Contactar Giuliano (PM)
3. **Problema UI/Hardware:** Contactar Jonathan (Frontend)

---

**Versión:** 0.1  
**Última actualización:** 5 de abril 2026
