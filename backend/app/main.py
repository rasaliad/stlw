from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router
from app.routers.sap_stl import router as sap_stl_router
from app.core.config import settings
from app.services.background_sync_service import background_sync_service
import logging
import logging.handlers
import sys
from pathlib import Path

# Configurar logging optimizado con rotación automática
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.WARNING)

# Usar directorio de logs de NSSM: C:\App\stlw\logs
# En producción: ../logs (relativo a backend/)
# En desarrollo/docker: logs/ (actual directory)
log_dir = Path(__file__).parent.parent.parent / "logs"  # stlw/logs
log_dir.mkdir(exist_ok=True)

# Handler con rotación (max 10MB por archivo, mantener 5 archivos)
file_handler = logging.handlers.RotatingFileHandler(
    filename=log_dir / "backend.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(log_level)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

# Handler para consola - solo errores críticos (para evitar duplicación con NSSM)
# NSSM captura stdout/stderr, así que solo enviamos errores críticos a stderr
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.ERROR)  # Solo ERROR y CRITICAL
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))

# Configurar logging root
logging.basicConfig(
    level=log_level,
    handlers=[file_handler, console_handler]
)

# Silenciar loggers verbosos
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)
logging.getLogger("apscheduler.scheduler").setLevel(logging.WARNING)
logging.getLogger("passlib").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("STL Backend iniciando...")
    logger.info(f"Nivel de logging configurado: {settings.LOG_LEVEL}")
    logger.info("Iniciando servicios de sincronización automática...")
    await background_sync_service.start_scheduler()
    yield
    # Shutdown
    logger.info("Deteniendo servicios de background...")
    await background_sync_service.stop_scheduler()

app = FastAPI(
    title="STL Backend API",
    description="API para sistema STL con Firebird",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
app.include_router(sap_stl_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "STL Backend API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)