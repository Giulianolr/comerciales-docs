# ÍNDICE DE DOCUMENTACIÓN - INFRAESTRUCTURA VPS
## Tu guía para entender la arquitectura y empezar implementación

**Generado:** 19 de abril 2026  
**Modelo:** SaaS Multi-Tenant (1 dominio, múltiples locales)  
**Stack:** Python + Vue + PostgreSQL + Redis + Nginx + Hetzner VPS

---

## 📚 DOCUMENTOS POR ROL

### 👨‍💼 **PARA GIULIANO (PM)**
Leer en este orden para entender el plan:

1. **ESTE ÍNDICE** (ahora, 5 min)
2. **INFRAESTRUCTURA_SETUP_PLAN.md** (15 min)
   - Timeline completo: 4 semanas
   - Costos + ROI
   - Riesgos + mitigaciones
   - Checklist ejecutivo

3. **CAMBIOS_INFRAESTRUCTURA.md** (opcional, contexto)
   - Por qué VPS vs GCP
   - Comparativa de costos

**Resumen:** 20 minutos para entender todo.

---

### 🔧 **PARA ALLAN (Backend/DevOps)**
Ejecuta estos pasos, documentos en orden de lectura:

#### SEMANA 1: Setup Infraestructura
1. **HETZNER_SETUP.md** (45 min - lunes 22)
   - [ ] Crear cuenta Hetzner
   - [ ] VPS CX31 creado
   - [ ] Dominio .cl registrado
   - [ ] Cloudflare DNS configurado
   - [ ] SSH access verificado

2. **VPS_SETUP.md** (2-3 horas - martes a viernes)
   - [ ] FASE 1: System setup (apt update, firewall, usuarios)
   - [ ] FASE 2: Instalar PostgreSQL, Redis, Nginx, Supervisor
   - [ ] FASE 3: Configurar BD multi-tenant
   - [ ] FASE 4: Clone backend + venv + dependencias
   - [ ] FASE 5: Supervisor + process management
   - [ ] FASE 6: Nginx reverse proxy
   - [ ] FASE 7: Frontend build & deploy
   - [ ] FASE 8: SSL con Cloudflare
   - [ ] FASE 9: Backups automáticos

#### SEMANA 2: Multi-Tenant (con Jonathan)
3. **MULTI_TENANT_ARCHITECTURE.md** (junto con Jonathan)
   - Entender schema BD (locals, users, products con local_id)
   - Implementar migraciones Alembic
   - Implementar JWT middleware
   - Filtros local_id en todas las routes
   - Tests de aislamiento

#### SEMANA 3-4: Operaciones & Go-Live
4. **DEPLOYMENT.md** (antes de cualquier deploy)
   - Opción A: Deploy manual (SSH + git pull)
   - Opción B: GitHub Actions auto-deploy
   - Procedure de rollback
   - Health checks + monitoring
   - Post-deploy verification

**Clave de éxito:** Seguir paso a paso, no saltarse fases. Cada fase = checkpoint.

---

### 🎨 **PARA JONATHAN (Frontend)**
Implementa auth y vistas multi-tenant:

#### SEMANA 2: Auth + Multi-Tenant UI
1. **MULTI_TENANT_ARCHITECTURE.md** (junto con Allan)
   - Entender JWT token (tiene local_id)
   - Entender aislamiento de datos
   - Validar requests al backend

2. **Implementación Frontend:**
   - [ ] Login screen (email + password → backend JWT)
   - [ ] Guardar JWT en localStorage
   - [ ] Axios interceptor: agregar Authorization header
   - [ ] Dashboard: mostrar local actual + user info
   - [ ] Logout: limpiar localStorage

#### SEMANA 3: Deployment
3. **DEPLOYMENT.md** (sección Frontend)
   - Opción A: Deploy manual (git pull + npm build)
   - Opción B: GitHub Actions auto-deploy
   - Testing post-deploy

**Clave de éxito:** No hardcodear URLs, usar variables de entorno.

---

## 🗺️ MAPA DE DOCUMENTOS

```
INFRAESTRUCTURA_SETUP_PLAN.md
├─ Timeline 4 semanas
├─ Costos + ROI
├─ Checklist ejecutivo
└─ Lee esto primero (Giuliano)

    ↓ (Semana 1)

HETZNER_SETUP.md
├─ Crear cuenta Hetzner
├─ VPS CX31
├─ Dominio .cl
├─ Cloudflare DNS
└─ Allan: Sigue paso a paso

    ↓ (Semana 1)

VPS_SETUP.md
├─ FASE 1-2: System + dependencias
├─ FASE 3-4: BD + Backend
├─ FASE 5-6: Supervisor + Nginx
├─ FASE 7-8: Frontend + SSL
├─ FASE 9: Backups
└─ Allan: 2-3 horas

    ↓ (Semana 2)

MULTI_TENANT_ARCHITECTURE.md
├─ Schema BD (locals, users, local_id FK)
├─ JWT token strategy
├─ Middleware de aislamiento
├─ Filtros por local_id
├─ Security patterns
└─ Allan + Jonathan: Implementar juntos

    ↓ (Semana 2-3)

DEPLOYMENT.md
├─ Deploy manual o GitHub Actions
├─ Rollback procedure
├─ Health checks
├─ Monitoring
└─ Antes de cualquier cambio a producción

    ↓ (Semana 4)

CAMBIOS_INFRAESTRUCTURA.md
└─ Contexto: por qué VPS vs GCP (referencia)
```

---

## ✅ CHECKLIST RÁPIDO (PRINT & FRAME)

```
SEMANA 1 (Allan):
☐ Hetzner account creada (HETZNER_SETUP.md)
☐ VPS CX31 corriendo (IP: ...)
☐ Dominio .cl registrado
☐ Cloudflare DNS OK
☐ VPS_SETUP.md FASE 1-3 completada (system + DB)
☐ VPS_SETUP.md FASE 4-5 completada (backend)
☐ VPS_SETUP.md FASE 6-7 completada (nginx + frontend)
☐ Health check: curl http://localhost/health → OK

SEMANA 2 (Allan + Jonathan):
☐ MULTI_TENANT_ARCHITECTURE.md leído por ambos
☐ Migraciones Alembic creadas (locals, users, products)
☐ JWT auth implementado (backend)
☐ Middleware @get_current_user implementado
☐ Todas las routes filtrando por local_id
☐ Login screen implementado (frontend)
☐ JWT en localStorage (frontend)
☐ Integration tests pasando

SEMANA 3 (Allan):
☐ DEPLOYMENT.md leído
☐ Backups automáticos funcionando
☐ GitHub Actions setup (auto-deploy)
☐ Health check automático corriendo
☐ Rollback procedure testeado

SEMANA 4 (Todos):
☐ Full integration test: login → transacción → inventario
☐ Load testing (100+ transacciones)
☐ Security review
☐ Pre-production checklist pasado
☐ ✅ GO LIVE
```

---

## 🚀 CÓMO EMPEZAR AHORA

### Opción A: Estoy listo ahora (hoy)
1. Giuliano: Lee INFRAESTRUCTURA_SETUP_PLAN.md (15 min)
2. Aprueba timeline + presupuesto
3. Comunica a Allan + Jonathan
4. Agendar kick-off call (mañana?)

### Opción B: Necesito más contexto
1. Giuliano: Lee CAMBIOS_INFRAESTRUCTURA.md (por qué VPS)
2. Luego: INFRAESTRUCTURA_SETUP_PLAN.md
3. Luego: Aprueba + comunica

### Opción C: Allan necesita empezar mañana
1. Allan: Lee HETZNER_SETUP.md ahora (45 min)
2. Mañana lunes: Empieza pasos HETZNER_SETUP
3. Martes-viernes: VPS_SETUP.md

---

## 🎯 OBJETIVOS SEMANALES

### Semana 1: "Infraestructura Física"
```
Entrada: Nada
Procesos: Hetzner + VPS setup
Salida: VPS corriendo con PostgreSQL + Redis + backend + frontend
```

### Semana 2: "Multi-Tenant Seguro"
```
Entrada: VPS con app funcionando
Procesos: BD multi-tenant + JWT auth + filtros local_id
Salida: Usuarios logueados, ven solo su local
```

### Semana 3: "Operaciones Maduras"
```
Entrada: App multi-tenant funcionando
Procesos: Backups + monitoring + auto-deploy + rollback
Salida: Sistema es resiliente, mantenible, recoverable
```

### Semana 4: "Go-Live"
```
Entrada: Sistema maduro, testeado, monitoreado
Procesos: Final verification + user communication
Salida: ✅ Sistema en producción, usuarios usando
```

---

## 📊 MÉTRICAS DE ÉXITO

Después de 4 semanas:

- ✅ API responde <200ms en queries normales
- ✅ Usuario puede login en <2 segundos
- ✅ Dashboard carga en <3 segundos
- ✅ Transacción se registra en <500ms
- ✅ Inventario actualiza en <1 segundo
- ✅ 0 secretos en código
- ✅ Backups automáticos corriendo
- ✅ Health check pasa cada minuto
- ✅ Downtime esperado: 0 (24/7 uptime)

---

## 🆘 AYUDA RÁPIDA

### "¿Dónde está X?"
- Setup VPS → HETZNER_SETUP.md
- Instalar servicios → VPS_SETUP.md
- Diseño BD → MULTI_TENANT_ARCHITECTURE.md
- Deploy código → DEPLOYMENT.md
- Timeline → INFRAESTRUCTURA_SETUP_PLAN.md

### "¿Cómo hago X?"
- Crear dominio → HETZNER_SETUP.md paso 3
- Instalar PostgreSQL → VPS_SETUP.md FASE 2.2
- Filtrar por local_id → MULTI_TENANT_ARCHITECTURE.md "Filtración de Queries"
- Deploy automático → DEPLOYMENT.md "Opción B"

### "Algo falló"
1. Lee DEPLOYMENT.md "ROLLBACK RÁPIDO"
2. Ejecuta rollback automático
3. Investigar logs: `/var/log/comerciales/`
4. Comunicar a Giuliano

---

## 📞 PREGUNTAS FRECUENTES

**P: ¿Puedo empezar solo la semana 1?**  
R: Sí. Semana 1 es independiente. Luego pausa si es necesario.

**P: ¿Qué pasa si Hetzner no está disponible?**  
R: VPS_SETUP.md da alternativas (DigitalOcean, Linode, Vultr).

**P: ¿Puedo volver a GCP después?**  
R: Sí. VPS ahora, GCP después si necesitas escalado automático.

**P: ¿Cuántas horas de trabajo total?**  
R: ~32 horas distribuidas en 4 semanas (8h semana 1, 12h semana 2, 8h semana 3, 4h semana 4).

**P: ¿Cuál es el downtime esperado?**  
R: ~1 minuto por deploy. VPS caído: 0.5% probabilidad/año (muy raro).

**P: ¿Qué pasa si tengo 50 locales?**  
R: Upgrade VPS a CX41 ($8/mes) o separar BD a managed. MULTI_TENANT_ARCHITECTURE.md tiene el path.

---

## 🎓 LEARNING PATH

Si eres nuevo en infraestructura, lee en este orden:

1. **CAMBIOS_INFRAESTRUCTURA.md** (5 min) — entiende "por qué VPS"
2. **INFRAESTRUCTURA_SETUP_PLAN.md** (15 min) — entiende timeline
3. **HETZNER_SETUP.md** (30 min) — entiende creación de servidor
4. **VPS_SETUP.md** (2-3h lectura lenta) — entiende cada servicio
5. **MULTI_TENANT_ARCHITECTURE.md** (1h lectura + estudio) — entiende aislamiento de datos

Después, estás listo para implementar.

---

## ✨ RESUMEN EN 1 MINUTO

```
1 dominio (comerciales.cl)
1 VPS barato ($3.60/mes)
1 base de datos compartida
N locales (cada uno aislado por local_id)
= Costo bajo ($31.60/local/mes) + escalable

Timeline: 4 semanas
Effort: ~32 horas
Status: Listo para implementar NOW
```

---

**Siguiente:** Lee INFRAESTRUCTURA_SETUP_PLAN.md (15 min) ➡️

**¿Listo?** Mensajeame cuando Giuliano apruebe timeline.
