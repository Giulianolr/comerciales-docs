# SETUP GCP + VSCODE PARA CLAUDE CODE
## Vincular Google Cloud Platform a VS Code para desarrollo local

**Versión:** 0.1  
**Fecha:** 6 de abril de 2026  
**Para:** PM (Giuliano), Backend Dev (Allan), Claude Code  
**Objetivo:** Permitir que Claude Code interactúe con GCP por CLI

---

## 📋 REQUISITOS PREVIOS

- ✅ Cuenta GitHub (Giulianolr) — YA TIENES
- ✅ Cuenta Google / Gmail — NECESARIO
- ✅ VSCode instalado en tu Mac — NECESARIO
- ✅ Tarjeta de crédito (para vincular GCP, pero free trial no cobra)
- ⏱️ Tiempo: ~20 minutos

---

## 🔧 PASO 1: INSTALAR GOOGLE CLOUD CLI

### En Mac:

```bash
# Instalar gcloud CLI
brew install google-cloud-sdk

# Verificar instalación
gcloud --version

# Output esperado:
# Google Cloud SDK 476.0.0
# bq 2.0.95
# gsutil 5.28
```

### En Windows (si aplica):

```bash
# Opción 1: Instalar directo
# https://cloud.google.com/sdk/docs/install#windows

# Opción 2: Chocolatey
choco install google-cloud-sdk

# Opción 3: Descargar installer manual
# https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe
```

---

## 🔐 PASO 2: AUTENTICARTE CON GOOGLE

```bash
# Login en Google
gcloud auth login

# Esto abrirá un browser
# 1. Selecciona tu cuenta Google
# 2. Permite acceso
# 3. Vuelve a la terminal
```

**Verificar autenticación:**

```bash
gcloud auth list

# Output esperado:
#            ACTIVE  ACCOUNT
#        *           tu-email@gmail.com
#
# Set the active account in configurations with:
#   $ gcloud config set account tu-email@gmail.com
```

---

## 🆕 PASO 3: CREAR PROYECTO GCP

```bash
# Crear proyecto nuevo
gcloud projects create comerciales-inventario --set-as-default

# Alternativamente (si prefieres nombre más corto):
gcloud projects create comerciales-dev --set-as-default

# Verificar que se creó
gcloud projects list

# Output esperado:
# PROJECT_ID              NAME                   PROJECT_NUMBER
# comerciales-inventario  comerciales-inventario 123456789012
```

---

## 💳 PASO 4: VINCULAR FACTURACIÓN (IMPORTANTE PARA FREE TRIAL)

El free trial de GCP requiere vincular una tarjeta, pero **NO te cobrará nada los primeros 90 días**.

### Opción A: Via Web Console (Más fácil)

```bash
# Abre la consola web
open "https://console.cloud.google.com/welcome?project=comerciales-inventario"

# Sigue estos pasos:
# 1. Click en "Billing" (lado izquierdo)
# 2. Click en "Link a Billing Account"
# 3. Ingresa tu tarjeta
# 4. Confirma
```

### Opción B: Via CLI

```bash
# Ver billing accounts disponibles
gcloud billing accounts list

# Vincular proyecto a billing account
# (Obtén el BILLING_ACCOUNT_ID del comando anterior)
gcloud billing projects link comerciales-inventario \
  --billing-account=BILLING_ACCOUNT_ID
```

---

## 🔑 PASO 5: CREAR CREDENCIALES PARA CLAUDE CODE

### Opción A: Application Default Credentials (RECOMENDADA - FÁCIL)

```bash
# Crear credenciales locales
gcloud auth application-default login

# Abrirá browser de nuevo
# Aprueba acceso
# Esto crea: ~/.config/gcloud/application_default_credentials.json
```

**Verificar credenciales creadas:**

```bash
ls ~/.config/gcloud/application_default_credentials.json

# Deberías ver el archivo
```

### Opción B: Service Account (MÁS SEGURO - COMPLEJO)

```bash
# Crear service account
gcloud iam service-accounts create claude-code \
  --display-name="Claude Code - Automated Deployment"

# Obtener email del service account
SA_EMAIL=$(gcloud iam service-accounts list --filter="displayName:claude-code" --format='value(email)')

# Dar permisos (editor = full access)
gcloud projects add-iam-policy-binding comerciales-inventario \
  --member=serviceAccount:$SA_EMAIL \
  --role=roles/editor

# Crear key JSON
gcloud iam service-accounts keys create ~/gcp-claude-key.json \
  --iam-account=$SA_EMAIL

# Activar credencial
export GOOGLE_APPLICATION_CREDENTIALS=~/gcp-claude-key.json

# Verificar
echo $GOOGLE_APPLICATION_CREDENTIALS
```

---

## ✅ PASO 6: VERIFICAR VINCULACIÓN

Copia y pega esto en terminal para verificar que todo funciona:

```bash
# 1. Verificar credencial activa
gcloud auth list

# 2. Verificar proyecto por defecto
gcloud config list

# 3. Test: Obtener info del proyecto
gcloud projects describe comerciales-inventario

# Output esperado:
# createTime: '2026-04-06T...'
# name: comerciales-inventario
# projectId: comerciales-inventario
# projectNumber: '123456789012'
# state: ACTIVE
```

**Si ves ACTIVE, estás listo ✅**

---

## 🎯 PASO 7: INSTALAR EXTENSIONES VSCODE (OPCIONAL)

Para mejor experiencia en VSCode:

### Cloud Code Extension

```bash
# Instalar extensión oficial de Google
code --install-extension googlecloudtools.cloudcode

# O buscala en VSCode:
# Extensiones → busca "Cloud Code" → instala por Google
```

### Otras extensiones útiles

```bash
# Docker (para trabajar con containers)
code --install-extension ms-azuretools.vscode-docker

# Remote SSH (si usas VPS)
code --install-extension ms-vscode-remote.remote-ssh

# Terraform (para infra)
code --install-extension HashiCorp.terraform
```

---

## 🚀 VERIFICACIÓN FINAL

Ejecuta esto para confirmar que Claude Code puede acceder a GCP:

```bash
# 1. Verificar que gcloud está en PATH
which gcloud

# 2. Verificar versión
gcloud --version

# 3. Listar proyectos
gcloud projects list

# 4. Listar recursos Cloud Run (debería estar vacío)
gcloud run services list --region=us-central1

# 5. Listar Cloud SQL (debería estar vacío)
gcloud sql instances list

# Si todos estos comandos funcionan, ¡estás listo!
```

---

## 📝 VARIABLES DE ENTORNO (OPCIONAL)

Para hacer debugging más fácil, agrega esto a tu `~/.zshrc` o `~/.bash_profile`:

```bash
# Google Cloud
export GOOGLE_PROJECT_ID=comerciales-inventario
export GOOGLE_REGION=us-central1
export GOOGLE_ZONE=us-central1-a

# Cloudinary (si usas)
export CLOUDSDK_PYTHON_SITEPACKAGES=1
```

Después:
```bash
source ~/.zshrc  # o ~/.bash_profile según tu shell
```

---

## ⚠️ TROUBLESHOOTING

### Problema: "gcloud: command not found"

```bash
# Solución: Agregar a PATH
echo 'export PATH="/usr/local/google-cloud-sdk/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Problema: "ERROR: (gcloud.projects.describe) User does not have permission"

```bash
# Solución: Reautenticarte
gcloud auth login

# O si usas service account:
export GOOGLE_APPLICATION_CREDENTIALS=~/gcp-claude-key.json
```

### Problema: "Application Default Credentials not found"

```bash
# Solución: Crear credenciales
gcloud auth application-default login
```

### Problema: "Project not found"

```bash
# Verificar que proyecto existe
gcloud projects list

# Si no lo ves, crear de nuevo
gcloud projects create comerciales-inventario --set-as-default
```

### Problema: "Billing account not linked"

```bash
# Solución: Ir a web console
open "https://console.cloud.google.com/welcome?project=comerciales-inventario"

# Link billing account en la UI
```

---

## 🔄 CONFIGURACIÓN PARA DESARROLLO LOCAL

Una vez tengas todo funcionando, configura VSCode:

### `.vscode/settings.json`

```json
{
  "google.cloudCode.enable": true,
  "google.cloudCode.project": "comerciales-inventario",
  "google.cloudCode.region": "us-central1",
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": true
  }
}
```

---

## ✨ SIGUIENTES PASOS

Una vez hayas completado este setup:

1. ✅ Compartir salida de `gcloud projects describe comerciales-inventario` con Giuliano
2. ✅ Allan comenzará a crear infraestructura en Sprint 0
3. ✅ Claude Code puede desplegar automáticamente

---

## 📞 COMANDOS MÁS USADOS (Para referencia)

```bash
# Ver config actual
gcloud config list

# Cambiar proyecto
gcloud config set project comerciales-inventario

# Listar recursos (una vez creados)
gcloud run services list
gcloud sql instances list
gcloud compute instances list

# Ver logs (una vez deployado)
gcloud app logs read
gcloud functions logs read

# Deploy simple test
gcloud run deploy hello-world \
  --image gcr.io/cloudrun/hello \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

**Versión:** 0.1  
**Última actualización:** 6 de abril 2026  
**Próxima actualización:** Post Sprint 0 (cuando tengas recursos reales en GCP)
