# ESTRATEGIA DE TESTING
## Sistema de Inventario Dinámico - Locales Comerciales Chile

**Para:** Equipo técnico (Allan, Jonathan) + PM  
**Versión:** 0.1-Sprint0  
**Filosofía:** Test-Driven Development (TDD) ESTRICTO — Nada de "testear al final"

---

## 🎯 Principio Core: RED → GREEN → REFACTOR

```
1. RED:     Escribir test que FALLA (funcionalidad no existe)
2. GREEN:   Escribir código mínimo para que test PASE
3. REFACTOR: Mejorar código sin romper test
4. REPEAT:  Siguiente funcionalidad

NUNCA SALTEAR PASO 1. Si saltás, no es TDD.
```

---

## 🔴 Backend Testing (FastAPI + Python)

### Unit Tests con Pytest

**Ubicación:** `comerciales-backend/tests/unit/`

**Estructura:**
```
tests/
├── unit/
│   ├── test_product_service.py
│   ├── test_order_service.py
│   ├── test_transaction_service.py
│   ├── test_inventory_service.py
│   ├── test_auth_service.py
│   └── test_models.py
├── integration/
│   ├── test_products_api.py
│   ├── test_orders_api.py
│   ├── test_transactions_api.py
│   ├── test_boletas_integration.py
│   └── test_websocket_sync.py
├── e2e/
│   └── test_full_sale_flow.py
└── conftest.py  (fixtures globales)
```

**Unit Test Example: ProductService**

```python
# tests/unit/test_product_service.py

import pytest
from app.services.product_service import ProductService
from app.models import Product
from sqlalchemy.orm import Session

@pytest.fixture
def mock_db(mocker):
    """Mock de base de datos"""
    return mocker.MagicMock(spec=Session)

@pytest.fixture
def product_service(mock_db):
    """Servicio con DB mockeada"""
    return ProductService(db=mock_db)

class TestProductService:
    
    def test_get_product_by_barcode_found(self, product_service, mock_db):
        """
        GIVEN: Existe un producto con barcode "123456"
        WHEN: Llamamos get_product_by_barcode("123456")
        THEN: Retorna el producto
        """
        # ARRANGE
        expected_product = Product(
            id="prod-1",
            store_id="store-1",
            barcode="123456",
            name="Tomate",
            price=2.50,
            stock_quantity=50.0
        )
        mock_db.query().filter().first.return_value = expected_product
        
        # ACT
        result = product_service.get_product_by_barcode("123456", "store-1")
        
        # ASSERT
        assert result.id == "prod-1"
        assert result.name == "Tomate"
        assert result.price == 2.50
        
    def test_get_product_by_barcode_not_found(self, product_service, mock_db):
        """
        GIVEN: NO existe un producto con barcode "999999"
        WHEN: Llamamos get_product_by_barcode("999999")
        THEN: Retorna None
        """
        mock_db.query().filter().first.return_value = None
        
        result = product_service.get_product_by_barcode("999999", "store-1")
        
        assert result is None
        
    def test_update_stock_decrements_inventory(self, product_service, mock_db):
        """
        GIVEN: Producto con stock=50
        WHEN: Decrementamos 2 unidades
        THEN: Stock pasa a 48 + se registra movement
        """
        product = Product(
            id="prod-1",
            store_id="store-1",
            stock_quantity=50.0
        )
        
        product_service.decrement_stock(product, 2.0, "sale", "ORD-123")
        
        # ASSERT: stock actualizado
        assert product.stock_quantity == 48.0
        
        # ASSERT: movement registrado (verificar mock fue llamado)
        mock_db.add.assert_called()
        mock_db.commit.assert_called_once()
        
    def test_stock_cannot_go_negative(self, product_service, mock_db):
        """
        GIVEN: Producto con stock=5
        WHEN: Intentamos decrementar 10
        THEN: Lanza exception (stock negativo)
        """
        product = Product(id="prod-1", stock_quantity=5.0)
        
        with pytest.raises(ValueError, match="Insufficient stock"):
            product_service.decrement_stock(product, 10.0, "sale", "ORD-123")
```

**Cobertura Mínima:** 80% en services, 70% en routers

```bash
# Ejecutar tests con cobertura
pytest tests/unit/ --cov=app.services --cov-report=html --cov-fail-under=80
```

---

### Integration Tests con FastAPI TestClient

**Ubicación:** `comerciales-backend/tests/integration/`

```python
# tests/integration/test_products_api.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy.orm import Session
from app.database import get_db

@pytest.fixture
def test_db():
    """DB real de test (SQLite en memoria)"""
    # Setup: crear tablas
    # Yield: test
    # Teardown: limpiar
    pass

@pytest.fixture
def client(test_db):
    """Client HTTP para test"""
    def override_get_db():
        return test_db
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

class TestProductsAPI:
    
    def test_create_product_success(self, client):
        """POST /products crea producto"""
        response = client.post(
            "/api/v1/products",
            json={
                "barcode": "123456",
                "name": "Tomate",
                "price": 2.50,
                "stock": 50,
                "category": "Verduras"
            },
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Tomate"
        assert data["barcode"] == "123456"
        
    def test_create_product_duplicate_barcode_fails(self, client):
        """POST /products falla si barcode duplicado"""
        # Crear primero
        client.post("/api/v1/products", json={"barcode": "123456", ...})
        
        # Intentar duplicar
        response = client.post("/api/v1/products", json={"barcode": "123456", ...})
        
        assert response.status_code == 409  # Conflict
        assert "already exists" in response.json()["detail"]
        
    def test_list_products_filters_by_store(self, client):
        """GET /products solo muestra productos del local logueado"""
        # Crear 2 productos en store1
        # Crear 1 producto en store2
        # Login como store1
        # Verificar que solo ve 2
        
        response = client.get(
            "/api/v1/products",
            headers={"Authorization": "Bearer store1_token"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 2  # RLS en acción
```

---

### E2E: Test Full Sale Flow

**Ubicación:** `comerciales-backend/tests/e2e/test_full_sale_flow.py`

```python
# Scenario: Cliente compra 2kg tomates + 1 pan, paga, boleta se emite

def test_complete_sale_flow(client, test_db):
    """
    E2E: Desde escaneo en balanza → QR → caja → boleta SII
    """
    
    # SETUP: Crear store, productos, usuarios
    store = create_test_store()
    operador = create_test_user(store_id=store.id, role="OPERADOR")
    cajero = create_test_user(store_id=store.id, role="CAJERO")
    
    tomate = create_test_product(
        store_id=store.id,
        barcode="123456",
        name="Tomate",
        price=2.50,
        stock=50.0
    )
    pan = create_test_product(
        store_id=store.id,
        barcode="789012",
        name="Pan",
        price=3.50,
        stock=20.0
    )
    
    # 1. OPERADOR EN BALANZA: Escanea tomate
    response = client.post(
        "/api/v1/orders/add_item",
        json={
            "station_id": 1,
            "product_barcode": "123456",
            "quantity": 2.0,
            "unit": "kg"
        },
        headers={"Authorization": f"Bearer {operador.token}"}
    )
    
    assert response.status_code == 200
    order_uuid = response.json()["order_uuid"]
    
    # 2. OPERADOR: Agrega pan
    response = client.post(
        "/api/v1/orders/add_item",
        json={
            "station_id": 1,
            "product_barcode": "789012",
            "quantity": 1.0,
            "unit": "unit"
        },
        headers={"Authorization": f"Bearer {operador.token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["total"] == 8.50  # 2*2.50 + 1*3.50
    
    # 3. OPERADOR: Genera QR
    response = client.post(
        f"/api/v1/orders/{order_uuid}/finalize",
        headers={"Authorization": f"Bearer {operador.token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["qr_code"] is not None
    
    # 4. CAJERO: Escanea QR
    response = client.get(
        f"/api/v1/orders/{order_uuid}",
        headers={"Authorization": f"Bearer {cajero.token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "Tomate"
    
    # 5. CAJERO: Confirma venta
    response = client.post(
        f"/api/v1/transactions/complete",
        json={
            "order_uuid": order_uuid,
            "payment_method": "cash",
            "amount": 10.11  # IVA incluído
        },
        headers={"Authorization": f"Bearer {cajero.token}"}
    )
    
    assert response.status_code == 201
    transaction_id = response.json()["id"]
    
    # 6. VERIFY: Stock decrementado
    tomate_after = test_db.query(Product).filter_by(id=tomate.id).first()
    assert tomate_after.stock_quantity == 48.0  # 50 - 2
    
    # 7. VERIFY: Audit log registrado
    audit = test_db.query(AuditLog).filter_by(
        action="VENTA_CONFIRMADA",
        entity_id=transaction_id
    ).first()
    assert audit is not None
    assert "ORD-" in audit.new_values["order_id"]
    
    # 8. VERIFY: Boleta fue encolada (Celery async)
    # Mock de Celery para verificar task fue creada
    assert celery_task_queue.has_task("emit_boleta", count=1)
```

---

## 🟢 Frontend Testing (Vue 3)

### Unit Tests con Vitest

**Ubicación:** `comerciales-frontend/tests/unit/`

```
tests/
├── unit/
│   ├── components/
│   │   ├── ProductScanner.spec.ts
│   │   ├── PreBoleta.spec.ts
│   │   ├── CajaDashboard.spec.ts
│   │   └── OperadorStation.spec.ts
│   ├── services/
│   │   ├── api.spec.ts
│   │   └── store.spec.ts
│   └── utils/
│       ├── formatters.spec.ts
│       └── validators.spec.ts
└── e2e/
    ├── balanza_flow.spec.ts
    ├── caja_flow.spec.ts
    └── full_sale.spec.ts
```

**Unit Test Example: ProductScanner Component**

```typescript
// tests/unit/components/ProductScanner.spec.ts

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ProductScanner from '@/components/ProductScanner.vue'
import { useOrderStore } from '@/stores/order'

describe('ProductScanner.vue', () => {
  
  it('renders scanner input field', () => {
    const wrapper = mount(ProductScanner)
    expect(wrapper.find('input[type="text"]').exists()).toBe(true)
  })
  
  it('emits add_item event when barcode is scanned', async () => {
    const store = useOrderStore()
    const wrapper = mount(ProductScanner, {
      global: {
        plugins: [createPinia()]
      }
    })
    
    const input = wrapper.find('input')
    await input.setValue('123456')
    await input.trigger('keydown.enter')
    
    // Verificar que store.addItem fue llamado
    expect(store.addItem).toHaveBeenCalledWith({
      barcode: '123456',
      quantity: 1
    })
  })
  
  it('shows error message if barcode is invalid', async () => {
    const wrapper = mount(ProductScanner)
    
    const input = wrapper.find('input')
    await input.setValue('INVALID')
    await input.trigger('keydown.enter')
    
    expect(wrapper.find('.error-message').text()).toContain('Invalid barcode')
  })
  
  it('clears input after successful scan', async () => {
    const store = useOrderStore()
    const wrapper = mount(ProductScanner)
    
    const input = wrapper.find('input')
    await input.setValue('123456')
    await input.trigger('keydown.enter')
    
    expect(input.element.value).toBe('')
  })
})
```

**Test Coverage:** 75% mínimo

```bash
vitest run --coverage --coverage.lines 75
```

---

### E2E Tests con Playwright

**Ubicación:** `comerciales-frontend/tests/e2e/`

```typescript
// tests/e2e/full_sale.spec.ts

import { test, expect } from '@playwright/test'

test('Full sale flow: balanza → caja → boleta', async ({ page }) => {
  
  // Setup: Ir a página login
  await page.goto('http://localhost:3000/login')
  
  // Login como OPERADOR
  await page.fill('input[name="email"]', 'operador@test.com')
  await page.fill('input[name="password"]', 'password123')
  await page.click('button:has-text("Ingresar")')
  
  // Verificar redirección a estaciones
  await expect(page).toHaveURL('http://localhost:3000/stations')
  
  // STEP 1: Escanear tomate (simular scanner)
  await page.focus('input[name="barcode"]')
  await page.keyboard.type('123456', { delay: 10 })  // Simular escaneo
  await page.keyboard.press('Enter')
  
  // Verificar que producto apareció en pre-boleta
  await expect(page.locator('text=Tomate')).toBeVisible()
  await expect(page.locator('text=$5.00')).toBeVisible()
  
  // STEP 2: Escanear pan
  await page.focus('input[name="barcode"]')
  await page.keyboard.type('789012', { delay: 10 })
  await page.keyboard.press('Enter')
  
  // Verificar total
  await expect(page.locator('text=Total: $8.50')).toBeVisible()
  
  // STEP 3: Generar QR
  await page.click('button:has-text("Finalizar")')
  
  // Verificar que aparece QR
  const qrImage = page.locator('img[alt="QR Code"]')
  await expect(qrImage).toBeVisible()
  
  // STEP 4: Login como CAJERO en otra pestaña
  const cajaPage = await page.context().newPage()
  await cajaPage.goto('http://localhost:3000/login')
  
  await cajaPage.fill('input[name="email"]', 'cajero@test.com')
  await cajaPage.fill('input[name="password"]', 'password123')
  await cajaPage.click('button:has-text("Ingresar")')
  
  await expect(cajaPage).toHaveURL('http://localhost:3000/caja')
  
  // STEP 5: Escanear QR en caja
  const qrCode = 'f47ac10b-58cc-4372-a567-0e02b2c3d479'  // UUID del QR
  
  await cajaPage.focus('input[name="qr_scanner"]')
  await cajaPage.keyboard.type(qrCode, { delay: 5 })
  await cajaPage.keyboard.press('Enter')
  
  // Verificar que detalle de orden apareció
  await expect(cajaPage.locator('text=Tomate × 2kg')).toBeVisible()
  await expect(cajaPage.locator('text=Pan integral × 1')).toBeVisible()
  await expect(cajaPage.locator('text=Total: $10.11')).toBeVisible()
  
  // STEP 6: Confirmar pago en efectivo
  await cajaPage.click('button[data-payment="cash"]')
  
  // Verificar confirmación
  await expect(cajaPage.locator('text=✓ VENTA COMPLETADA')).toBeVisible()
  await expect(cajaPage.locator('text=Folio SII:')).toBeVisible()
})

test('Offline mode: sin internet, cajero puede seguir cobrando', async ({ page }) => {
  
  // Simular desconexión
  await page.context().setOffline(true)
  
  // Ir a caja
  await page.goto('http://localhost:3000/caja')
  
  // Escanear QR
  await page.focus('input[name="qr_scanner"]')
  await page.keyboard.type('f47ac10b-58cc-4372-a567-0e02b2c3d479')
  await page.keyboard.press('Enter')
  
  // Verificar que muestra advertencia de offline pero permite cobrar
  await expect(page.locator('text=⚠️ MODO OFFLINE')).toBeVisible()
  
  // Confirmar pago
  await page.click('button[data-payment="cash"]')
  
  // Verificar: ✓ VENTA COMPLETADA pero sin folio SII
  await expect(page.locator('text=Boleta pendiente de sincronización')).toBeVisible()
  
  // Volver online
  await page.context().setOffline(false)
  
  // Esperar a que boleta se emita automáticamente (5 min en produc, 10s en test)
  await page.waitForTimeout(15000)
  
  // Verificar que folio SII apareció
  await expect(page.locator('text=Folio SII:')).toBeVisible()
})
```

---

## 🔵 CI/CD Pipeline (GitHub Actions)

**Ubicación:** `.github/workflows/test-and-deploy.yml`

```yaml
name: Test & Deploy

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      working-directory: comerciales-backend
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      working-directory: comerciales-backend
      env:
        DATABASE_URL: postgresql://postgres:test_pass@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
      run: |
        pytest tests/unit/ --cov=app.services --cov-report=xml --cov-fail-under=80
    
    - name: Run integration tests
      working-directory: comerciales-backend
      env:
        DATABASE_URL: postgresql://postgres:test_pass@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
      run: |
        pytest tests/integration/ -v
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./comerciales-backend/coverage.xml
    
    - name: Lint (Flake8)
      working-directory: comerciales-backend
      run: flake8 app/ tests/ --max-line-length=100 --ignore=E203,W503
    
    - name: Type check (mypy)
      working-directory: comerciales-backend
      run: mypy app/ --ignore-missing-imports

  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: comerciales-frontend/package-lock.json
    
    - name: Install dependencies
      working-directory: comerciales-frontend
      run: npm ci
    
    - name: Run unit tests
      working-directory: comerciales-frontend
      run: npm run test:unit -- --coverage --coverage.lines 75
    
    - name: Lint
      working-directory: comerciales-frontend
      run: npm run lint
    
    - name: Type check
      working-directory: comerciales-frontend
      run: npm run type-check
    
    - name: Build
      working-directory: comerciales-frontend
      run: npm run build

  test-e2e:
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Start services (Docker Compose)
      run: docker-compose -f comerciales-infra/docker-compose.test.yml up -d
    
    - name: Wait for services
      run: |
        docker-compose -f comerciales-infra/docker-compose.test.yml \
          exec -T backend bash -c 'wait-for-it localhost:5432 && wait-for-it localhost:6379'
    
    - name: Run E2E tests
      working-directory: comerciales-frontend
      run: npx playwright test
    
    - name: Upload playwright report
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: playwright-report
        path: comerciales-frontend/playwright-report/
    
    - name: Stop services
      if: always()
      run: docker-compose -f comerciales-infra/docker-compose.test.yml down

  deploy:
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend, test-e2e]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to VPS
      env:
        DEPLOY_KEY: ${{ secrets.VPS_DEPLOY_KEY }}
        DEPLOY_HOST: ${{ secrets.VPS_HOST }}
        DEPLOY_USER: ${{ secrets.VPS_USER }}
      run: |
        mkdir -p ~/.ssh
        echo "$DEPLOY_KEY" > ~/.ssh/deploy_key
        chmod 600 ~/.ssh/deploy_key
        ssh -i ~/.ssh/deploy_key $DEPLOY_USER@$DEPLOY_HOST 'cd /app && ./deploy.sh'

```

**Reglas Estrictas:**
- ✅ **TODOS los tests DEBEN pasar** antes de mergear a main
- ✅ **Coverage MÍNIMO:** Backend 80%, Frontend 75%
- ✅ **Lint DEBE pasar** (flake8, eslint, prettier)
- ✅ **Type check DEBE pasar** (mypy, TypeScript)
- ✅ **Codigo debe buildear** (sin warnings de build)
- ✅ **E2E DEBE pasar** antes de deploy a producción

---

## 📋 Checklist TDD Sprint-by-Sprint

### Sprint 1 (Inventario + Balanza)

**Backend:**
- [ ] Test: ProductService CRUD (80% coverage)
- [ ] Test: StationService (crear/actualizar estaciones)
- [ ] Test: OrderService (crear pre-órdenes, agregar items)
- [ ] Test: API endpoints /products, /stations, /orders
- [ ] Test: WebSocket sync (orden → pantalla cliente)

**Frontend:**
- [ ] Test: ProductScanner component
- [ ] Test: PreBoleta display
- [ ] Test: Pinia store (order state)
- [ ] Test: E2E: escaneo → QR generation

### Sprint 2-3 (Caja + SII)

**Backend:**
- [ ] Test: TransactionService (confirmar venta, actualizar stock)
- [ ] Test: BolService (integración SII mock)
- [ ] Test: Offline queue (pending_boletas)
- [ ] Test: RLS (multi-tenant isolation)
- [ ] Test: Celery task (emit_boleta async)

**Frontend:**
- [ ] Test: CajaDashboard component
- [ ] Test: QR scanner integration
- [ ] Test: E2E: QR escaneo → caja → pago

---

## 🎓 Recursos & Setup Local

**Setup Backend Testing:**
```bash
cd comerciales-backend
pip install -r requirements-test.txt

# Crear DB test
createdb test_comerciales

# Correr tests
pytest tests/ -v --cov

# Modo watch (re-run en cambios)
ptw
```

**Setup Frontend Testing:**
```bash
cd comerciales-frontend
npm install

# Run tests
npm run test:unit

# Modo watch
npm run test:unit -- --watch

# E2E
npx playwright install
npm run test:e2e
```

**Documentación:**
- Pytest: https://docs.pytest.org/
- Vitest: https://vitest.dev/
- Playwright: https://playwright.dev/
- FastAPI Testing: https://fastapi.tiangolo.com/advanced/testing-dependencies/

---

**Versión:** 0.1  
**Última actualización:** 20 de abril 2026  
**Responsable:** Allan (Backend), Jonathan (Frontend), Giuliano (Oversight)

