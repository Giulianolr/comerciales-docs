#!/bin/bash

###############################################################################
# setup-e2e.sh
# Script para levantar el entorno E2E local:
# - PostgreSQL (puerto 5432)
# - Redis (puerto 6379)
# - Popular la BD con datos de prueba
###############################################################################

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/comerciales-backend"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  E2E Local Setup - Sistema de Locales${NC}"
echo -e "${BLUE}=========================================${NC}\n"

# 1. Verificar que Docker está disponible
echo -e "${YELLOW}1️⃣  Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado. Instálalo desde https://www.docker.com/products/docker-desktop${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker disponible${NC}\n"

# 2. Levantar contenedores
echo -e "${YELLOW}2️⃣  Levantando PostgreSQL y Redis...${NC}"
cd "$PROJECT_ROOT"
docker compose up -d
echo -e "${GREEN}✅ Contenedores levantados${NC}\n"

# 3. Esperar a que PostgreSQL esté listo
echo -e "${YELLOW}3️⃣  Esperando a que PostgreSQL esté listo...${NC}"
max_attempts=30
attempt=0
until docker exec comerciales-postgres pg_isready -U comerciales -d comerciales > /dev/null 2>&1 || [ $attempt -eq $max_attempts ]; do
    attempt=$((attempt + 1))
    echo "  Intento $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}❌ PostgreSQL no respondió a tiempo${NC}"
    exit 1
fi
echo -e "${GREEN}✅ PostgreSQL listo${NC}\n"

# 4. Instalar dependencias del backend si es necesario
echo -e "${YELLOW}4️⃣  Verificando dependencias del backend...${NC}"
cd "$BACKEND_DIR"
if ! python3 -c "import alembic" 2>/dev/null; then
    echo "  Instalando dependencias..."
    python3 -m pip install -q -e .
fi
echo -e "${GREEN}✅ Dependencias verificadas${NC}\n"

# 5. Ejecutar seed
echo -e "${YELLOW}5️⃣  Poblando la base de datos...${NC}"
cd "$BACKEND_DIR"
python3 -m scripts.seed_db
echo -e "${GREEN}✅ Base de datos poblada${NC}\n"

# 6. Resumen final
echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}🎉 Setup completado!${NC}"
echo -e "${BLUE}=========================================${NC}\n"
echo -e "📊 ${YELLOW}Servicios levantados:${NC}"
echo "  • PostgreSQL en localhost:5432"
echo "  • Redis en localhost:6379"
echo ""
echo -e "📝 ${YELLOW}Credenciales:${NC}"
echo "  BD: comerciales / comerciales2026"
echo "  Admin: admin@omsai.cl / admin123"
echo "  Cajero: cajero@omsai.cl / 123"
echo ""
echo -e "🔗 ${YELLOW}Comandos útiles:${NC}"
echo "  • Ver logs:     docker compose logs -f"
echo "  • Parar:        docker compose down"
echo "  • Conectar BD:  psql -h localhost -U comerciales -d comerciales"
echo ""
