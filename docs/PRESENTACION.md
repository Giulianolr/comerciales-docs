# PRESENTACIÓN EJECUTIVA
## Sistema de Inventario Dinámico - Locales Comerciales Chile

**Documento para:** PM (Giuliano)  
**Preparado por:** Equipo Técnico (Allan, Jonathan)  
**Fecha:** 5 de abril de 2026  
**Versión:** 0.1-MVP  

---

## 📌 RESUMEN EJECUTIVO (1 minuto)

El proyecto moderniza el flujo de ventas en el local comercial (balanza → caja) **unificando procesos en tiempo real** con inventario automático y boletas electrónicas SII integradas.

| Métrica | Actual | Futuro | Mejora |
|---------|--------|--------|--------|
| Sincronización balanza ↔ caja | Manual/desconectada | Automática (WebSocket) | 100% tiempo real |
| Actualización inventario | Manual (post-venta) | Automática (al confirmar) | Instantánea |
| Errores por desincronización | Frecuentes | Cero (datos únicos) | Elimina retrasos |
| Tiempo preparación de boleta | ~2-3 min | <10 seg | -80% tiempo |
| Visibilidad de stock | Limitada | Real-time dashboard | Decisiones basadas en datos |

**ROI Estimado:** Ahorro 2-3 horas/día en trabajo manual + reducción de errores de inventario → ~$1,500-2,000/mes en productividad.

---

## 🎯 OBJETIVOS DEL PROYECTO

### Objetivo Principal
**Implementar un sistema de inventario dinámico integrado que sincronice balanza, caja y gestión de stock en tiempo real, mejorando eficiencia operacional y cumpliendo requisitos legales SII.**

### Objetivos Secundarios
1. **Reducir trabajo manual** → eliminar actualizaciones manuales de inventario post-venta
2. **Mejorar precisión** → cero desincronización entre balanza y caja
3. **Cumplimiento legal** → boletas electrónicas DTE automáticas via SII
4. **Visibilidad gerencial** → dashboard en tiempo real con alertas de stock
5. **Escalabilidad** → arquitectura lista para múltiples locales (2-20+)

---

## 🏢 CONTEXTO & PROBLEMA

### Situación Actual
El local opera con un flujo **desconectado y manual**:

```
1. Operador escanea barcode en BALANZA
2. Agrega item a una de 4 estaciones
3. Cliente completó compra → se genera PRE-BOLETA con QR
4. **PROBLEMA:** QR solo contiene TOTAL, no detalle de productos

5. Cajero escanea QR en CAJA
6. Caja recibe solo el TOTAL (sin detalle)
7. Cajero debe INGRESAR MANUALMENTE cada item nuevamente
8. **RESULTADO:** Inventario nunca se actualiza automáticamente
            → Mucho trabajo manual
            → Errores frecuentes
            → Sin visibilidad de stock real
```

### Impacto Negativo
- 📊 **Inventario inexacto:** Stock en sistema ≠ stock real (robo, errores de tipeo)
- 🕐 **Bajo productividad:** 2-3 horas/día en actualizaciones manuales
- 💸 **Pérdidas:** Stockout (sin saber que falta algo) o overstock
- 📱 **Sin datos gerenciales:** Imposible tomar decisiones basadas en ventas reales
- ⚖️ **Riesgo legal:** Boletas manuales, difícil auditoria SII

---

## ✨ SOLUCIÓN PROPUESTA

### Arquitectura Transformada

```
ANTES (Desconectado):
[Balanza] ←→ [QR solo total] ←→ [Caja]
   ↓                                 ↓
[Nada de inventario automático]    [Trabajo manual]

DESPUÉS (Integrado):
[Balanza] ←→ [API Backend] ←→ [Caja]
    ↓            ↓                   ↓
[WebSocket] [PostgreSQL]      [Detalle completo]
    ↓            ↓                   ↓
[Pantalla]   [Redis cache]    [Confirma = -X stock]
             [SII DTE]        [Auditoría completa]
             [Alertas/Analytics]
```

### Los 6 Cambios Clave

| # | Cambio | Implementación |
|---|--------|-----------------|
| 1 | **Sincronización real-time** | WebSocket entre balanza y caja (operador ve pantalla cliente actualizada) |
| 2 | **Pre-boleta completa** | QR contiene detalle COMPLETO (no solo total) |
| 3 | **Inventario automático** | Al confirmar venta → stock descuenta instantáneamente |
| 4 | **SII integrado** | Boleta electrónica se emite automáticamente vía proveedor SII |
| 5 | **Auditoría completa** | Cada transacción registra: usuario, timestamp, movimientos |
| 6 | **Analytics gerencial** | Dashboard Metabase con ventas, stock, tendencias en tiempo real |

---

## 📊 ALCANCE & FASES

### Alcance del MVP
✅ **Incluido:**
- 1-2 locales piloto como fase inicial
- 4 estaciones de la balanza operativas
- Sincronización balanza ↔ caja en tiempo real
- Inventario dinámico automático
- Integración SII (boletas electrónicas)
- Dashboard gerencial Metabase
- Auditoría completa

❌ **No incluido (Fases 2+):**
- Integraciones con sistemas ERP externos (Odoo, SAP)
- Múltiples sucursales (requiere data warehouse)
- Análisis predictivo con IA (evaluación en piloto)
- Mobile app (operadores)
- Reporte impositivo avanzado

### Cronograma de Implementación

| Sprint | Semana | Entregables | Hito |
|--------|--------|-------------|------|
| **0** | 1 | Setup GCP + repos GitHub + specs HW | Infraestructura operativa |
| **1** | 2-3 | Módulo Inventario (CRUD productos + stock) | Productos en sistema |
| **2** | 4-5 | Módulo Balanza (4 estaciones + QR completo) | Balanza → Backend en tiempo real |
| **3** | 6-7 | Módulo Caja (lectura QR + descuento stock automático) | Venta completa = inventario -X |
| **4** | 8-9 | Integración SII + Auditoría completa | Boleta electrónica operativa |
| **5** | 10-11 | Dashboards + Alertas | Analytics gerencial en vivo |
| **6** | 12 | QA + Deploy producción + Capacitación | Sistema en producción |

**Timeline total:** 12 semanas (8-12 semanas objetivo) | **% Completado:** 0% (hoy = día 1)

---

## 💰 PRESUPUESTO & COSTOS (REVISADO - ECONÓMICO)

### Inversión Inicial (Desarrollo)
| Concepto | Estimado |
|----------|----------|
| 2 Devs x 10-12 semanas (Allan + Jonathan) | $7,000-11,000 |
| Design/UX (pantallas operador + gerencial) | $1,000-2,000 |
| Documentación + Capacitación | $500-1,000 |
| **TOTAL DESARROLLO** | **$8,500-14,000** |

### Costos Operacionales Mensuales (PILOTO 1-2 LOCALES)
| Concepto | Costo USD | Costo CLP | Notas |
|----------|-----------|-----------|-------|
| VPS Hetzner CX31 (2vCPU, 4GB, 40GB) | $3.60 | 3,240 | Self-hosted, PostgreSQL + Redis |
| Dominio (.cl) | $2.00 | 1,800 | NIC Chile |
| Cloudflare (DNS + SSL) | $0.00 | - | Free tier ✅ |
| B2 Backups | $0.00 | - | 10GB/mes free ✅ |
| Email/Notifications | $0.00 | - | SendGrid/manual free ✅ |
| SII Proveedor (Bsale) | $28.00 | 25,200 | Inevitable (DTE) |
| **TOTAL MENSUAL** | **$33.60 USD** | **~30,240 CLP/mes** | ✅ BAJO |

### ROI Estimado (Anualizado)
- **Productividad:** 2-3 horas/día x 20 días x 12 meses = ~50-75 hrs/año
  - A $25 USD/hora (salario operario promedio) = **$1,250-1,875 USD/año**
- **Reducción de errores de inventario:** ~5% pérdida actual → 0.5%
  - Supongamos ingresos mensuales $10,000 USD: **$500-900 USD/año ahorrado**
- **Faster checkout:** Mejora experiencia cliente → ~2-3% más clientes
  - **$1,200-3,600 USD/año incremento ingresos**
- **TOTAL ROI ANUAL:** **$2,950-6,375 USD (~2.6-5.6M CLP/año)**
- **Cost of infrastructure/year:** $33.60 × 12 = **$403 USD (~363k CLP)**

**Payback period:** ~2-3 meses (ROI sigue siendo EXCELENTE)  
**Anual net:** $2,547-5,972 USD después de costos infra

### Escalado a 10 Locales
| Concepto | Costo/mes |
|----------|-----------|
| VPS upgrade (CX41) | $8.00 USD |
| Dominio × 10 | $20 USD |
| SII × 10 (Bsale) | $280 USD |
| **TOTAL PARA 10 LOCALES** | **$308 USD/mes** (~277k CLP) |
| **POR LOCAL** | **$30.80 USD/mes** |

---

## 👥 EQUIPO & ROLES

### Estructura de Trabajo
| Rol | Nombre | Stack | Responsabilidades |
|-----|--------|-------|------------------|
| **PM / Product Owner** | Giuliano | N/A | Visión, requerimientos, stakeholders, aprobaciones críticas |
| **Backend Engineer** | Allan | Python/FastAPI, GCP, DevOps | APIs, base de datos, infraestructura cloud, integraciones SII |
| **Frontend Engineer** | Jonathan | Vue 3, TypeScript, UI/UX | Interfaces operador/gerencial, WebSocket, hardware integration |

### Comunicación
- **Daily standup:** 9:30 AM (15 min)
- **Sprint planning:** Lunes (inicio de sprint)
- **Sprint review:** Viernes (fin de sprint)
- **Escalamientos:** Directo a Giuliano (PM)

---

## 🔐 SEGURIDAD & CUMPLIMIENTO

### Estándares Implementados
- **Autenticación:** JWT tokens con refresh cycles
- **Autorización:** Role-based access (ADMIN, GERENTE, CAJERO, OPERADOR)
- **Auditoría:** Registro inmutable de cada transacción (quién, qué, cuándo, dónde)
- **SII (DTE):** Boletas electrónicas firmadas digitalmente
- **Datos:** Encriptación en tránsito (HTTPS) y en reposo (Cloud SQL encryption)
- **Secretos:** GCP Secret Manager (nunca en código)

### Cumplimiento Legal Chile
- ✅ SII: Boletas electrónicas DTE integradas
- ✅ Auditoría: Trazabilidad de movimientos de inventario
- ✅ Certificado digital: Almacenado de manera segura

---

## ⚠️ RIESGOS & MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-----------|--------|------------|
| Hardware desconocido (balanza, scanner) | Alta | Crítico | Reunión martes → obtener specs exactas + pruebas prototipo |
| Proveedor SII indisponible | Baja | Alto | Testing en sandbox, fallback a boleta manual temporal |
| Conectividad del local | Media | Medio | Modo offline básico para caja (sincroniza después) |
| Capacitación operadores | Media | Medio | Plan de capacitación + documentación visual (semana 12) |
| Scope creep | Alta | Medio | Reuniones de control semanal (PM), freeze de features |

---

## ✅ PRÓXIMOS PASOS (Ruta Crítica)

### Esta Semana
1. ✅ **COMPLETADO:** Aprobación de arquitectura
2. **HITO CRÍTICO MARTES:** Reunión en local
   - Obtener marca/modelo exacta: escáner, balanza, caja
   - Protocolo de comunicación (USB, Ethernet, API?)
   - Estado actual del sistema POS
3. **Miércoles:** Revisión de hardware, decisiones finales SII
4. **Sprint 0 comienza:** Setup infraestructura GCP + repos

### Próximas 2 Semanas
- Sprint 0 completado (infra operativa)
- Sprint 1 comienza (módulo inventario)
- Primer CRUD de productos funcional

### Próximas 4 Semanas
- Sprint 1-2 completados
- Balanza → API Backend en tiempo real
- Pre-boletas con QR completo generándose

---

## 📞 CONTACTO

| Rol | Nombre | Email | Teléfono | Horario |
|-----|--------|-------|----------|---------|
| PM | Giuliano | - | - | - |
| Backend | Allan | - | - | - |
| Frontend | Jonathan | - | - | - |

**Escalamientos:** Directo a Giuliano (PM)

---

## 📎 DOCUMENTACIÓN ADJUNTA

1. **README.md** — Overview completo del proyecto + estructura
2. **ARQUITECTURA.md** — Diagramas C4, stack tecnológico, decisiones
3. **MODELO_DATOS.md** — Esquema de base de datos + relaciones
4. **API_REFERENCE.md** — Endpoints (auto-generado en Sprint 0)
5. **FLUJO_OPERACIONAL.md** — Guía paso a paso para operarios
6. **Plan detallado** — `/plans/swirling-knitting-hickey.md`

---

## 📋 CHECKLIST PM

- [ ] Aprobación de presupuesto ($125-185 USD/mes infraestructura)
- [ ] Confirmación timeline (12 semanas)
- [ ] Designación de stakeholder principal (cliente/gerente local)
- [ ] Acceso a local para reunión martes
- [ ] Aprobación de proveedor SII (Bsale/Acepta)
- [ ] Comunicación a operadores sobre cambios próximos
- [ ] Plan de capacitación para operadores (Sprint 6)

---

**Documento preparado por:** Equipo Técnico  
**Versión:** 0.1  
**Última actualización:** 5 de abril de 2026  
**Próxima revisión:** Después de reunión martes (hardware)
