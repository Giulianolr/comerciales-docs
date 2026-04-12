# INFRAESTRUCTURA ECONÓMICA (v2)
## Reducción de costos: $125-185 USD → $32-42 USD/mes

**Versión:** 0.2 (Revisada para costo mínimo)  
**Presupuesto aprobado:** $20-40 USD/mes total  
**Aceptados:** Self-hosted + sin redundancia automática  

---

## 📊 COMPARATIVA ANTES vs DESPUÉS

### Opción 1: GCP Managed (Original - RECHAZADA)
```
Cloud Run Backend:      $15-30 USD/mes
Cloud SQL PostgreSQL:   $30-50 USD/mes
Memorystore Redis:      $25-40 USD/mes
Cloud Storage:          $5 USD/mes
Sentry/Monitoring:      $20+ USD/mes
SII (Bsale):            $28 USD/mes
────────────────────────────────────
TOTAL:                  $123-183 USD/mes ❌ MUY CARO
```

### Opción 2: Self-Hosted en VPS Barato (RECOMENDADO)
```
VPS Pequeño (Hetzner):  $5-7 USD/mes
  ├─ PostgreSQL self-hosted
  ├─ Redis self-hosted
  ├─ FastAPI backend
  └─ Vue frontend (static assets)
Dominio:                $2 USD/mes
DNS/SSL:                $0 USD/mes (Cloudflare free)
Backup (B2):            $0-3 USD/mes (primeros 10GB gratis)
SII (Bsale):            $28 USD/mes
────────────────────────────────────
TOTAL:                  $35-40 USD/mes ✅ VIABLE
```

---

## 🏗️ ARQUITECTURA ECONÓMICA PROPUESTA

```
┌─────────────────────────────────────────────────────────┐
│              FRONTEND (Vue 3 - Static)                  │
│  ├─ HTML/CSS/JS estáticos                              │
│  ├─ Alojado en: Cloudflare Pages (FREE) O VPS         │
│  ├─ CDN: Cloudflare (FREE tier)                        │
│  └─ Conexión: WebSocket + HTTP a backend               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         BACKEND (FastAPI en VPS Barato)                │
│         ┌─────────────────────────────────┐            │
│         │    VPS Hetzner Cloud CX31      │            │
│         │ 2 vCPU + 4GB RAM + 40GB SSD    │            │
│         │       (~$5-7 USD/mes)          │            │
│         └─────────────────────────────────┘            │
│              ↓              ↓              ↓            │
│         ┌────────┐   ┌────────┐   ┌─────────┐        │
│         │ FastAPI│   │Postgres│   │ Redis   │        │
│         │        │   │        │   │         │        │
│         │Port:   │   │Local   │   │Local    │        │
│         │8000    │   │5432    │   │6379     │        │
│         └────────┘   └────────┘   └─────────┘        │
│              ↓              ↓              ↓            │
│         ┌────────────────────────────────┐            │
│         │  Gunicorn + Supervisor         │            │
│         │  (autostart, restart on fail)  │            │
│         └────────────────────────────────┘            │
│              ↓              ↓                           │
│         ┌────────────────────────────────┐            │
│         │  Nginx (reverse proxy, SSL)    │            │
│         │  puerto 80 → 443 (HTTPS)       │            │
│         └────────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│              INTEGRACIONES EXTERNAS                     │
├─────────────────────────────────────────────────────────┤
│ SII (Bsale):    $28 USD/mes (FIJO, no negociable)     │
│ Dominio:        $2 USD/mes (nombre.cl en NIC Chile)   │
│ Cloudflare:     $0 USD/mes (DNS + SSL gratis)         │
│ B2 Backups:     $0-3 USD/mes (10GB gratis/mes)        │
│ Email:          $0 USD/mes (sendgrid free tier)       │
│ WhatsApp alerts: $0 USD/mes (Twilio free o manual)    │
└─────────────────────────────────────────────────────────┘
```

---

## 💻 VPS RECOMENDADO: HETZNER CLOUD CX31

**¿Por qué Hetzner?**
- ✅ Precio: €3.29/mes (~$3.60 USD) — MÁS BARATO que DigitalOcean ($5)
- ✅ Infraestructura: Excelente, servidores en Alemania/Finlandia
- ✅ Performance: 2 vCPU + 4GB RAM = suficiente para 200 transacciones/día
- ✅ Storage: 40GB SSD (suficiente para BD + logs 6 meses)
- ✅ Backup: Snapshots por $0.16 USD (opcional)

### Alternativas (si Hetzner no está disponible en Chile):
| Proveedor | Costo | Specs | Ventaja |
|-----------|-------|-------|---------|
| **Hetzner CX31** | €3.29/mes | 2vCPU, 4GB, 40GB | 🥇 BARATO |
| **DigitalOcean** | $5/mes | 1vCPU, 1GB, 25GB | Popular en latam |
| **Linode Nanode** | $5/mes | 1vCPU, 1GB, 25GB | Bueno |
| **Vultr** | $2.50/mes | 1vCPU, 512MB, 10GB | MÁS barato (muy límite) |
| **Render** | FREE | 1 dyno, auto-sleep | Limitado, para MVP |

**RECOMENDACIÓN:** Hetzner CX31 (mejor relación precio/performance)

---

## 📦 STACK SIMPLIFICADO (Self-Hosted)

### Backend
```
FastAPI (Python)
├─ Gunicorn (app server)
├─ Nginx (reverse proxy + SSL)
├─ PostgreSQL 15 (localhost)
├─ Redis (localhost, para sessions/cache)
└─ Supervisor (autostart, monitor procesos)

No needed:
❌ Cloud Build (usar GitHub Actions local o manual SSH)
❌ Artifact Registry (build en VPS o pre-build en dev)
❌ Secret Manager (usar variables env o .env.local)
❌ Cloud Logging (usar journalctl, ELK local opcional)
```

### Frontend
```
Vue 3 build estático
├─ Compilado con Vite
├─ Servido por Nginx (desde /var/www/html)
├─ Cloudflare CDN (free tier)
└─ Actualización: Git pull + npm run build vía webhook

No needed:
❌ Cloud Storage (usar VPS storage)
❌ Cloud CDN (usar Cloudflare free)
```

### Database
```
PostgreSQL 15 (self-hosted en /var/lib/postgresql)
├─ Backup local: pg_dump en cron job
├─ Backup cloud: B2 (Backblaze) free tier
├─ Replicación: NO (aceptamos downtime risk)
└─ Monitoreo: Supervisión manual o alertas simples

Alternativa: MariaDB/MySQL si prefieres
```

### Monitoreo & Logs
```
Simple (sin Sentry/Datadog):
├─ Journalctl para logs del sistema
├─ FastAPI logs a archivos
├─ Cron job: alerts por email si error rate sube
├─ Health check simple: GET /api/v1/health

Opcional (si budget permite):
├─ Sentry free tier (10k errors/month)
├─ Simple uptime monitor (StatusCake free)
└─ Email alerts (SendGrid free 100/día)
```

---

## 💰 DESGLOSE DE COSTOS (MENSUAL)

### PILOTO 1 LOCAL (50-200 tx/día)

| Item | Costo USD | Costo CLP | Notas |
|------|-----------|-----------|-------|
| **VPS Hetzner CX31** | $3.60 | 3,240 | 2vCPU, 4GB, 40GB SSD |
| **Dominio (.cl)** | $2.00 | 1,800 | NIC Chile, renovación anual |
| **Cloudflare** | $0.00 | - | DNS + SSL free tier ✅ |
| **B2 Backups** | $0.00 | - | 10GB/mes free ✅ |
| **SendGrid Email** | $0.00 | - | 100 emails/día free ✅ |
| **SII (Bsale)** | $28.00 | 25,200 | FIJO, no negociable |
| **Slack/Notificaciones** | $0.00 | - | Free o por email |
| | **TOTAL** | **$33.60** | **~30,240 CLP/mes** |

### ESCALADO A 5-10 LOCALES (después)

| Item | Costo USD | Notas |
|------|-----------|-------|
| **VPS Hetzner CX41** | $8.00 | Upgrade: 4vCPU, 8GB, 80GB (si necesario) |
| **Dominio (por local)** | $2.00 × 10 | $20 total para 10 locales |
| **SII (Bsale × 10)** | $28.00 × 10 | $280 total para 10 locales |
| | **TOTAL INFRAESTRUCTURA** | **$328/mes para 10 locales** |
| | **POR LOCAL** | **$32.80/mes** |

---

## 🔧 ARQUITECTURA TÉCNICA SIMPLIFICADA

### Folder Structure en VPS

```bash
/home/app/
├── comerciales-backend/          # Clone del repo
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routes/
│   │   └── services/
│   ├── migrations/
│   ├── requirements.txt
│   ├── .env                       # Variables (secretas)
│   └── wsgi.py                    # Para Gunicorn
│
├── comerciales-frontend/          # Clone del repo
│   ├── dist/                      # Build estático (servido por Nginx)
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
└── scripts/
    ├── deploy.sh                  # Script deploy manual
    ├── backup.sh                  # Backup DB a B2 (cron job)
    ├── health-check.sh           # Monitoring simple
    └── restart-services.sh        # En caso de crash
```

### Procesos en VPS (via Supervisor)

```ini
# /etc/supervisor/conf.d/comerciales.conf

[program:comerciales-api]
command=/home/app/venv/bin/gunicorn \
    -w 4 \
    -b 127.0.0.1:8000 \
    comerciales_backend.wsgi:app
directory=/home/app/comerciales-backend
autostart=true
autorestart=true
stderr_logfile=/var/log/comerciales/api-error.log
stdout_logfile=/var/log/comerciales/api-access.log

[program:comerciales-redis]
command=/usr/bin/redis-server /etc/redis/redis.conf
autostart=true
autorestart=true
```

### Nginx Config (SSL gratis con Cloudflare)

```nginx
# /etc/nginx/sites-available/comerciales

upstream api_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name comerciales.tudominio.cl;
    
    # Frontend estático
    location / {
        root /var/www/comerciales;
        try_files $uri /index.html;
    }
    
    # API backend
    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
    }
}
```

---

## 📦 INSTALACIÓN & DEPLOYMENT (Simplificado)

### Setup Inicial (1 vez)
```bash
# 1. SSH a VPS
ssh root@[IP-VPS]

# 2. Setup básico
apt-get update && apt-get upgrade -y
apt-get install -y nginx postgresql redis-server supervisor python3.11 git

# 3. Clone repos
cd /home/app
git clone https://github.com/[org]/comerciales-backend.git
git clone https://github.com/[org]/comerciales-frontend.git

# 4. Backend setup
cd comerciales-backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m alembic upgrade head

# 5. Frontend build
cd ../comerciales-frontend
npm install
npm run build
cp -r dist/* /var/www/comerciales/

# 6. Start services
supervisorctl reread
supervisorctl update
supervisorctl start comerciales-api
systemctl start redis-server
systemctl restart nginx
```

### Deploy Después de Cambios
```bash
# En VPS (manualmente o via GitHub webhook)
cd /home/app/comerciales-backend
git pull origin develop
source venv/bin/activate
pip install -r requirements.txt
supervisorctl restart comerciales-api

cd ../comerciales-frontend
git pull origin develop
npm install
npm run build
cp -r dist/* /var/www/comerciales/
```

---

## ⚠️ TRADE-OFFS & RIESGOS (Aceptados)

| Trade-off | Impacto | Mitigación |
|-----------|---------|-----------|
| **Sin redundancia** | Si VPS falla → downtime total | Backup en B2, puede recuperarse en 30 min |
| **Sin auto-scaling** | Si tráfico sube → slow | Monitoreo manual, upgrade VPS si necesario |
| **Sin failover automático** | Downtime manual | Alertas por email, restart manual en 5 min |
| **Self-hosted DevOps** | Devs deben manejar ops | Allan capacitado, docs en runbooks |
| **No managed DB** | Sin backups automáticos | Cron job diario, B2 backup |
| **Sin CDN global** | Latencia para usuarios lejanos | Cloudflare free (DNS acceleration) |

**Pero es VIABLE para:**
- ✅ 50-200 transacciones/día
- ✅ 1-2 locales piloto
- ✅ Uptime razonable (99% si monitoreo)
- ✅ Recuperación rápida ante fallos

---

## 📈 ESCALADO FUTURO

### Cuando llegues a 10+ locales o >500 tx/día:
```
Upgrade Path:
1. VPS CX41 (4vCPU, 8GB): $8/mes
2. PostgreSQL managed (Heroku/Railway): +$50/mes (opcional)
3. Redis managed: +$5/mes (opcional)
4. Monitoring avanzado (Sentry): +$50/mes (opcional)

NUEVO TOTAL: ~$100-150 USD/mes para 10 locales + infra robust
```

---

## 🎯 CHECKLIST PRE-DEPLOYMENT

### Antes de ir a producción:
- [ ] Acceso SSH al VPS
- [ ] PostgreSQL corriendo, BD inicializada
- [ ] Redis corriendo
- [ ] FastAPI en Gunicorn funciona
- [ ] Nginx reverse proxy configurado
- [ ] Frontend build estático funciona
- [ ] SSL certificado en Cloudflare
- [ ] Backup script en cron (diario)
- [ ] Health check respondiendo
- [ ] Logs configurados
- [ ] SII (Bsale) API key en .env
- [ ] Alerts por email configuradas

---

## 💡 ALTERNATIVAS AÚN MÁS BARATAS (Si necesario)

### Opción A: Render.com (Free tier con limitaciones)
```
Render Web Service: FREE (con auto-sleep)
  ├─ PostgreSQL: FREE (pero 90 días límite, luego $12/mes)
  ├─ Redis: FREE (pero 90 días límite, luego $15/mes)
  └─ Downtime: 15 min inactividad
Bsale: $28 USD/mes
──────────────
TOTAL: $28 USD/mes (primeros 3 meses), luego $55+

⚠️ NO RECOMENDADO para producción
```

### Opción B: Railway.app (Free tier también)
```
Similar a Render, también con downtime después 3 meses
```

---

## ✅ RECOMENDACIÓN FINAL

**USAR: Hetzner CX31 Self-Hosted (~$33.60 USD/mes)**

✅ Presupuesto viable ($33 < $40 límite)  
✅ Suficiente poder (2vCPU, 4GB RAM)  
✅ Escalable (upgrade a CX41 si crece)  
✅ Sin vendor lock-in  
✅ Control total  

**ACEPTADOS TRADE-OFFS:**
- Self-hosted (Allan maneja DevOps con documentación)
- Sin redundancia (acceptable para piloto)
- Downtime manual (pero rápido de recuperar)

---

**Versión:** 0.2  
**Actualizado:** 5 de abril 2026  
**Costo total:** $33.60 USD/mes (~30,240 CLP/mes)  
**Payback:** Sigue siendo 2-3 meses (ROI no cambia)
