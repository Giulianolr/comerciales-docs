"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.v1.endpoints import auth, products, orders, transactions, ws
from app.core.events import init_redis_manager

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Comerciales API",
    description="Sistema de Inventario Dinámico para Locales Comerciales",
    version="0.1.0",
)


@app.on_event("startup")
async def startup_event():
    """Inicializar Redis pub/sub manager en startup."""
    await init_redis_manager(use_fake=True)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok"}


# Registrar routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(ws.router, prefix="/api/v1")
