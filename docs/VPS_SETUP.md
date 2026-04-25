# VPS SETUP COMPLETO
## Configuración automática de servidor Ubuntu 22.04 + PostgreSQL + Redis + FastAPI

**Para:** Allan (Backend/DevOps)  
**Tiempo:** ~2-3 horas (la mayoría es espera de instalación)  
**Requisitos previos:**
- VPS Hetzner CX31 creado (IP anotada)
- SSH access funcionando
- Dominio registrado + DNS apuntando al VPS

---

## FASE 1: SETUP INICIAL DEL SISTEMA (20 min)

### 1.1 SSH al servidor
```bash
ssh -i ~/.ssh/hetzner-key.pem root@[TU_IP_VPS]
# Reemplazar [TU_IP_VPS] con tu IP (ej: 1.2.3.4)
```

### 1.2 Update sistema
```bash
apt-get update && apt-get upgrade -y
```

### 1.3 Instalar utilidades básicas
```bash
apt-get install -y \
  curl \
  wget \
  git \
  htop \
  vim \
  nano \
  build-essential \
  certbot \
  python3-certbot-nginx \
  ufw
```

### 1.4 Configurar firewall
```bash
# Enable UFW
ufw enable

# Permitir SSH
ufw allow 22/tcp

# Permitir HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Verificar
ufw status
```

### 1.5 Crear usuario de aplicación (NO root)
```bash
# Crear usuario 'app'
adduser --disabled-password --gecos "" app

# Agregar permisos sudo
usermod -aG sudo app

# Cambiar a usuario app
su - app
```

---

## FASE 2: INSTALACIÓN DE DEPENDENCIAS (45 min)

### 2.1 Python 3.11 + venv
```bash
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
python3.11 --version
```

### 2.2 PostgreSQL 15
```bash
# Instalar
sudo apt-get install -y postgresql postgresql-contrib postgresql-client

# Iniciar servicio
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verificar
sudo -u postgres psql --version
```

### 2.3 Redis 7
```bash
# Instalar
sudo apt-get install -y redis-server

# Iniciar
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verificar
redis-cli ping
# Debería responder: PONG
```

### 2.4 Nginx
```bash
sudo apt-get install -y nginx

# Iniciar
sudo systemctl start nginx
sudo systemctl enable nginx

# Verificar
curl http://localhost
# Debería mostrar página default de Nginx
```

### 2.5 Supervisor (gestor de procesos)
```bash
sudo apt-get install -y supervisor

# Iniciar
sudo systemctl start supervisor
sudo systemctl enable supervisor
```

---

## FASE 3: CONFIGURACIÓN DE BASE DE DATOS (20 min)

### 3.1 Crear BD y usuario
```bash
# Conectar a PostgreSQL como admin
sudo -u postgres psql

# Dentro de psql, ejecutar:
CREATE USER comerciales WITH PASSWORD 'PASSWORD_SEGURO_AQUI';
CREATE DATABASE comerciales_db OWNER comerciales;
ALTER ROLE comerciales SET client_encoding TO 'utf8';
ALTER ROLE comerciales SET default_transaction_isolation TO 'read committed';
ALTER ROLE comerciales SET default_transaction_deferrable TO on;
ALTER ROLE comerciales SET timezone TO 'UTC';

# Verificar
\l
# Debería listar comerciales_db

# Salir
\q
```

### 3.2 Crear directorio para datos
```bash
sudo mkdir -p /var/lib/postgresql/backups
sudo chown postgres:postgres /var/lib/postgresql/backups
sudo chmod 700 /var/lib/postgresql/backups
```

### 3.3 Configurar PostgreSQL para aceptar conexiones locales
```bash
# Verificar que ya está configurado (Ubuntu por defecto permite local socket)
sudo -u postgres psql -c "SELECT datname FROM pg_database WHERE datname = 'comerciales_db';"
# Debería responder: comerciales_db
```

---

## FASE 4: CLONE REPOS Y SETUP BACKEND (45 min)

### 4.1 Clone del repositorio backend
```bash
# Crear carpeta de aplicaciones
sudo mkdir -p /home/app/comerciales-backend
sudo chown app:app /home/app/comerciales-backend
cd /home/app/comerciales-backend

# Clone (necesitarás token GitHub)
# Opción A: Si tienes SSH key en GitHub
git clone git@github.com:TuOrg/comerciales-backend.git .

# Opción B: Si usas HTTPS (pide GitHub token)
git clone https://github.com/TuOrg/comerciales-backend.git .
# Luego pega token cuando pida password
```

### 4.2 Crear venv e instalar dependencias
```bash
cd /home/app/comerciales-backend

# Crear virtualenv
python3.11 -m venv venv

# Activar
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Verificar que funciona
python -c "import fastapi; print(fastapi.__version__)"
```

### 4.3 Configurar variables de entorno
```bash
# Crear archivo .env
nano /home/app/comerciales-backend/.env

# Pegar esto (REEMPLAZA valores):
═════════════════════════════════════════════
DATABASE_URL=postgresql://comerciales:PASSWORD_SEGURO@localhost:5432/comerciales_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=TU_SECRET_KEY_ALEATORIO_64_CHARS
ENVIRONMENT=production
BSALE_API_KEY=TU_BSALE_API_KEY
BSALE_SECRET=TU_BSALE_SECRET
LOG_LEVEL=INFO
═════════════════════════════════════════════

# Guardar: Ctrl+O, Enter, Ctrl+X
```

### 4.4 Ejecutar migraciones Alembic
```bash
source venv/bin/activate
cd /home/app/comerciales-backend

# Ejecutar migrations
alembic upgrade head

# Verificar (conectar a BD)
psql -U comerciales -d comerciales_db -c "\dt"
# Debería listar tablas
```

### 4.5 Test: Ejecutar FastAPI localmente
```bash
source venv/bin/activate
cd /home/app/comerciales-backend

# Iniciar en background
uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# Esperar 3 segundos
sleep 3

# Probar endpoint
curl http://127.0.0.1:8000/api/v1/health
# Debería responder: {"status":"ok"}

# Matar el proceso
pkill -f uvicorn
```

---

## FASE 5: CONFIGURACIÓN DE SUPERVISOR (15 min)

### 5.1 Crear archivo config de Supervisor
```bash
sudo nano /etc/supervisor/conf.d/comerciales.conf

# Pegar esto:
═════════════════════════════════════════════
[program:comerciales-api]
command=/home/app/comerciales-backend/venv/bin/gunicorn \
    -w 4 \
    -b 127.0.0.1:8000 \
    -k uvicorn.workers.UvicornWorker \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    app.main:app

directory=/home/app/comerciales-backend
user=app
environment=PATH="/home/app/comerciales-backend/venv/bin",HOME="/home/app"
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/comerciales/api.log
stderr_logfile=/var/log/comerciales/api-error.log

[program:redis-server]
command=/usr/bin/redis-server /etc/redis/redis.conf
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/comerciales/redis.log

[program:postgresql]
command=/bin/sh -c "exec /usr/lib/postgresql/14/bin/postgres -D /var/lib/postgresql/14/main -c config_file=/etc/postgresql/14/main/postgresql.conf"
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/comerciales/postgresql.log
═════════════════════════════════════════════

# Guardar: Ctrl+O, Enter, Ctrl+X
```

### 5.2 Crear directorio de logs
```bash
sudo mkdir -p /var/log/comerciales
sudo chown -R app:app /var/log/comerciales
sudo chmod 755 /var/log/comerciales
```

### 5.3 Recargar Supervisor
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status

# Debería mostrar los procesos
```

### 5.4 Iniciar servicios
```bash
sudo supervisorctl start comerciales-api
sudo supervisorctl start redis-server

# Esperar 3 segundos
sleep 3

# Verificar
sudo supervisorctl status
# comerciales-api y redis-server deberían estar RUNNING
```

---

## FASE 6: CONFIGURACIÓN NGINX (20 min)

### 6.1 Crear configuración Nginx
```bash
sudo nano /etc/nginx/sites-available/comerciales

# Pegar esto (REEMPLAZA tudominio.cl):
═════════════════════════════════════════════
upstream api_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name tudominio.cl www.tudominio.cl;
    client_max_body_size 20M;

    # Redirect HTTP to HTTPS (cuando tengas SSL)
    # return 301 https://$server_name$request_uri;

    # Frontend estático
    location / {
        root /var/www/comerciales;
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public, immutable";
    }

    # API backend
    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "ok\n";
        add_header Content-Type text/plain;
    }

    # Logs
    access_log /var/log/nginx/comerciales-access.log;
    error_log /var/log/nginx/comerciales-error.log;
}
═════════════════════════════════════════════

# Guardar: Ctrl+O, Enter, Ctrl+X
```

### 6.2 Habilitar sitio
```bash
sudo ln -s /etc/nginx/sites-available/comerciales /etc/nginx/sites-enabled/

# Eliminar default
sudo rm /etc/nginx/sites-enabled/default

# Test configuración
sudo nginx -t
# Debería responder: ok
```

### 6.3 Reiniciar Nginx
```bash
sudo systemctl restart nginx

# Verificar
curl http://localhost/health
# Debería responder: ok
```

---

## FASE 7: FRONTEND BUILD & DEPLOY (15 min)

### 7.1 Clone repositorio frontend
```bash
cd /home/app
# Asumes tienes repo frontend en GitHub
git clone https://github.com/TuOrg/comerciales-frontend.git
cd comerciales-frontend

# Instalar dependencias
npm install

# Build
npm run build
# Crea carpeta 'dist'
```

### 7.2 Copiar a directorio Nginx
```bash
# Crear directorio
sudo mkdir -p /var/www/comerciales

# Copiar archivos
sudo cp -r /home/app/comerciales-frontend/dist/* /var/www/comerciales/

# Permisos
sudo chown -R www-data:www-data /var/www/comerciales
sudo chmod -R 755 /var/www/comerciales
```

### 7.3 Verificar acceso
```bash
curl http://localhost/
# Debería mostrar contenido HTML del frontend
```

---

## FASE 8: SSL CON CLOUDFLARE (5 min)

### 8.1 Configurar SSL en Cloudflare
1. Ve a https://dash.cloudflare.com
2. Selecciona tu dominio
3. "SSL/TLS" → "Overview"
4. Cambiar a "Full" o "Full (strict)"
5. "Edge Certificates" → "Always Use HTTPS" = ON

### 8.2 Update Nginx a HTTPS (opcional ahora)
Si quieres habilitar HTTPS directo en Nginx (Cloudflare hace la encriptación):
```bash
sudo nano /etc/nginx/sites-available/comerciales

# Cambiar:
# listen 80;
# Por:
listen 443 ssl http2;
listen [::]:443 ssl http2;

# Agregar al final del bloque server:
ssl_certificate /etc/ssl/certs/cloudflare.crt;
ssl_certificate_key /etc/ssl/private/cloudflare.key;

# (Cloudflare no necesita cert local, pero si quieres strict mode, pedir cert a Cloudflare)
```

Por ahora, **Cloudflare maneja HTTPS automáticamente** desde su red.

---

## FASE 9: MONITOREO Y BACKUPS (15 min)

### 9.1 Crear script de backup
```bash
sudo nano /home/app/scripts/backup.sh

# Pegar esto:
═════════════════════════════════════════════
#!/bin/bash

BACKUP_DIR="/var/lib/postgresql/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="comerciales_db_${TIMESTAMP}.sql.gz"

# Crear backup
sudo -u postgres pg_dump comerciales_db | gzip > "$BACKUP_DIR/$BACKUP_FILE"

# Mantener últimos 7 días
find "$BACKUP_DIR" -name "comerciales_db_*.sql.gz" -mtime +7 -delete

echo "Backup completado: $BACKUP_FILE"
═════════════════════════════════════════════

# Guardar: Ctrl+O, Enter, Ctrl+X
```

### 9.2 Agregar cron job (backup diario)
```bash
sudo crontab -e

# Agregar esta línea (backup a las 2:00 AM):
0 2 * * * /home/app/scripts/backup.sh >> /var/log/comerciales/backup.log 2>&1
```

### 9.3 Health check simple
```bash
# Verificar servicios
curl http://localhost/health
curl -s http://127.0.0.1:8000/api/v1/health | jq .

# Verificar BD
psql -U comerciales -d comerciales_db -c "SELECT 1;"

# Verificar Redis
redis-cli ping
```

---

## ✅ VERIFICACIÓN FINAL

### Tests de conectividad
```bash
# 1. Frontend carga
curl -s http://localhost/ | head -20

# 2. API responde
curl -s http://localhost/api/v1/health | jq .

# 3. BD conecta
psql -U comerciales -d comerciales_db -c "SELECT NOW();"

# 4. Redis responde
redis-cli PING

# 5. Logs se generan
tail -10 /var/log/comerciales/api.log
```

### Monitoreo de procesos
```bash
# Ver procesos activos
sudo supervisorctl status

# Ver logs en tiempo real
tail -f /var/log/comerciales/api.log

# Usar top para ver uso de recursos
top -b -n 1 | head -20
```

---

## 📋 CHECKLIST COMPLETADO

- [ ] SSH configurado
- [ ] Firewall habilitado
- [ ] PostgreSQL instalado y BD creada
- [ ] Redis instalado y corriendo
- [ ] Nginx instalado
- [ ] Backend clonado y venv creado
- [ ] Migraciones ejecutadas
- [ ] Supervisor configurado
- [ ] Frontend clonado y buildeado
- [ ] Archivos estáticos en /var/www/comerciales
- [ ] Nginx proxy configurado
- [ ] Cloudflare SSL activado
- [ ] Backups automatizados con cron
- [ ] Health check respondiendo
- [ ] Logs siendo generados

---

## 🚀 PRÓXIMOS PASOS

1. **DEPLOYMENT.md** → Procedimiento de deploy (cambios en código)
2. **MULTI_TENANT_ARCHITECTURE.md** → Estructura de BD para múltiples locales
3. **TROUBLESHOOTING.md** → Si algo no funciona

---

**Duración total:** ~2-3 horas  
**Costo:** Incluido en $33.60 USD/mes  
**Próximo:** Ver DEPLOYMENT.md
