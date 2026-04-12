# ESTRATEGIA HÍBRIDA: GCP FREE TRIAL + VPS
## Plan de desarrollo en GCP (gratis) + producción en VPS (bajo costo)

**Versión:** 0.1  
**Fecha:** 6 de abril de 2026  
**Para:** PM (Giuliano), Backend Dev (Allan)  
**Timeline:** 6 abril - 20 julio (14 semanas)

---

## 📊 VISIÓN GENERAL

```
FASE 1: DESARROLLO (6 abril - 5 julio = 13 semanas)
├─ Infraestructura: GCP Cloud Run + Cloud SQL + Redis
├─ Costo: $0 USD (GCP free trial)
├─ Ventaja: Rápido, managed, sin DevOps complexity
├─ Riesgo: Trial expira 5 julio
└─ Status: ✅ MEJOR PARA DESARROLLO

     ↓↓↓ MIGRACIÓN CRÍTICA (Semana 11-12) ↓↓↓

FASE 2: PRODUCCIÓN (6 julio - infinito)
├─ Infraestructura: VPS Hetzner CX31 + PostgreSQL + Redis
├─ Costo: $33.60 USD/mes (~30k CLP/mes)
├─ Ventaja: Estable, bajo costo, control total
├─ Riesgo: Requiere DevOps (Allan)
└─ Status: ✅ SEGURO PARA PRODUCCIÓN

COSTO TOTAL AÑO 1: $0 (dev) + $169 (prod, 5 meses) = $169 USD
```

---

## 🗓️ TIMELINE DETALLADO

```
ABRIL 2026
────────────────────────────────────────────────────────
6    Sprint 0 comienza
     ├─ Setup GCP project
     ├─ Cloud Run + Cloud SQL + Redis
     ├─ Primeros endpoints FastAPI
     └─ Free trial activo ✅ (~$0/mes)

MAYO 2026
────────────────────────────────────────────────────────
6    Sprint 1 comienza (Semana 2)
     ├─ Módulo Inventario operativo
     └─ Testing en GCP ✅ ($0/mes)

20   Sprint 2 comienza (Semana 3)
     ├─ Módulo Balanza + Estaciones
     └─ WebSocket testing en GCP ✅ ($0/mes)

JUNIO 2026
────────────────────────────────────────────────────────
3    Sprint 3 comienza (Semana 5)
     ├─ Módulo Caja + POS
     └─ Testing integral en GCP ✅ ($0/mes)

17   Sprint 4 comienza (Semana 7)
     ├─ Integración SII (Bsale)
     ├─ Auditoría completa
     └─ Full testing en GCP ✅ ($0/mes)

    ⚠️ SEMANA 11 - CRÍTICA (30 junio)
    ├─ 🚨 MIGRACIÓN COMIENZA
    ├─ Crear VPS Hetzner
    ├─ Migrar DB GCP → VPS
    ├─ Testing en VPS (staging)
    └─ Backup completo antes de cutover

JULIO 2026
────────────────────────────────────────────────────────
5    🚨 FREE TRIAL DE GCP EXPIRA
     ├─ Trial → Billing start en GCP (sin pago si migrado)
     ├─ DEADLINE: Sistema debe estar en VPS
     └─ Si falla → Downtime

6    Cutover a VPS (cambio DNS)
     ├─ Cambiar registros DNS a VPS IP
     ├─ Validar conectividad
     ├─ Monitoreo 24/7
     └─ Rollback plan listo

15   Sprint 5 comienza (Semana 10 - POST-MIGRACIÓN)
     ├─ Analytics + Dashboards
     ├─ Sistema en VPS estable ✅
     └─ Testing en ambiente real

20   Sprint 6 comienza (Semana 12)
     ├─ QA final + testing end-to-end
     ├─ Capacitación operadores
     └─ Sistema LISTO PARA PRODUCCIÓN ✅

     🎉 FIN: SISTEMA EN PRODUCCIÓN (20 julio)
     └─ Clientes reales usando VPS Hetzner
```

---

## 💰 DESGLOSE DE COSTOS

### Fase 1: GCP Free Trial (6 abril - 5 julio)

```
Periodo:           6 abril - 5 julio = 13 semanas
Cloud Run:         GRATIS (dentro de free tier)
Cloud SQL:         GRATIS (db-f1-micro gratis)
Memorystore:       GRATIS (Redis 1GB gratis)
Cloud Storage:     GRATIS (5GB gratis)
───────────────────────────────────────────────────
TOTAL:             $0 USD ✅
```

### Fase 2: VPS Producción (6 julio - 20 julio + después)

```
Periodo:           6 julio onwards
VPS Hetzner:       $3.60 USD/mes
Dominio:           $2.00 USD/mes
Cloudflare:        $0 USD/mes
B2 Backups:        $0 USD/mes (10GB gratis)
SII (Bsale):       $28 USD/mes
───────────────────────────────────────────────────
TOTAL:             $33.60 USD/mes (~30k CLP/mes)

5 meses (6 jul - 31 dic): $168 USD
```

### Año 1 Total

```
Desarrollo (13 semanas):    $0 USD   (GCP free)
Producción (5 meses):       $168 USD (VPS)
───────────────────────────────────
AÑO 1 TOTAL:                $168 USD (~151k CLP)

AÑO 2+ (12 meses):          $403 USD/año (solo VPS)
```

---

## 🔄 PLAN DE MIGRACIÓN (Detallado)

### ANTES DE INICIAR (Semana 10, ~30 junio)

**Checklist pre-migración:**
- [ ] Backup completo de GCP Cloud SQL
- [ ] VPS Hetzner creado y funcional
- [ ] PostgreSQL en VPS testado
- [ ] Redis en VPS testado
- [ ] Nginx configurado
- [ ] Certificado SSL ready (Cloudflare)
- [ ] Dominio apunta a server temporal
- [ ] Plan B documentado (rollback)
- [ ] Equipo notificado (sin usuarios reales aún)

### PASO 1: Crear VPS en Paralelo (2-3 días)

**Sin afectar desarrollo:**

```bash
# En Hetzner Cloud dashboard
1. Crear instancia CX31 (2vCPU, 4GB, 40GB SSD)
2. OS: Ubuntu 22.04 LTS
3. Región: Europa (Alemania) u otra cercana a Chile

# SSH a VPS
ssh root@[VPS_IP]

# Setup básico
apt update && apt upgrade -y
apt install -y nginx postgresql redis-server supervisor python3.11 git

# PostgreSQL
systemctl start postgresql
psql --version

# Redis
systemctl start redis-server
redis-cli ping  # Debería responder PONG

# Nginx
systemctl start nginx
curl localhost  # Debería responder algo
```

**Duración:** 2-3 horas de trabajo

### PASO 2: Preparar Database (1 día)

**Exportar desde GCP:**

```bash
# En tu Mac/Local, conectado a GCP Cloud SQL
gcloud sql export sql comerciales-db \
  gs://comerciales-backups/db-backup-2026-06-30.sql \
  --database=comerciales_db

# Descargar backup localmente
gsutil cp gs://comerciales-backups/db-backup-2026-06-30.sql ./db-backup.sql

# Verificar tamaño
ls -lh db-backup.sql  # Debería ser <100MB
```

**Importar a VPS:**

```bash
# Copiar archivo a VPS
scp db-backup.sql root@[VPS_IP]:/tmp/

# En VPS, restaurar
ssh root@[VPS_IP]

# Crear BD vacía
sudo -u postgres createdb comerciales_db

# Restaurar
sudo -u postgres psql comerciales_db < /tmp/db-backup.sql

# Verificar
sudo -u postgres psql -d comerciales_db -c "SELECT COUNT(*) FROM products;"
```

**Duración:** 2-4 horas (depende de tamaño DB)

### PASO 3: Replicar Backend & Frontend (1 día)

**Backend:**

```bash
# En VPS
cd /home/app
git clone https://github.com/Giulianolr/comerciales-backend.git
cd comerciales-backend

# Setup venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Update .env con credenciales VPS
# DATABASE_URL=postgresql://app:password@localhost/comerciales_db
# REDIS_URL=redis://localhost:6379

# Migrations
alembic upgrade head

# Test local
python -m uvicorn app.main:app --reload
```

**Frontend:**

```bash
# En tu local
cd comerciales-frontend
npm install
npm run build

# Copiar a VPS
scp -r dist/* root@[VPS_IP]:/var/www/comerciales/

# En VPS, verificar
ls -la /var/www/comerciales/
```

**Duración:** 2-3 horas

### PASO 4: Configurar Nginx & SSL (1 día)

**Nginx config:**

```bash
# En VPS, crear archivo
sudo nano /etc/nginx/sites-available/comerciales

# Agregar (ver INFRAESTRUCTURA_ECONOMICA.md para config completa):
```

```nginx
upstream api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name comerciales.tudominio.cl;
    
    location / {
        root /var/www/comerciales;
        try_files $uri /index.html;
    }
    
    location /api/ {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Habilitar site
sudo ln -s /etc/nginx/sites-available/comerciales \
  /etc/nginx/sites-enabled/comerciales

# Validar config
sudo nginx -t

# Restart
sudo systemctl restart nginx

# SSL (Cloudflare, luego agrupar en producción)
# Por ahora: HTTP puro está OK (staging)
```

**Duración:** 1-2 horas

### PASO 5: Supervisor & Autostart (1 día)

**Configurar procesos:**

```bash
# En VPS, crear /etc/supervisor/conf.d/comerciales.conf

[program:comerciales-api]
command=/home/app/comerciales-backend/venv/bin/gunicorn \
    -w 4 \
    -b 127.0.0.1:8000 \
    app.wsgi:app
directory=/home/app/comerciales-backend
autostart=true
autorestart=true
stderr_logfile=/var/log/comerciales-api-error.log
stdout_logfile=/var/log/comerciales-api-access.log

[program:comerciales-redis]
command=/usr/bin/redis-server /etc/redis/redis.conf
autostart=true
autorestart=true

# Aplicar
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

**Duración:** 1 hora

### PASO 6: Testing en Staging (2-3 días)

**Validar TODO:**

```bash
# 1. Health check
curl https://[VPS_IP]/health

# 2. API básica
curl https://[VPS_IP]/api/v1/products

# 3. WebSocket
wscat -c wss://[VPS_IP]/api/v1/ws

# 4. Database
curl https://[VPS_IP]/api/v1/stations

# 5. SII integración
# Hacer test de emisión de boleta

# 6. Performance
ab -n 100 -c 10 https://[VPS_IP]/api/v1/products

# 7. Logs
tail -f /var/log/comerciales-api-access.log
```

**Duración:** 2-3 horas

### PASO 7: Preparar Cutover (1 día)

**Backup final y rollback plan:**

```bash
# Backup FINAL en VPS (horas antes de cutover)
sudo -u postgres pg_dump comerciales_db > \
  /home/app/backups/db-pre-cutover-2026-07-06.sql

# Backup a B2
b2 sync /home/app/backups b2://comerciales-backups/pre-cutover/

# Documentar IPs:
GCP_CLOUD_RUN_IP=xxx.run.app
VPS_IP=1.2.3.4
DOMINIO=comerciales.tudominio.cl

# Rollback plan ready:
# Si algo falla, cambiar DNS back a GCP (1 min)
```

**Duración:** 1 hora

---

## 🔄 CUTOVER (El día 5-6 de julio)

### Cronograma Exacto

```
18:00 (Tarde previa)
└─ Notificación: "System will be down for 1 hour tonight"
└─ Backup final en ambos sistemas
└─ Equipo en standby

20:00 (Noche, sin usuarios)
└─ 🚨 INICIO CUTOVER
└─ Parar GCP Cloud Run
└─ Verificar data en VPS está actualizada
└─ Cambiar DNS: dominio.cl → VPS IP

20:05 (5 minutos después)
└─ Validar que dominio apunta a VPS
└─ Test: curl dominio.cl → debe responder desde VPS
└─ Validar todas las rutas API

20:30 (30 minutos después)
└─ Si TODO OK: ✅ CUTOVER EXITOSO
└─ Si hay problemas: Cambiar DNS back a GCP
└─ Monitorear logs

21:00 (1 hora después)
└─ Validación final
└─ Notificación: "System is back online"

22:00 - 06:00
└─ Monitoreo intenso 8 horas
└─ Alerts por email si hay errores
└─ Rollback ready si necesario
```

### Rollback Plan (Si algo falla)

```bash
# Cambiar DNS back a GCP (5 minutos max)
# 1. DNS provider (NIC Chile o Cloudflare)
# 2. Cambiar A record: dominio.cl → GCP Cloud Run IP
# 3. Esperar DNS propagación (5-15 min)
# 4. Validar
# 5. Comunicar: "Temporary revert to GCP, investigating issue"

# Post-morttem:
# - Identificar problema
# - Fixear en VPS
# - Re-intentar cutover siguiente día
```

---

## 📋 DOCUMENTO DE CHECKLIST

### Pre-Migration (Semana 10, 30 junio)

- [ ] Backup completo GCP (SQL + assets)
- [ ] VPS Hetzner CX31 creado
- [ ] PostgreSQL en VPS funcional
- [ ] Redis en VPS funcional
- [ ] Backend clonado en VPS
- [ ] Frontend build en VPS
- [ ] Nginx configurado
- [ ] Supervisor configurado
- [ ] Database restaurada (test)
- [ ] API respondiendo en VPS
- [ ] WebSocket funcionando en VPS
- [ ] SII sandbox testing exitoso
- [ ] Rollback plan documentado
- [ ] Equipo notificado

### Día de Cutover (5-6 julio)

- [ ] Final backup en GCP
- [ ] Final backup en VPS
- [ ] DNS provider accesible
- [ ] Team en Slack/llamada
- [ ] GCP Cloud Run apagado
- [ ] DNS cambiado a VPS
- [ ] Validación de todas las rutas
- [ ] Logs sin errores
- [ ] SII trabajando
- [ ] Users notificados

### Post-Cutover (7+ julio)

- [ ] Monitoreo 24/7 por 48h
- [ ] GCP desactivado (para no generar costos)
- [ ] VPS backup a B2 diarios
- [ ] Alertas configuradas
- [ ] Runbook actualizado

---

## 🎯 BENEFICIOS DE ESTA ESTRATEGIA

| Aspecto | Beneficio |
|---------|-----------|
| **Costo** | $0 en desarrollo, $33.60 en producción (vs $125+ todo el tiempo) |
| **Velocidad Dev** | GCP managed → rápido, sin DevOps complexity |
| **Estabilidad Prod** | VPS estable, sin sorpresas de downtime |
| **Migración** | Planificada, documentada, no caótica |
| **Experiencia** | Allan aprende DevOps en ambiente controlado |
| **Escalabilidad** | VPS soporta 500+ tx/día si es necesario |
| **Control** | Acceso total a infraestructura |

---

## ⚠️ RIESGOS & MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-----------|---------|-----------|
| Migración falla | BAJA (10%) | MEDIO | Rollback a GCP en 5 min |
| Data loss | MUY BAJA (1%) | CRÍTICO | Múltiples backups (GCP + B2 + local) |
| Performance problems VPS | BAJA (15%) | BAJO | Load testing pre-cutover |
| DNS propagación lenta | BAJA (5%) | BAJO | TTL bajo (5 min) pre-cutover |
| Downtime > 1 hora | MUY BAJA (2%) | CRÍTICO | Runbook detallado, team listo |

---

## 📞 CONTACTOS DURANTE MIGRACIÓN

```
PM (Giuliano):        Decisiones, comunicación cliente
Backend (Allan):      Ejecución técnica, troubleshooting
Ops (¿Alguien?):      Monitoreo, alertas
Support:              ¿disponible 24/7?
```

---

## 📝 DOCUMENTOS RELACIONADOS

- `INFRAESTRUCTURA_ECONOMICA.md` — Setup VPS detallado
- `SETUP_GCP_VSCODE.md` — Setup GCP para desarrollo
- `PROXIMOS_PASOS.md` — Plan inmediato (semanas 0-1)

---

**Versión:** 0.1  
**Última actualización:** 6 de abril 2026  
**Próxima revisión:** Semana 10 (30 junio, pre-migración)  
**Responsable:** PM (Giuliano) + Backend (Allan)
