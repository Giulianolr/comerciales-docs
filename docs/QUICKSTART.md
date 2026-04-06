# QUICKSTART PARA ALLAN & JONATHAN
## Cómo empezar con el proyecto en Sprint 0

**Para:** Allan (Backend), Jonathan (Frontend)  
**Tiempo:** ~30 minutos setup  
**Fecha:** 6 de abril de 2026  

---

## 📦 PASO 1: CLONAR REPOSITORIOS

```bash
# Crear carpeta de trabajo
mkdir -p ~/dev/comerciales
cd ~/dev/comerciales

# Clonar los 3 repos
git clone https://github.com/Giulianolr/comerciales-backend.git
git clone https://github.com/Giulianolr/comerciales-frontend.git
git clone https://github.com/Giulianolr/comerciales-infra.git

# Verificar
ls -la
# Deberías ver 3 carpetas
```

---

## 🔧 PARA ALLAN (BACKEND)

### Paso 1: Setup Ambiente Python

```bash
cd comerciales-backend

# Crear virtual environment
python3.11 -m venv venv

# Activar
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic alembic redis python-dotenv python-jose passlib

# Verificar
python --version  # Python 3.11+
pip list | grep fastapi  # Debería aparecer
```

### Paso 2: Configurar .env

```bash
# Crear archivo .env local
cat > .env << EOF
# Database (desarrollo local)
DATABASE_URL=sqlite:///./test.db

# Redis
REDIS_URL=redis://localhost:6379

# SII (por ahora dummy)
SII_API_KEY=dummy_key_dev
SII_PROVIDER=bsale

# Security
SECRET_KEY=your-secret-key-here-change-in-prod
ALGORITHM=HS256

# Environment
ENVIRONMENT=development
EOF
```

### Paso 3: Crear Estructura Base

```bash
# Crear folders
mkdir -p app/models
mkdir -p app/routes
mkdir -p app/services
mkdir -p app/schemas
mkdir -p migrations

# Crear app/main.py inicial
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Comerciales Inventario API",
    description="Sistema de inventario dinámico",
    version="0.1"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API Funcionando ✅"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
```

### Paso 4: Run Servidor Local

```bash
# Activar venv (si no está)
source venv/bin/activate

# Correr servidor
python -m uvicorn app.main:app --reload

# Output esperado:
# Uvicorn running on http://127.0.0.1:8000
# Press CTRL+C to quit

# Test en otra terminal
curl http://localhost:8000/
# {"message": "API Funcionando ✅"}
```

### Paso 5: Setup Alembic (Migraciones)

```bash
# Inicializar Alembic
alembic init migrations

# Ver help
alembic --help

# Crear primera migración (vacía, para template)
alembic revision -m "initial_schema"

# Ver migraciones creadas
ls migrations/versions/
```

---

## 🎨 PARA JONATHAN (FRONTEND)

### Paso 1: Setup Node/npm

```bash
cd comerciales-frontend

# Verificar Node
node --version  # v18+ recomendado
npm --version   # v9+

# Si necesitas actualizar
npm install -g npm@latest
```

### Paso 2: Instalar Dependencias

```bash
# Instalar todo
npm install

# Debería tomar 2-3 minutos
# Verificar package.json se actualiza
```

### Paso 3: Instalar Librerías Necesarias

```bash
# Vue 3 + TypeScript + Tooling
npm install vue@3 typescript

# State management
npm install pinia

# HTTP client
npm install axios

# UI Framework
npm install tailwindcss postcss autoprefixer
npm install -D shadcn-vue

# Real-time
npm install socket.io-client

# Forms & validation
npm install vee-validate yup

# Charts (para dashboards)
npm install chart.js vue-chartjs
```

### Paso 4: Crear Estructura Base

```bash
# Crear carpeta src si no existe
mkdir -p src/components
mkdir -p src/pages
mkdir -p src/stores
mkdir -p src/api
mkdir -p src/types

# Crear App.vue básico
cat > src/App.vue << 'EOF'
<template>
  <div id="app" class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow">
      <div class="px-4 py-2">
        <h1 class="text-2xl font-bold">Comerciales Inventario</h1>
      </div>
    </nav>
    <main class="container mx-auto p-4">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

onMounted(() => {
  console.log('App iniciada ✅')
})
</script>
EOF
```

### Paso 5: Run Dev Server

```bash
# Development server
npm run dev

# Output esperado:
# VITE v4.x.x ready in xxx ms
# ➜ Local: http://localhost:5173/
# ➜ press h to show help

# Abre en browser
# http://localhost:5173/
```

---

## 📝 WORKFLOW GIT

### Crear Feature Branch

```bash
# Asegúrate estar en develop
git checkout develop
git pull origin develop

# Crear branch para tu feature
git checkout -b feature/tu-feature-name

# Ejemplos:
# feature/api-products
# feature/inventory-ui
# feature/websocket-sync
```

### Hacer Commit

```bash
# Ver cambios
git status

# Agregar cambios
git add .

# Commit
git commit -m "feat: descripción de cambios"

# Ejemplos:
# "feat: add GET /api/products endpoint"
# "style: format Vue component"
# "fix: inventory calculation bug"
# "docs: add API documentation"
```

### Push & PR

```bash
# Push a GitHub
git push -u origin feature/tu-feature-name

# Crear PR (vía GitHub web o CLI)
gh pr create --title "Add products endpoint" --body "Brief description"

# Ver PRs
gh pr list
```

---

## 🏗️ ESTRUCTURA DE CARPETAS (Final)

```
comerciales-backend/
├── app/
│   ├── main.py
│   ├── models/              # SQLAlchemy models
│   │   ├── product.py
│   │   ├── station.py
│   │   ├── order.py
│   │   └── transaction.py
│   ├── routes/              # FastAPI routers
│   │   ├── products.py
│   │   ├── orders.py
│   │   ├── transactions.py
│   │   └── auth.py
│   ├── services/            # Business logic
│   │   ├── product_service.py
│   │   ├── inventory_service.py
│   │   └── sii_service.py
│   ├── schemas/             # Pydantic models
│   │   ├── product.py
│   │   ├── order.py
│   │   └── transaction.py
│   └── core/                # Config, auth, constants
│       ├── config.py
│       ├── security.py
│       └── constants.py
├── migrations/              # Alembic migrations
├── tests/                   # Pytest tests
├── .env                     # Local config
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md

comerciales-frontend/
├── src/
│   ├── App.vue
│   ├── main.ts
│   ├── router.ts           # Vue Router
│   ├── components/         # Componentes reutilizables
│   │   ├── Navbar.vue
│   │   ├── Sidebar.vue
│   │   └── ProductCard.vue
│   ├── pages/              # Pages
│   │   ├── Operador.vue
│   │   ├── Cajero.vue
│   │   └── Gerente.vue
│   ├── stores/             # Pinia stores
│   │   ├── products.ts
│   │   ├── orders.ts
│   │   └── auth.ts
│   ├── api/                # API calls
│   │   ├── products.ts
│   │   ├── orders.ts
│   │   └── client.ts
│   ├── types/              # TypeScript types
│   │   ├── product.ts
│   │   ├── order.ts
│   │   └── index.ts
│   └── styles/             # CSS/Tailwind
├── public/
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── .env.local
├── package.json
└── README.md

comerciales-infra/
├── gcp/                    # GCP configs
│   ├── main.tf            # GCP Project, services
│   ├── cloud-run.tf       # Cloud Run config
│   ├── cloud-sql.tf       # Database config
│   └── redis.tf           # Redis config
├── vps/                    # VPS scripts
│   ├── setup.sh           # Initial VPS setup
│   ├── deploy.sh          # Deploy script
│   ├── backup.sh          # Backup script
│   └── nginx.conf         # Nginx config
├── ci-cd/                  # GitHub Actions
│   └── .github/
│       └── workflows/
│           ├── test.yml   # Run tests
│           └── deploy.yml # Deploy to GCP/VPS
└── README.md
```

---

## 🧪 TESTING INICIAL

### Backend Test

```bash
# En comerciales-backend/
source venv/bin/activate

# Crear test básico
mkdir -p tests
cat > tests/test_main.py << 'EOF'
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "API Funcionando ✅"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
EOF

# Instalar pytest
pip install pytest

# Run tests
pytest tests/
# PASSED tests/test_main.py::test_read_root ✓
# PASSED tests/test_main.py::test_health ✓
```

### Frontend Test

```bash
# En comerciales-frontend/

# Crear test básico
mkdir -p __tests__
cat > __tests__/App.test.ts << 'EOF'
import { describe, it, expect } from 'vitest'
import App from '../src/App.vue'

describe('App.vue', () => {
  it('renders properly', () => {
    expect(App).toBeDefined()
  })
})
EOF

# Instalar vitest
npm install -D vitest

# Run tests
npm run test
# ✓ __tests__/App.test.ts (1)
```

---

## 🚀 CHECKLIST PARA EMPEZAR

### Allan (Backend)
- [ ] Cloné comerciales-backend
- [ ] Creé venv y instalé dependencias
- [ ] Corrí `python -m uvicorn app.main:app --reload`
- [ ] Accedí a http://localhost:8000 y veo respuesta
- [ ] Creé `.env` local
- [ ] Creé estructura de carpetas
- [ ] Corrí tests básicos

### Jonathan (Frontend)
- [ ] Cloné comerciales-frontend
- [ ] Instalé dependencias con `npm install`
- [ ] Corrí `npm run dev`
- [ ] Accedí a http://localhost:5173
- [ ] Creé estructura de carpetas
- [ ] Corrí tests básicos

### Ambos
- [ ] Creé feature branch (`feature/sprint0-setup`)
- [ ] Hice primer commit
- [ ] Hice push a GitHub
- [ ] Creé PR

---

## 📞 PRÓXIMOS PASOS

1. **Hoy (6 abril):** Setup local completado
2. **Martes (9 abril):** Reunión hardware
3. **Miércoles (10 abril):** GCP setup confirmado
4. **Sprint 0 (14-18 abril):**
   - [ ] Allan: Cloud Run + Cloud SQL funcionando
   - [ ] Jonathan: Vue 3 básico en vivo
   - [ ] Primeros endpoints funcionando
   - [ ] Primer deploy a GCP

---

## 📚 DOCUMENTACIÓN ADICIONAL

- **SETUP_GCP_VSCODE.md** — Cómo vincular GCP
- **INFRAESTRUCTURA_ECONOMICA.md** — Setup VPS
- **ESTRATEGIA_HIBRIDA.md** — Plan de migración
- **ARQUITECTURA.md** — Decisiones técnicas
- **MODELO_DATOS.md** — Schema DB

---

**¡Bienvenidos al proyecto! 🚀 Si tienen dudas, pregunten.**

Versión: 0.1 | Última actualización: 6 de abril 2026
