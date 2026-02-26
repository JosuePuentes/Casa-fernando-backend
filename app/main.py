"""Aplicación principal - Casa Fernando Backend."""
import logging
import re
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import init_db
from app.config import get_settings
from app.api import auth, cliente_area, mesonera, pos, facturacion, admin, websocket, comandas, mesas

logger = logging.getLogger(__name__)

VERCEL_REGEX = re.compile(r"^https://[a-z0-9.-]+\.vercel\.app$")


class AddCORSHeadersMiddleware(BaseHTTPMiddleware):
    """Añade CORS headers a TODAS las respuestas para evitar bloqueos."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        origin = request.headers.get("origin")
        if origin and (origin in ("http://localhost:3000", "https://casa-fernando-frontend.vercel.app") or VERCEL_REGEX.match(origin)):
            response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializar BD al arrancar."""
    await init_db()
    yield


app = FastAPI(
    title="Casa Fernando API",
    description="Backend ERP para restaurante - Área cliente, mesonera, punto de venta y facturación",
    version="1.0.0",
    lifespan=lifespan,
)

_settings = get_settings()
_cors_origins = [_o.strip() for _o in _settings.CORS_ORIGINS.split(",") if _o.strip()]
if not _cors_origins:
    _cors_origins = ["http://localhost:3000", "https://casa-fernando-frontend.vercel.app"]
if "https://casa-fernando-frontend.vercel.app" not in _cors_origins:
    _cors_origins.append("https://casa-fernando-frontend.vercel.app")

app.add_middleware(AddCORSHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Maneja errores no capturados. Delega HTTPException y ValidationError."""
    from fastapi import HTTPException
    from fastapi.exceptions import RequestValidationError
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    if isinstance(exc, RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})
    logger.exception("Error no capturado: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc) if str(exc) else "Error interno del servidor"},
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
    return {
        "app": "Casa Fernando Backend",
        "docs": "/docs",
        "version": "1.0.0",
    }
