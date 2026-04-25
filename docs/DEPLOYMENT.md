# DEPLOYMENT & CI/CD
## Procedimientos para deploy, rollback y actualización de código

**Para:** Allan (DevOps) + Jonathan (Frontend)  
**Tiempo:** Backend ~5 min, Frontend ~3 min  
**Downtime:** ~1 minuto (configurable)

---

## 🚀 DEPLOY BACKEND (FastAPI)

### Opción A: Manual (Recomendado inicialmente)

#### Paso 1: SSH al servidor
```bash
ssh -i ~/.ssh/hetzner-key.pem app@[TU_IP_VPS]
cd /home/app/comerciales-backend
```

#### Paso 2: Actualizar código
```bash
# Traer cambios del repo
git fetch origin
git checkout main  # O la rama que uses
git pull origin main

# Ver qué cambió
git log --oneline -5
```

#### Paso 3: Instalar dependencias (si hay nuevas)
```bash
source venv/bin/activate
pip install -r requirements.txt
pip list --outdated
```

#### Paso 4: Ejecutar migraciones (si hay)
```bash
# Ver migraciones pendientes
alembic current
alembic upgrade head

# Verificar BD
psql -U comerciales -d comerciales_db -c "\dt"
```

#### Paso 5: Gracias, ahora reinicia servicio
```bash
# Opción 1: Via supervisor (RECOMENDADO)
sudo supervisorctl restart comerciales-api

# Opción 2: Manual
pkill -f gunicorn
source venv/bin/activate
gunicorn -w 4 -b 127.0.0.1:8000 app.main:app &

# Esperar 3 segundos
sleep 3

# Verificar que esté corriendo
curl http://localhost:8000/api/v1/health
```

#### Paso 6: Verificar en navegador
```
https://comerciales.cl/api/v1/health
# Debería responder {"status":"ok"}
```

---

### Opción B: Con GitHub Actions (Automático)

#### Configurar CI/CD con GitHub Actions
```bash
# Crear archivo: .github/workflows/deploy.yml

name: Deploy to VPS

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_IP }}
          username: app
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /home/app/comerciales-backend
            git fetch origin
            git checkout main
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            alembic upgrade head
            sudo supervisorctl restart comerciales-api
            echo "✅ Deploy completado"
```

#### Configurar secrets en GitHub
1. Ve a repo → Settings → Secrets and variables → Actions
2. Agregar:
   - `VPS_IP`: Tu IP Hetzner (1.2.3.4)
   - `SSH_PRIVATE_KEY`: Tu clave privada SSH (contenido del `.pem`)

#### Deploy automático
```
Ahora, cada push a main:
1. GitHub Actions detecta cambios
2. SSH a VPS
3. Actualiza código + BD + reinicia servicio
4. Listo

(Sin hacer nada manual)
```

---

## 🎨 DEPLOY FRONTEND (Vue 3)

### Opción A: Manual

#### Paso 1: SSH al servidor + carpeta frontend
```bash
ssh -i ~/.ssh/hetzner-key.pem app@[TU_IP_VPS]
cd /home/app/comerciales-frontend
```

#### Paso 2: Actualizar código
```bash
git fetch origin
git checkout main
git pull origin main
```

#### Paso 3: Build
```bash
npm install --legacy-peer-deps  # Si hay warnings
npm run build
# Crea/actualiza carpeta 'dist/'
```

#### Paso 4: Copiar a Nginx
```bash
sudo cp -r dist/* /var/www/comerciales/
```

#### Paso 5: Verificar en navegador
```
https://comerciales.cl/
# Debería mostrar la nueva versión
```

---

### Opción B: Con GitHub Actions (Automático)

```yaml
name: Deploy Frontend

on:
  push:
    branches:
      - main
    paths:
      - 'frontend-code/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Use Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: cd frontend-code && npm install --legacy-peer-deps
      
      - name: Build
        run: cd frontend-code && npm run build
      
      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_IP }}
          username: app
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /home/app/comerciales-frontend
            git pull origin main
            npm install --legacy-peer-deps
            npm run build
            sudo cp -r dist/* /var/www/comerciales/
            echo "✅ Frontend deploy completado"
```

---

## 🔄 ROLLBACK (REVERTIR CAMBIOS)

### Rollback Manual (Rápido)
```bash
cd /home/app/comerciales-backend

# Ver histórico de commits
git log --oneline -10

# Revertir a commit anterior
git checkout <hash_del_commit_anterior>
git reset --hard HEAD

# Reiniciar servicio
sudo supervisorctl restart comerciales-api

# Verificar
curl http://localhost:8000/api/v1/health
```

### Rollback Automático (Si deploy falla)
```bash
# Script: /home/app/scripts/rollback.sh
#!/bin/bash

cd /home/app/comerciales-backend

# Guardar commit fallido
FAILED_COMMIT=$(git log -1 --oneline)
echo "Deploy fallido en: $FAILED_COMMIT" >> /var/log/deploy-log.txt

# Revertir a última versión stable
git revert HEAD --no-edit
git push origin main

# Reiniciar
sudo supervisorctl restart comerciales-api

# Alerta
echo "⚠️ ROLLBACK EJECUTADO - Revisar logs" | \
  mail -s "Deploy Fallido - Rollback" allan@example.com
```

---

## 📊 VERSIONING & CONTROL DE CAMBIOS

### Commits semánticos
```
Backend commits:
feat: agregar endpoint de reportes
fix: corregir bug en cálculo de inventario
refactor: mejorar queries de BD
docs: actualizar documentación de API

Frontend commits:
feat: agregar vista de reportes diarios
fix: corregir responsive en mobile
style: actualizar colores según branding
```

### Versionamiento (semantic versioning)
```bash
# Tag para releases importantes
git tag v1.0.0 -m "Release producción inicial"
git push origin v1.0.0

# Ver tags
git tag -l
```

---

## ✅ CHECKLIST PRE-DEPLOY

### Backend
- [ ] Código está en rama correcta (`main`)
- [ ] Tests pasan (si hay): `pytest tests/`
- [ ] Linting pasa (si hay): `flake8 app/`
- [ ] Migraciones están creadas (si hay cambios de BD)
- [ ] `.env` en VPS tiene las variables correctas
- [ ] No hay secretos en el código (usa .env)
- [ ] Variables de entorno ENVIRONMENT=production

### Frontend
- [ ] Build local funciona: `npm run build`
- [ ] Sin errores en consola
- [ ] URLs de API apuntan a producción
- [ ] Variables de entorno correctas (Cloudflare, etc)
- [ ] Build es estático (sin dependencias de servidor)

### VPS
- [ ] Espacio en disco: `df -h` (>10GB libre)
- [ ] BD puede respaldar: `sudo du -sh /var/lib/postgresql`
- [ ] Nginx está corriendo: `sudo systemctl status nginx`
- [ ] Supervisor está corriendo: `sudo supervisorctl status`

---

## 🔍 MONITOREO POST-DEPLOY

### Verificaciones inmediatas (primeros 5 min)
```bash
# 1. API respondiendo
curl https://comerciales.cl/api/v1/health

# 2. Frontend carga
curl -s https://comerciales.cl/ | head -20

# 3. Login funciona
curl -X POST https://comerciales.cl/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# 4. Logs sin errores
tail -20 /var/log/comerciales/api.log
tail -20 /var/log/nginx/comerciales-error.log

# 5. Recursos del servidor
top -b -n 1 | head -10
```

### Health checks automáticos (opcional)
```bash
# Script: /home/app/scripts/health-check.sh
#!/bin/bash

URL="https://comerciales.cl/api/v1/health"
RESPONSE=$(curl -s -w "%{http_code}" "$URL")
HTTP_CODE="${RESPONSE: -3}"

if [ "$HTTP_CODE" != "200" ]; then
  # Falló, enviar alerta
  echo "ALERTA: API no responde (HTTP $HTTP_CODE)" | \
    mail -s "⚠️ API DOWN" allan@example.com
  
  # Intentar reiniciar
  sudo supervisorctl restart comerciales-api
  sleep 5
  
  # Verificar nuevamente
  curl -s "$URL" > /dev/null
fi
```

### Agregar a cron (cada 5 minutos)
```bash
sudo crontab -e

# Agregar:
*/5 * * * * /home/app/scripts/health-check.sh >> /var/log/health-check.log 2>&1
```

---

## 🚨 ROLLBACK RÁPIDO SI ALGO FALLA

```bash
# Si API no responde después de deploy
cd /home/app/comerciales-backend

# Ver últimos commits
git log --oneline -3

# Revertir al anterior
git checkout main~1

# Reiniciar
sudo supervisorctl restart comerciales-api

# Verificar
curl http://localhost:8000/api/v1/health

# Luego investigar qué fue el problema
git diff main main~1
```

---

## 📅 DEPLOYMENT SCHEDULE

### Ventana de deploy recomendada
```
MEJOR: Martes a Jueves, 3:00-5:00 PM
(Después de cierre de local, antes de cena)

EVITAR: 
- Viernes (si falla, está sin IT el fin de semana)
- Fines de semana (clientes usando)
- Días pico de ventas
```

### Comunicación pre-deploy
```
24h antes:
"Mañana a las 3 PM haremos actualización. 
Downtime estimado: 1-2 minutos"

Enviar a: gerentes + admin locales
```

---

## 📋 TEMPLATE: DEPLOYMENT LOG

```bash
# Guardar en: /var/log/deployments.log

═════════════════════════════════════════════════
DEPLOYMENT LOG - 2026-04-20 15:30 UTC
═════════════════════════════════════════════════

COMPONENTE:     Backend
RAMA:           main
COMMIT:         abc1234 (feat: agregar reportes)
EJECUTADO POR:  Allan

PRE-DEPLOY CHECKS:
✅ Tests pasaron (5/5)
✅ BD migrada (v20 → v21)
✅ .env actualizado
✅ Espacio en disco: 25GB libre

DEPLOY:
✅ git pull completado
✅ pip install completado
✅ alembic upgrade completado
✅ supervisorctl restart completado

POST-DEPLOY CHECKS:
✅ API responde (HTTP 200)
✅ Frontend carga
✅ Login funciona
✅ Transacción test completada

DOWNTIME:     45 segundos
STATUS:       ✅ EXITOSO
OBSERVACIONES: Todo normal

═════════════════════════════════════════════════
```

---

## ⚠️ ERRORES COMUNES

### Error: "git pull" rechazado (cambios locales)
```bash
# Problema: Hay cambios sin commit en VPS
git stash  # Guardar cambios temporales
git pull origin main
git stash pop  # Restaurar si es necesario
```

### Error: "pip install" falla
```bash
# Problema: Dependencia no compatible
pip install -r requirements.txt --no-cache-dir --force-reinstall

# Si sigue fallando, ver logs:
tail -100 /tmp/pip_errors.log
```

### Error: "alembic upgrade" falla
```bash
# Ver qué migraciones están
alembic current
alembic branches

# Si una migración no es reversible, investigar:
git log alembic/versions/
```

### Error: "supervisorctl restart" no funciona
```bash
# Verificar proceso está corriendo
ps aux | grep gunicorn

# Si no está, iniciar manual
sudo supervisorctl start comerciales-api

# Si supervisor tiene error:
sudo supervisorctl status
sudo supervisorctl reread
sudo supervisorctl update
```

---

## ✅ CHECKLIST FINAL

Post-deployment (primeros 30 min):

- [ ] API responde HTTP 200
- [ ] Frontend carga sin errores
- [ ] Login funciona
- [ ] Dashboard carga data
- [ ] Transacción de prueba funciona
- [ ] Logs no muestran errores
- [ ] Nginx reverse proxy funciona
- [ ] SSL/HTTPS funciona
- [ ] Backup automático corrió
- [ ] Alertas email sin fallos

---

**Próximos documentos:**
- TROUBLESHOOTING.md (Si algo falla)
- MONITORING.md (Uptime, alertas)
- BACKUP_STRATEGY.md (Recuperación de datos)
