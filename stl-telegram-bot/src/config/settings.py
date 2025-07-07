"""
Configuración del bot STL Telegram
"""
import os
from typing import Optional

class Settings:
    """Configuración centralizada"""
    
    # Base de datos (configuración por defecto para Docker)
    DB_HOST: str = os.getenv("DB_HOST", "host.docker.internal")
    DB_PORT: int = int(os.getenv("DB_PORT", "3050"))
    DB_PATH: str = os.getenv("DB_PATH", "C:/App/STL/Datos/DATOS_STL.FDB")
    DB_USER: str = os.getenv("DB_USER", "sysdba")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "masterkey")
    
    # Bot Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # Intervalos (segundos)
    QUEUE_PROCESS_INTERVAL: int = int(os.getenv("QUEUE_PROCESS_INTERVAL", "60"))
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "300"))
    
    @property
    def database_url(self) -> str:
        """URL de conexión a la base de datos"""
        return f"{self.DB_HOST}/{self.DB_PORT}:{self.DB_PATH}"

# Instancia global de configuración
settings = Settings()