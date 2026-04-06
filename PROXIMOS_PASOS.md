# PRÓXIMOS PASOS CRÍTICOS
## Sistema de Inventario Dinámico - Locales Comerciales Chile

**Fecha:** 5 de abril de 2026  
**Responsable:** Giuliano (PM) + Equipo Técnico  
**Estado:** 🟢 Arquitectura aprobada, documentación completada → Listo para Sprint 0

---

## ⏰ CRONOGRAMA INMEDIATO

### HOY - Viernes 5 de Abril
- ✅ **COMPLETADO:** Aprobación de arquitectura
- ✅ **COMPLETADO:** Documentación completa (README, PRESENTACION, ARQUITECTURA, MODELO_DATOS, FLUJO_OPERACIONAL)
- **ACCIÓN PM:** 
  - [ ] Revisar documentación completa
  - [ ] Crear lista de preguntas para reunión martes
  - [ ] Coordinar acceso a local para martes

### MARTES 9 de Abril - 🔴 REUNIÓN CRÍTICA EN LOCAL

**OBJETIVO:** Obtener especificaciones exactas de hardware + ambiente actual

**Asistentes recomendados:**
- Giuliano (PM) — Lidera reunión
- Jonathan (Dev Frontend) — Toma notas técnicas de hardware
- Dueño/Gerente del local — Contexto operacional

**A Obtener:**

1. **ESCÁNER DE CÓDIGO DE BARRAS**
   - [ ] Marca y modelo exacto
   - [ ] ¿USB? ¿Ethernet? ¿Otro protocolo?
   - [ ] Driver disponible para Linux/Windows?
   - [ ] Velocidad (escanea 1 barcode/segundo?)
   - [ ] ¿Hay API o SDK disponible?

2. **BALANZA CON 4 ESTACIONES**
   - [ ] Marca y modelo exacto
   - [ ] ¿Conectada a una computadora central o 4 independientes?
   - [ ] Protocolo de comunicación (USB, Ethernet, Serial)?
   - [ ] ¿Tiene pantalla propia en cada estación?
   - [ ] ¿Puede pesar automáticamente o requiere operador?
   - [ ] ¿Existe API/SDK para obtener datos de peso en tiempo real?
   - [ ] ¿Qué software actualmente usa? (¿Podemos ver documentación?)

3. **SISTEMA DE CAJA ACTUAL**
   - [ ] ¿Existe POS? ¿Marca/modelo? ¿Obsoleto o actual?
   - [ ] ¿Usa Windows, Linux, Android?
   - [ ] ¿Es software propietario o comercial?
   - [ ] ¿Puede reemplazarse completamente o requiere integración?
   - [ ] ¿Qué datos exporta? ¿JSON, CSV, texto?

4. **INFRAESTRUCTURA ACTUAL**
   - [ ] ¿Internet disponible? ¿Fibra o móvil? ¿Velocidad?
   - [ ] ¿WiFi en local? ¿Cubierta de las 4 estaciones?
   - [ ] ¿Computadora central? ¿Marca, OS, edad?
   - [ ] ¿Impresoras? ¿Térmicas o inyección? ¿Para boletas?
   - [ ] ¿Pantallas disponibles para mostrar pre-boleta?

5. **REQUISITOS SII & LEGAL**
   - [ ] ¿Tiene proveedor de boletas SII ya? ¿Cuál? (Bsale, Acepta, etc)
   - [ ] ¿Certificado digital activo? (necesario para DTE)
   - [ ] ¿RUT del local?
   - [ ] ¿Acceso a portal SII para pruebas?

6. **OPERACIONAL ACTUAL**
   - [ ] ¿Cuántos operadores en balanza? ¿Turnos?
   - [ ] ¿Cuántos cajeros?
   - [ ] ¿Volumen de transacciones por día? (preguntar de nuevo)
   - [ ] ¿Horario de apertura?
   - [ ] ¿Hay cierre de caja diario?

**Entregables de PM post-reunión:**
- [ ] Documento "Especificaciones de Hardware" (crear en `/docs/hardware/`)
- [ ] Diagrama actualizado de arquitectura física (ubicación de componentes)
- [ ] Matriz de decisiones técnicas (qué está confirmado vs qué requiere cambios)

---

### MIÉRCOLES 10 de Abril - Revisión de Hardware + Decisiones Finales

**Qué hacer:**
1. **Allan + Jonathan analizan** especificaciones de hardware
2. **Crean PoC (Proof of Concept)** si hay duda en integración
   - Ej: "¿Podemos realmente leer peso en tiempo real desde balanza X?"
3. **PM confirma con cliente:**
   - Proveedor SII definitivo + credenciales para sandbox
   - Acceso a infraestructura (computadoras, internet)
   - Fecha de inicio real (¿el próximo lunes?)

---

### JUEVES 11 de Abril - Preparación Sprint 0

**Allan:**
- [ ] Crear repositorio `comerciales-backend` en GitHub
- [ ] Setup Dockerfile + docker-compose.yml (FastAPI template)
- [ ] Crear rama `develop` como rama de integración
- [ ] Crear archivo `README.md` en backend (guía dev)
- [ ] Configurar GitHub Actions workflow (test + build)
- [ ] Crear folder `migrations/` con Alembic init

**Jonathan:**
- [ ] Crear repositorio `comerciales-frontend` en GitHub
- [ ] Setup Vite + Vue 3 template
- [ ] Crear rama `develop` como rama de integración
- [ ] Instalar dependencias base (axios, pinia, tailwind, shadcn-vue)
- [ ] Crear archivo `README.md` en frontend (guía dev)
- [ ] Setup mock de API (para que pueda trabajar sin backend)

**PM (Giuliano):**
- [ ] Crear repositorio `comerciales-docs` en GitHub
- [ ] Mover documentación (`docs/` folder) a este repo
- [ ] Crear repositorio `comerciales-infra` en GitHub (Terraform templates)
- [ ] Invitar a Allan y Jonathan como colaboradores en todos los repos
- [ ] Configurar proyecto GitHub (project board, milestones)

---

### LUNES 14 de Abril - 🚀 SPRINT 0 OFICIALMENTE INICIA

**Objetivo:** Infraestructura completamente funcional + scaffolding backend+frontend

**Tareas Allan (Backend):**
- [ ] Crear GCP project
- [ ] Setup Cloud SQL PostgreSQL (13, ya que algunas features de 15 son nuevas)
- [ ] Crear Cloud Run service (dummy, solo para deployments)
- [ ] Setup Memorystore Redis
- [ ] Secret Manager: guardar credenciales SII
- [ ] FastAPI project scaffolding:
  - Models (SQLAlchemy) para Users, Products, Orders básico
  - Migrations (Alembic) setup
  - Auth (JWT) básico
  - Hello World endpoint
- [ ] Deploy primer versión a Cloud Run (sin datos útiles aún)

**Tareas Jonathan (Frontend):**
- [ ] Vue 3 setup completo
- [ ] 3 pantallas stub (operador, cajero, gerente)
- [ ] Conexión a backend (mock o real)
- [ ] Responsive design basic
- [ ] Tailwind + shadcn-vue setup

**Tareas PM:**
- [ ] Crear issues en GitHub para cada task
- [ ] Setup project board (Kanban: To Do, In Progress, Done)
- [ ] Primera reunión con cliente para validar ambiente

---

## 📋 CHECKLIST ANTES DE MARTES 9 (REUNIÓN HARDWARE)

### PM (Giuliano)
- [ ] Revisar toda la documentación (README, PRESENTACION, ARQUITECTURA)
- [ ] Preparar documento de "Preguntas para Hardware" (usar sección anterior como base)
- [ ] Confirmar acceso a local
- [ ] Coordinar horario y asistentes
- [ ] Imprimir o llevar plan en tablet

### Allan
- [ ] Revisar ARQUITECTURA.md (entender decisiones técnicas)
- [ ] Revisar MODELO_DATOS.md (entender schema DB)
- [ ] Preparar preguntas técnicas sobre balanza/integración
- [ ] Revisar presupuesto GCP (¿está dentro de presupuesto?)

### Jonathan
- [ ] Revisar FLUJO_OPERACIONAL.md (entender UX)
- [ ] Revisar ARQUITECTURA.md (UI mockups mentales)
- [ ] Preparar preguntas sobre pantallas disponibles en local
- [ ] Revisar especificaciones de hardware (layout físico)

---

## 🎯 INDICADORES DE ÉXITO (Semana 1)

Al finalizar la reunión de martes + preparativos, debe estar claro:

- ✅ Hardware especificado 100% (sin incertidumbres)
- ✅ Proveedor SII confirmado con sandbox activo
- ✅ Arquitectura física confirmada (dónde irá cada componente)
- ✅ Timeline de desarrollo confirmada (empezamos lunes 14?)
- ✅ Budget confirmado (¿dentro de $15k-$40k?)
- ✅ Equipo claro en roles y responsabilidades

Si falta algo: **DETENER y resolver antes de empezar Sprint 0**

---

## 📚 DOCUMENTOS GENERADOS (LEER ANTES DE SPRINT 0)

### Para PM (Giuliano) — Leer en este orden:
1. **README.md** (10 min) — Overview
2. **PRESENTACION.md** (15 min) — Ejecutivo para presentar a cliente
3. **PROXIMOS_PASOS.md** (este) (10 min) — Plan inmediato

### Para Devs (Allan + Jonathan):
1. **README.md** (10 min) — Context general
2. **ARQUITECTURA.md** (30 min) — Decisiones técnicas + diagramas
3. **MODELO_DATOS.md** (20 min) — Schema BD (Allan enfoque)
4. **FLUJO_OPERACIONAL.md** (20 min) — UX (Jonathan enfoque)
5. **Plan** (`/plans/swirling-knitting-hickey.md`) (15 min) — Timeline detallado

---

## 🔧 SETUP DEL WORKSPACE (Recomendado)

### Estructura local (Giuliano):
```
/Documentación
├── README.md                    ← Lee primero
├── PRESENTACION.md              ← Ejecutivo
├── docs/
│   ├── ARQUITECTURA.md          ← Devs
│   ├── MODELO_DATOS.md          ← Allan
│   ├── FLUJO_OPERACIONAL.md    ← Jonathan
│   ├── hardware/               (se llena post-martes)
│   └── runbooks/               (se llena en Sprints)
├── PROXIMOS_PASOS.md            ← Éste
└── [Carpeta para PPT cuando se cree]

/Repositorios GitHub (crear martes post-reunión)
├── comerciales-backend/
├── comerciales-frontend/
├── comerciales-infra/
└── comerciales-docs/
```

---

## ⚡ RIESGOS & MITIGACIONES

| Riesgo | Si ocurre... | Acción rápida |
|--------|-------------|---------------|
| Hardware incompatible con nuestra architecture | Requiere redesign | Tener Plan B (ej: middleware hardware custom) |
| SII proveedor sandbox no disponible | Sprint 4 en riesgo | Encontrar alternativa antes de Sprint 4 |
| Local sin Internet estable | Crítico para balance | Implementar offline mode ASAP (Sprint 2-3) |
| Retraso en martes/miércoles | Perdemos días | Iniciar Sprint 0 con asunciones, ajustar después |

---

## 📞 CONTACTOS CLAVE

| Rol | Nombre | Para qué |
|-----|--------|----------|
| PM | Giuliano | Decisiones, stakeholders, cronograma |
| Backend | Allan | Infraestructura GCP, APIs, DB |
| Frontend | Jonathan | UI/UX, hardware integration, mockups |
| Cliente (Dueño local) | [Nombre] | Requisitos operacionales, acceso |
| Soporte Técnico | [Si hay] | Hardware issues |

---

## ✅ SEÑALES DE QUE ESTAMOS LISTOS PARA SPRINT 0

- ✅ Documentación completa y revisada
- ✅ Hardware especificado 100%
- ✅ Equipo entiende arquitectura
- ✅ Repositorios GitHub creados
- ✅ GCP proyecto creado + budget confirmado
- ✅ Proveedor SII con sandbox
- ✅ Cliente alineado en timeline y expectativas

---

**Versión:** 0.1  
**Próxima revisión:** Martes 9 de abril (post-reunión)  
**Responsable de actualizar:** Giuliano (PM)
