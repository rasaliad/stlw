from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router
from app.routers.sap_stl import router as sap_stl_router
from app.core.config import settings
from app.services.background_sync_service import background_sync_service
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando servicios de background...")
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