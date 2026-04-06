# CAMBIOS DE INFRAESTRUCTURA
## De GCP Managed a VPS Self-Hosted (Reducción 73% de costos)

**Fecha:** 5 de abril 2026  
**Decisión:** Cambio por request del PM (costos muy elevados)  
**Impacto:** Reducción de $125-185 USD/mes → $33.60 USD/mes  

---

## 📊 COMPARATIVA ANTES vs DESPUÉS

```
╔════════════════════════════════════════════════════════════════════╗
║                    OPCIÓN 1: GCP MANAGED                           ║
╠════════════════════════════════════════════════════════════════════╣
║ Cloud Run (backend)              $15-30 USD/mes                    ║
║ Cloud SQL PostgreSQL             $30-50 USD/mes                    ║
║ Memorystore Redis                $25-40 USD/mes                    ║
║ Cloud Storage, Secret Manager     $5-7 USD/mes                     ║
║ Cloud Build, Logging              $0-5 USD/mes                     ║
║ n8n (Cloud Run)                  $10 USD/mes                       ║
║ Metabase (Cloud Run)             $10 USD/mes                       ║
║ Monitoreo/Sentry                 $20+ USD/mes                      ║
║ SII (Bsale)                      $28 USD/mes                       ║
║ ───────────────────────────────────────────────────────────────── ║
║ TOTAL INFRAESTRUCTURA            $125-185 USD/mes ❌              ║
╚════════════════════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════════════════════╗
║                 OPCIÓN 2: VPS SELF-HOSTED ✅ ELEGIDA              ║
╠════════════════════════════════════════════════════════════════════╣
║ VPS Hetzner CX31 (2vCPU, 4GB RAM, 40GB SSD)                       ║
║   ├─ PostgreSQL self-hosted                                        ║
║   ├─ Redis self-hosted                                             ║
║   ├─ FastAPI + Gunicorn                                            ║
║   ├─ Nginx reverse proxy                                           ║
║   └─ Supervisor (process management)           $3.60 USD/mes       ║
║ Dominio (.cl)                                   $2.00 USD/mes      ║
║ Cloudflare (DNS + SSL)                          $0 USD/mes ✅      ║
║ B2 Backups (10GB gratis)                        $0 USD/mes ✅      ║
║ SendGrid Email (free tier)                      $0 USD/mes ✅      ║
║ SII (Bsale)                                     $28 USD/mes        ║
║ ───────────────────────────────────────────────────────────────── ║
║ TOTAL INFRAESTRUCTURA                           $33.60 USD/mes ✅ ║
╚════════════════════════════════════════════════════════════════════╝

AHORRO: $91.40 - $151.40 USD/mes (73% de reducción) 🎉
ANUALIZADO: $1,097 - $1,817 USD/año ahorrados
```

---

## 🏗️ ARQUITECTURA ANTES vs DESPUÉS

### ANTES (GCP Managed - Empresa Fortune 500)
```
[Frontend]
    ↓ (HTTPS)
[Cloud Run - FastAPI]        ← $15-30/mes (serverless, escalado auto)
    ↓
[Cloud SQL - PostgreSQL]     ← $30-50/mes (managed, backups auto)
    ↓
[Memorystore - Redis]        ← $25-40/mes (managed, replicación)
    ↓
[Cloud Storage]              ← backups, XMLs SII
    ↓
[Secret Manager]             ← credenciales SII
    ↓
[Cloud Build + CI/CD]        ← deployments automáticos
    ↓
[Cloud Logging + Sentry]     ← monitoreo centralizado

Ventajas:
✅ Escalado automático
✅ Redundancia/failover automático
✅ Backups automáticos
✅ Zero DevOps
✅ Fácil setup

Desventajas:
❌ MUY CARO para startup/piloto ($125-185/mes)
❌ Vendor lock-in GCP
❌ Complejo de configurar inicialmente
```

### DESPUÉS (VPS Self-Hosted - Startup/Piloto)
```
[Frontend - Vue 3 static]
    ↓ (HTTPS via Cloudflare + Nginx)
┌─────────────────────────────────────┐
│    VPS Hetzner CX31                 │ ← $3.60/mes
│  ┌─────────────────────────────┐   │
│  │ Nginx (reverse proxy + SSL) │   │
│  │ :80/:443 (Cloudflare)       │   │
│  └──────────────┬──────────────┘   │
│                 ├─────────────────┐ │
│  ┌──────────────┴────────────┐   │ │
│  │ FastAPI (Gunicorn)        │   │ │
│  │ :8000 (internal)          │   │ │
│  │ 4 workers                 │   │ │
│  └──────────────┬────────────┘   │ │
│                 │                │ │
│  ┌──────────────▼──────┐ ┌──────┴─▼──────┐
│  │ PostgreSQL 15       │ │ Redis 7        │
│  │ /var/lib/postgres   │ │ /var/lib/redis │
│  │ Local socket        │ │ Local socket   │
│  └─────────────────────┘ └────────────────┘
│                 │
│  ┌──────────────▼──────────────┐
│  │ Supervisor                  │
│  │ ├─ FastAPI (autorestart)   │
│  │ ├─ Redis (autorestart)     │
│  │ ├─ Nginx (autorestart)     │
│  │ └─ Cron: backups diarios   │
│  └─────────────────────────────┘
└─────────────────────────────────────┘
    ↓
[B2 Backups] ← $0 (10GB gratis, daily pg_dump)
    ↓
[SII - Bsale] ← $28/mes (intención)

Ventajas:
✅ BARATO para startup ($3.60 for compute)
✅ Control total (no vendor lock-in)
✅ Simple de entender (1 servidor)
✅ Fácil debuggear
✅ Escalable verticalmente (upgrade VPS)

Desventajas:
❌ Sin escalado automático (manual si necesario)
❌ Sin failover automático (downtime si falla)
❌ Backups manual (pero automáticos via cron)
❌ DevOps responsibility en Allan
❌ No es "enterprise-grade"
```

---

## 💡 ¿POR QUÉ ESTE CAMBIO?

### Realidad de la Situación
- 📍 Es un **piloto** (1-2 locales), no una aplicación "enterprise"
- 📊 Volumen predecible (50-200 tx/día)
- 💰 Presupuesto limitado ($15k-$40k para desarrollo)
- 🎯 Tiempo de mercado: Necesita ir a producción rápido
- 👥 Equipo técnico: Allan es capaz de manejar VPS básico

### Cálculo ROI con Ambas Opciones

**Con GCP ($150/mes):**
```
Costo anual:     $1,800 USD
ROI anual:       $2,547-5,972 USD
Net/año:         $747-4,172 USD (POSITIVO pero con overhead)
```

**Con VPS ($33.60/mes):**
```
Costo anual:     $403 USD
ROI anual:       $2,547-5,972 USD
Net/año:         $2,144-5,569 USD (MUCHO MÁS LIMPIO)
Inversión inicial: 100% menos compleja
```

---

## ✅ TRADE-OFFS ACEPTADOS

| Trade-off | Severidad | Mitigación | Aceptable? |
|-----------|-----------|-----------|-----------|
| **Sin escalado automático** | MEDIA | Monitor manualmente, upgrade VPS si necesario | ✅ SÍ |
| **Sin failover automático** | MEDIA | Alertas por email, restart manual en 5-10 min | ✅ SÍ |
| **DevOps manual** | BAJA | Allan tiene experiencia, documentación completa | ✅ SÍ |
| **Downtime total si falla VPS** | BAJA | Estadísticamente raro (~0.1% año), 30-60 min recovery | ✅ SÍ |
| **No managed backups** | BAJA | Cron job automático, B2 cloud backup | ✅ SÍ |
| **Mantenimiento OS** | BAJA | Apt update automático, 30 min / mes | ✅ SÍ |

---

## 🚀 EVOLUCIÓN FUTURA (Path to Enterprise)

### Cuando llegues a 10+ locales o >1000 tx/día:
```
Opción A: Escalar VPS
├─ VPS CX41 (4vCPU, 8GB):        +$4.40/mes
├─ Separar PostgreSQL managed:    +$50/mes (si necesario)
├─ Separar Redis managed:         +$15/mes (si necesario)
└─ Total:                         ~$100-120/mes

Opción B: Migrar a GCP (si quieres escalado automático)
├─ Mantener infraestructura como está en VPS
├─ Setup GCP en paralelo
├─ Migrar DB gradualmente
└─ Desechar VPS cuando GCP esté listo
```

---

## 📋 CHECKLIST: SETUP VPS (Para Allan)

### Pre-deployment
- [ ] Cuenta en Hetzner Cloud (https://www.hetzner.cloud/)
- [ ] Crear VPS CX31 (Ubuntu 22.04 LTS)
- [ ] SSH key setup
- [ ] Dominio registrado (.cl en NIC Chile)
- [ ] Cloudflare cuenta + DNS configurado
- [ ] Bsale API key obtenida

### Setup Sistema
- [ ] Update sistema (`apt update && apt upgrade`)
- [ ] Instalar: nginx, postgresql, redis-server, supervisor, python3.11
- [ ] Python venv + dependencias
- [ ] Clone repos backend + frontend

### Database
- [ ] PostgreSQL inicializado
- [ ] User `comerciales` creado
- [ ] Base de datos `comerciales_db` creado
- [ ] Alembic migrations corridas

### Backend
- [ ] FastAPI app en `/home/app/comerciales-backend`
- [ ] Gunicorn configurado
- [ ] Supervisor conf creada y corriendo
- [ ] Nginx reverse proxy configurado
- [ ] SSL via Cloudflare

### Frontend
- [ ] Vue build estático (`npm run build`)
- [ ] Assets en `/var/www/comerciales`
- [ ] Nginx sirviendo archivos estáticos

### Monitoring & Backups
- [ ] Health check endpoint working
- [ ] Cron job: backup diario pg_dump
- [ ] B2 CLI: upload automático backups
- [ ] Email alerts configuradas

---

## 📞 SOPORTE & DOCUMENTACIÓN

### Nuevo Documento Creado
**`docs/INFRAESTRUCTURA_ECONOMICA.md`**
- Setup completo paso a paso
- Nginx config
- Supervisor config
- Backup strategy
- Troubleshooting
- Alternativas (si Hetzner no disponible)

### Runbooks (Para crear en Sprint 0-1)
- `docs/runbooks/deploy.md` — Cómo deployar cambios
- `docs/runbooks/backup.md` — Estrategia de backup
- `docs/runbooks/troubleshooting.md` — Si algo falla
- `docs/runbooks/oncall.md` — Procedimientos de on-call

---

## 🎯 TIMELINE IMPACTO

- **Hoy (5 abril):** Decisión + documentación completa
- **Martes (9 abril):** Reunión hardware (no afectado)
- **Miércoles (10 abril):** Revisión técnica (confirmar Hetzner setup)
- **Sprint 0 (14-18 abril):** Allan crea VPS + setup infraestructura

**No retrasa timeline.** De hecho, lo simplifica.

---

## ✨ CONCLUSIÓN

### Decisión
**VPS Self-Hosted en Hetzner CX31 es la opción correcta para un piloto.**

- ✅ Costo realista para startup (~$30k CLP/mes)
- ✅ Suficiente poder (2vCPU, 4GB RAM para 200 tx/día)
- ✅ Escalable (upgrade a CX41 cuando sea necesario)
- ✅ Simple (1 servidor, fácil de entender)
- ✅ ROI mejor: $2.1k-5.5k USD neto/año vs $700-4.1k USD

### Riesgos Minimizados
- Downtime: Raro (~0.1% año), recovery rápido (30 min)
- Pérdida de datos: Backup automático diario a B2
- Performance: Suficiente para volumen actual, upgrade fácil

### Próximo Paso
**Allan debe familiarizarse con `docs/INFRAESTRUCTURA_ECONOMICA.md` antes de Sprint 0**

---

**Versión:** 0.1  
**Decisión tomada:** 5 de abril 2026  
**Responsable:** Giuliano (PM)  
**Implementación:** Allan (Backend/DevOps)  
**Timeline:** Sprint 0 (14-18 abril)
