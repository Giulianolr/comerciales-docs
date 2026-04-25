#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Validating Barcode Endpoint ===${NC}"

# Configuration
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="comerciales"
DB_USER="comerciales"
DB_PASSWORD="comerciales2026"
API_URL="http://localhost:8000"
BARCODE="7891234567890"
STORE_ID="11111111-1111-1111-1111-111111111111"

# Step 1: Check if PostgreSQL is accessible
echo -e "${BLUE}Step 1: Checking PostgreSQL connection...${NC}"
if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" &>/dev/null; then
  echo -e "${RED}✗ PostgreSQL not accessible at $DB_HOST:$DB_PORT${NC}"
  exit 1
fi
echo -e "${GREEN}✓ PostgreSQL is running${NC}"

# Step 2: Check if API is running
echo -e "${BLUE}Step 2: Checking API availability...${NC}"
if ! curl -s "$API_URL/api/v1/health" &>/dev/null; then
  echo -e "${RED}✗ API not accessible at $API_URL${NC}"
  echo "   Make sure the backend is running: cd comerciales-backend && make run"
  exit 1
fi
echo -e "${GREEN}✓ API is running${NC}"

# Step 3: Get a JWT token via login
echo -e "${BLUE}Step 3: Authenticating to backend...${NC}"
TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@comerciales.cl",
    "password": "admin123"
  }')

TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token' 2>/dev/null)
if [ -z "$TOKEN" ] || [ "$TOKEN" == "null" ]; then
  echo -e "${RED}✗ Failed to get JWT token${NC}"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi
echo -e "${GREEN}✓ Authenticated (token: ${TOKEN:0:20}...)${NC}"

# Step 4: Insert product into PostgreSQL
echo -e "${BLUE}Step 4: Inserting test product into database...${NC}"
PRODUCT_ID="55555555-5555-5555-5555-555555555555"
CATEGORY_ID="44444444-4444-4444-4444-444444444444"

# Ensure category exists
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  -c "INSERT INTO categories (id, store_id, name, description)
      VALUES ('$CATEGORY_ID', '$STORE_ID', 'Test Category', 'For testing')
      ON CONFLICT DO NOTHING;" 2>/dev/null || true

# Insert the product
INSERT_RESULT=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
  -c "INSERT INTO products (id, store_id, category_id, barcode, name, description, price, unit, stock_quantity, is_active)
      VALUES ('$PRODUCT_ID', '$STORE_ID', '$CATEGORY_ID', '$BARCODE', 'Test Product', 'Product for barcode validation', 9999.00, 'unit', 100, true)
      ON CONFLICT (store_id, barcode) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
      RETURNING id;" 2>&1)

if echo "$INSERT_RESULT" | grep -q "ERROR"; then
  echo -e "${RED}✗ Failed to insert product${NC}"
  echo "Error: $INSERT_RESULT"
  exit 1
fi
echo -e "${GREEN}✓ Product inserted (ID: $PRODUCT_ID)${NC}"

# Step 5: Query the product via API endpoint
echo -e "${BLUE}Step 5: Calling GET /api/v1/products/barcode/$BARCODE...${NC}"
API_RESPONSE=$(curl -s -X GET "$API_URL/api/v1/products/barcode/$BARCODE" \
  -H "X-Store-ID: $STORE_ID" \
  -H "Authorization: Bearer $TOKEN")

if echo "$API_RESPONSE" | jq empty 2>/dev/null; then
  RESPONSE_BARCODE=$(echo "$API_RESPONSE" | jq -r '.barcode' 2>/dev/null)
  RESPONSE_NAME=$(echo "$API_RESPONSE" | jq -r '.name' 2>/dev/null)

  if [ "$RESPONSE_BARCODE" == "$BARCODE" ]; then
    echo -e "${GREEN}✓ Endpoint returned product correctly${NC}"
    echo -e "  Barcode: $RESPONSE_BARCODE"
    echo -e "  Name: $RESPONSE_NAME"
    echo ""
    echo -e "${GREEN}=== SUCCESS: Barcode endpoint is working ===${NC}"
    exit 0
  else
    echo -e "${RED}✗ Barcode mismatch in response${NC}"
    echo "Response: $API_RESPONSE"
    exit 1
  fi
else
  echo -e "${RED}✗ Invalid JSON response from API${NC}"
  echo "Response: $API_RESPONSE"
  exit 1
fi
