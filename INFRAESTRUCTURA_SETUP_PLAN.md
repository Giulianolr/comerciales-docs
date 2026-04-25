# PLAN DE SETUP INFRAESTRUCTURA VPS
## Resumen Ejecutivo + Timeline

**Versión:** 1.0  
**Fecha:** 19 de abril 2026  
**Estado:** ✅ Listo para implementación  
**Responsable:** Allan (Backend/DevOps), Jonathan (Frontend)  
**Supervisor:** Giuliano (PM)

---

## 📋 VISTA GENERAL

```
┌─────────────────────────────────────────────────────┐
│ INFRAESTRUCTURA MULTI-LOCAL (SaaS)                  │
├─────────────────────────────────────────────────────┤
│ 1 Dominio                                            │
│ ├─ comerciales.cl                                   │
│                                                      │
│ 1 VPS Hetzner CX31 ($3.60/mes)                     │
│ ├─ Ubuntu 22.04                                     │
│ ├─ PostgreSQL (BD compartida)                       │
│ ├─ Redis (sesiones/cache)                           │
│ ├─ FastAPI (4 workers)                              │
│ ├─ Nginx (reverse proxy)                            │
│ └─ Supervisor (process management)                  │
│                                                      │
│ 1 Frontend estático (Vue 3)                         │
│ ├─ Servido por Nginx                                │
│ ├─ Build estático (npm run build)                   │
│ └─ Cache via Cloudflare                             │
│                                                      │
│ N Locales (1, 2, 3, ... 10+)                       │
│ └─ Cada uno en tabla locals + users + data          │
│                                                      │
│ Costo Total: $33.60 USD/mes (Infra base)           │
│ Costo por Local: ~$31.60 USD/mes (con Bsale)       │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 OBJECTIVES & SUCCESS CRITERIA

### Objetivo Principal
Tener **1 dominio (comerciales.cl)** operativo sirviendo a **múltiples locales** con datos aislados, usando **VPS self-hosted económico** en Hetzner.

### Success Criteria
- ✅ Usuario puede login con credenciales (email + password)
- ✅ Cada usuario ve solo datos de su local
- ✅ Transacciones se registran correctamente
- ✅ Inventario se actualiza en tiempo real
- ✅ Puede integrarse con Bsale para facturación
- ✅ VPS está monitoreado y con backups automáticos
- ✅ Deploy de cambios de código funciona sin downtime

---

## 📅 TIMELINE IMPLEMENTACIÓN (4 SEMANAS)

### SEMANA 1: INFRAESTRUCTURA BASE (Allan - ~8 horas)

**Lunes 22 abril:**
- [ ] Crear cuenta Hetzner Cloud (15 min)
- [ ] Crear VPS CX31 + SSH key (15 min)
- [ ] Registrar dominio .cl (30 min, más propagación 24h)
- [ ] Configurar Cloudflare (30 min)
- **Entregable:** VPS corriendo, dominio apuntando

**Martes-Miércoles 23-24 abril:**
- [ ] SSH al servidor (5 min)
- [ ] Ejecutar VPS_SETUP.md Fase 1-3: update + dependencias + DB (2 horas)
- [ ] Instalar PostgreSQL + Redis + Nginx + Supervisor (1 hora)
- [ ] Verificar servicios corriendo (15 min)
- **Entregable:** Server básico con BD + Redis funcionando

**Jueves 25 abril:**
- [ ] Clone backend repo (5 min)
- [ ] Setup venv + dependencies (15 min)
- [ ] Ejecutar migraciones (5 min)
- [ ] Configurar Supervisor (20 min)
- [ ] Test: API respondiendo en 127.0.0.1:8000 (10 min)
- **Entregable:** Backend operativo

**Viernes 26 abril:**
- [ ] Clone frontend repo (5 min)
- [ ] npm build (10 min)
- [ ] Copiar a /var/www/comerciales (5 min)
- [ ] Configurar Nginx (15 min)
- [ ] Test: Frontend cargando en http://localhost (5 min)
- **Entregable:** Frontend + Backend + Nginx integrado

**Fin semana:** Descanso merecido 🎉

---

### SEMANA 2: MULTI-TENANT & SEGURIDAD (Allan + Jonathan - ~12 horas)

**Lunes 29 abril:**
- [ ] Revisar MULTI_TENANT_ARCHITECTURE.md (30 min)
- [ ] Crear esquema BD multi-tenant (migraciones Alembic)
  - [ ] Table `locals`
  - [ ] Table `users` (con local_id FK)
  - [ ] Update `products`, `transactions`, etc.
- [ ] Ejecutar migraciones en BD (15 min)
- **Entregable:** BD con estructura multi-tenant

**Martes-Miércoles 30 abril - 1 mayo:**
- [ ] Backend: Implementar JWT auth con local_id (2 horas)
- [ ] Backend: Implementar middleware `@get_current_user` (1 hora)
- [ ] Backend: Update todas las routes para filtrar por local_id (3 horas)
- [ ] Tests: Validar aislamiento de datos (1 hora)
- **Entregable:** Backend seguro multi-tenant

**Jueves 2 mayo:**
- [ ] Frontend: Implementar login screen (1 hora)
- [ ] Frontend: Guardar JWT en localStorage (30 min)
- [ ] Frontend: Agregar JWT a headers en todas las requests (1 hora)
- [ ] Frontend: Implementar logout (15 min)
- **Entregable:** Frontend auth completo

**Viernes 3 mayo:**
- [ ] Integration testing: Login → Dashboard → Ver datos (1 hora)
- [ ] Cross-browser testing (Chrome, Safari, Firefox) (30 min)
- [ ] Performance testing (load time < 2s) (30 min)
- **Entregable:** Sistema auth + multi-tenant funcionando end-to-end

---

### SEMANA 3: MONITOREO, BACKUPS & DEPLOYMENT (Allan - ~8 horas)

**Lunes 6 mayo:**
- [ ] Crear scripts backup (backup.sh) (30 min)
- [ ] Configurar cron job para backup automático (15 min)
- [ ] Configurar B2 para cloud backups (30 min)
- [ ] Test: Hacer restore de backup (30 min)
- **Entregable:** Backups automáticos configurados

**Martes 7 mayo:**
- [ ] Revisar DEPLOYMENT.md (30 min)
- [ ] Configurar GitHub Actions para auto-deploy (1 hora)
- [ ] Test: Push a main → auto-deploy (30 min)
- [ ] Configurar health-check automático (30 min)
- **Entregable:** CI/CD automático + health monitoring

**Miércoles 8 mayo:**
- [ ] Crear scripts de rollback (30 min)
- [ ] Test: Simular deploy fallido + rollback (1 hora)
- [ ] Documentar procedimientos operativos (1 hora)
- **Entregable:** Runbooks de operación

**Jueves-Viernes 9-10 mayo:**
- [ ] Load testing (simular 100+ transacciones) (1 hora)
- [ ] Security review (SQL injection, XSS, auth) (1 hora)
- [ ] Performance profiling (optimizar queries lentas) (1 hora)
- [ ] UAT: Validación con usuario real (1-2 horas)
- **Entregable:** Sistema pronto para producción

---

### SEMANA 4: PRODUCCIÓN & GO-LIVE (Todos - ~4 horas)

**Lunes 13 mayo:**
- [ ] Final checklist pre-production (45 min)
- [ ] Prueba completa del flujo:
  - [ ] Login (usuario local 1)
  - [ ] Ver productos
  - [ ] Crear transacción
  - [ ] Ver inventario actualizado
- [ ] Setup alerts de monitoreo (15 min)
- **Entregable:** Todo verificado, listo para GO LIVE

**Martes 14 mayo - GO LIVE 🚀**
- [ ] Anuncio a gerentes de locales (1 mensaje WhatsApp)
- [ ] Monitor activo primeros 2 horas
- [ ] Responder preguntas/issues en tiempo real
- [ ] Logs siendo guardados y monitoreados
- **Entregable:** Sistema en producción, usuarios usando

---

## 📦 DOCUMENTOS CREADOS (Lee en este orden)

### Para Allan (DevOps):
1. **HETZNER_SETUP.md** (45 min)
   - Crear cuenta Hetzner
   - Crear VPS CX31
   - Registrar dominio .cl
   - Configurar Cloudflare

2. **VPS_SETUP.md** (2-3 horas)
   - Setup inicial del servidor
   - Instalar PostgreSQL, Redis, Nginx, Supervisor
   - Clone backend, ejecutar migraciones
   - Deploy frontend
   - Configurar backups

3. **MULTI_TENANT_ARCHITECTURE.md** (leer con Jonathan)
   - Esquema de BD multi-tenant
   - Estrategia de aislamiento de datos
   - Ejemplos de queries seguras

4. **DEPLOYMENT.md** (leer antes de deploy)
   - Cómo actualizar código
   - GitHub Actions auto-deploy
   - Rollback rápido
   - Health checks

### Para Jonathan (Frontend):
1. **MULTI_TENANT_ARCHITECTURE.md**
   - Entender modelo SaaS
   - Aislamiento de datos por local
   - JWT tokens

2. **DEPLOYMENT.md**
   - Cómo hacer deploy del frontend
   - GitHub Actions workflow
   - Testing post-deploy

### Para Ambos:
1. **CAMBIOS_INFRAESTRUCTURA.md** (contexto)
   - Por qué VPS self-hosted vs GCP
   - Trade-offs aceptados
   - Escalado futuro

---

## 🛠️ TECH STACK

```
Backend:
├─ Language: Python 3.11
├─ Framework: FastAPI
├─ ORM: SQLAlchemy
├─ Migrations: Alembic
├─ Server: Gunicorn + Uvicorn workers
├─ DB: PostgreSQL 15
├─ Cache: Redis 7
└─ Auth: JWT (PyJWT)

Frontend:
├─ Framework: Vue 3
├─ Build: Vite
├─ Styling: [TBD - Tailwind? Bootstrap?]
├─ HTTP Client: Axios
└─ State: [localStorage para JWT]

Infrastructure:
├─ VPS: Hetzner Cloud CX31
├─ OS: Ubuntu 22.04 LTS
├─ Web Server: Nginx
├─ Process Manager: Supervisor
├─ DNS: Cloudflare
├─ Backups: B2 (Backblaze)
├─ CI/CD: GitHub Actions
└─ Monitoring: Simple (health endpoint)

Integrations:
├─ SII: Bsale API ($28/mes)
├─ Email: SendGrid (free tier)
└─ Domain: NIC Chile (.cl registry)
```

---

## 💰 COSTOS VERIFICADOS

### Mensual (Base)
```
VPS Hetzner CX31:        $3.60 USD
Dominio .cl:             $2.00 USD
Cloudflare:              $0.00 USD (free tier)
B2 Backups:              $0.00 USD (10GB gratis)
SendGrid Email:          $0.00 USD (free tier)
SII (Bsale):             $28.00 USD

TOTAL INFRAESTRUCTURA:   $33.60 USD/mes
```

### Por Local (cuando escalemos)
```
Costo Infra por local:   $3.36 USD (parte de CX31)
Costo Bsale por local:   $28.00 USD (fijo)
─────────────────────────────────────
Costo Base por Local:    $31.36 USD/mes

Si cobras $50/mes por local:
Margen por local:        $18.64 USD/mes

Con 10 locales:
Revenue:                 $500/mes
Costo:                   $316/mes
Margen:                  $184/mes
ROI:                     58% margin
```

---

## ⚠️ RIESGOS & MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|-----------|
| VPS caído | Baja (0.5%) | Alto (downtime total) | Alertas diarias, restore en 30 min |
| Pérdida de datos | Muy baja | Crítico | Backup automático diario a B2 |
| Performance degradación | Media (10%) | Medio | Upgrade a CX41 ($8/mes) |
| Error en deploy | Baja (5%) | Medio | Rollback automático, GitHub Actions |
| Acceso no autorizado | Muy baja | Crítico | JWT, SSL, firewall, no secrets en código |
| Escalado insuficiente | Baja | Medio | Monitor uso, path a managed DB |

---

## ✅ PRE-REQUISITOS ANTES DE EMPEZAR

- [ ] **Acceso:** Ambos (Allan + Jonathan) con acceso a GitHub repo
- [ ] **Crédito:** Tarjeta de crédito para Hetzner ($5 USD para verificar)
- [ ] **Dominio:** Decidir nombre (ej: comerciales.cl, locales.cl, etc)
- [ ] **API Keys:** Bsale API key obtenida
- [ ] **Email:** Cuenta SendGrid (free tier) creada
- [ ] **Acceso Cloud:** Crear cuenta B2 Backblaze (free tier)

---

## 📞 SOPORTE & ESCALATION

### Problemas comunes (ver TROUBLESHOOTING.md):
- SSH no conecta → Firewall issue
- BD no migra → Alembic issue
- API no responde → Supervisor/Gunicorn issue
- Frontend no carga → Nginx config issue
- Deploy falla → GitHub Actions / branch issue

### Escalation:
- **Técnico:** Allan revisa logs en /var/log/comerciales/
- **Arquitectura:** Revisar MULTI_TENANT_ARCHITECTURE.md
- **Operaciones:** Revisar DEPLOYMENT.md + BACKUP_STRATEGY.md

---

## 🎉 DEFINICIÓN DE "LISTO PARA PRODUCCIÓN"

✅ Cuando todos estos sean true:

- [ ] Usuario puede login (email + password)
- [ ] Dashboard muestra datos del local (no otros)
- [ ] Puede crear transacción + inventario actualiza
- [ ] API responde <200ms en queries normales
- [ ] Backups automáticos corriendo cada noche
- [ ] Health check pasa (HTTP 200)
- [ ] SSL/HTTPS funciona (Cloudflare)
- [ ] No hay secretos en código (.env en .gitignore)
- [ ] Logs están siendo registrados
- [ ] Rollback procedure documentado y testeado
- [ ] 2+ horas de monitoring sin errores

---

## 📋 CHECKLIST RÁPIDO (PRINT Y USA)

```
SEMANA 1 - INFRAESTRUCTURA:
[ ] Cuenta Hetzner creada
[ ] VPS CX31 corriendo (IP: _________)
[ ] Dominio registrado (Nombre: _________)
[ ] Cloudflare DNS configurado
[ ] SSH access funcionando
[ ] PostgreSQL + Redis + Nginx corriendo
[ ] Backend venv + dependencias instaladas
[ ] Migraciones ejecutadas
[ ] Frontend build & copia a /var/www completada
[ ] Nginx reverse proxy funcionando

SEMANA 2 - MULTI-TENANT:
[ ] Tablas con local_id creadas
[ ] JWT auth implementado
[ ] Middleware @get_current_user implementado
[ ] Filtros local_id en todas las routes
[ ] Tests de aislamiento pasando
[ ] Login screen funciona
[ ] JWT en localStorage
[ ] Integration tests completados

SEMANA 3 - OPERACIONES:
[ ] Backup script funcionando
[ ] B2 cloud backup configurado
[ ] GitHub Actions deploy funcionando
[ ] Health check endpoint funciona
[ ] Rollback procedure testeado
[ ] Logs siendo monitoreados

SEMANA 4 - GO LIVE:
[ ] Pre-production checklist pasado
[ ] Flujo completo testeado (login → transacción)
[ ] Gerentes notificados
[ ] Sistema monitoreado en vivo
[ ] Issues resueltos en tiempo real
[ ] ✅ SISTEMA EN PRODUCCIÓN
```

---

## 🚀 SIGUIENTES PASOS (AHORA)

### Giuliano (PM):
1. ✅ Revisar este documento
2. Aprobar timeline y presupuesto
3. Comunicar a Allan + Jonathan
4. Agendar kick-off meeting (lunes 22 abril)

### Allan (DevOps):
1. ✅ Leer HETZNER_SETUP.md (hoy)
2. Lunes: Empezar FASE 1 (Hetzner + dominio)
3. Martes-Viernes: Completar FASE 2-5 (VPS setup)

### Jonathan (Frontend):
1. ✅ Leer MULTI_TENANT_ARCHITECTURE.md (entiende modelo)
2. Preparar repositorio frontend (estructura limpia)
3. Semana 2: Implementar auth en frontend

---

## 📞 CONTACTOS & RESPONSABLES

| Rol | Persona | Responsabilidad | Teléfono |
|-----|---------|-----------------|----------|
| **PM** | Giuliano | Timeline, aprobaciones, stakeholder | +56 9 XXXX XXXX |
| **Backend/DevOps** | Allan | VPS, BD, API, deployments | +56 9 XXXX XXXX |
| **Frontend** | Jonathan | Vue, UI, integration | +56 9 XXXX XXXX |
| **Emergencias (fuera hrs)** | Allan | 24/7 soporte | +56 9 XXXX XXXX |

---

**Documento versión:** 1.0  
**Última actualización:** 19 de abril 2026  
**Próxima revisión:** 22 de abril (after kick-off)  
**Status:** ✅ Listo para implementación

---

## 📚 DOCUMENTOS DE REFERENCIA

- `docs/HETZNER_SETUP.md` — Crear VPS + dominio
- `docs/VPS_SETUP.md` — Setup servidor Ubuntu
- `docs/MULTI_TENANT_ARCHITECTURE.md` — Diseño BD
- `docs/DEPLOYMENT.md` — Deploy & CI/CD
- `docs/INFRAESTRUCTURA_ECONOMICA.md` — Análisis de costos
- `CAMBIOS_INFRAESTRUCTURA.md` — Por qué VPS (contexto)

---

**¡Listo para GO! 🚀**
