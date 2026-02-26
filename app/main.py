"""Aplicación principal - Casa Fernando Backend."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api import auth, cliente_area, mesonera, pos, facturacion, admin, websocket, comandas


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializar BD al arrancar."""
    await init_db()
    yield
    # cleanup si fuera necesario


app = FastAPI(
    title="Casa Fernando API",
    description="Backend ERP para restaurante - Área cliente, mesonera, punto de venta y facturación",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(auth.router, prefix="/api")
app.include_router(cliente_area.router, prefix="/api")
app.include_router(mesonera.router, prefix="/api")
app.include_router(pos.router, prefix="/api")
app.include_router(facturacion.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(websocket.router, prefix="/api")
app.include_router(comandas.router, prefix="/api")
app.include_router(mesas.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "app": "Casa Fernando Backend",
        "docs": "/docs",
        "version": "1.0.0",
    }
