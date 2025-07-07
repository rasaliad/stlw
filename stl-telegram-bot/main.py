#!/usr/bin/env python3
"""
STL Telegram Bot
Bot independiente para notificaciones del sistema STL Warehouse Management
"""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path


# Agregar el directorio actual al path para imports
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from src.bot.telegram_bot import STLTelegramBot
from src.services.queue_processor import QueueProcessor
from src.config.settings import settings


# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.LOG_FILE) if settings.LOG_FILE else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

class STLBotService:
    """Servicio principal del bot STL"""
    
    def __init__(self):
        self.bot = None
        self.queue_processor = None
        self.running = False
        
    async def start(self):
        """Inicia el servicio del bot"""
        try:
            logger.info("🚀 Iniciando STL Telegram Bot...")
            
            # Inicializar bot
            self.bot = STLTelegramBot()
            await self.bot.initialize()
            
            # Inicializar procesador de cola
            self.queue_processor = QueueProcessor()
            
            # Iniciar servicios
            self.running = True
            
            # Ejecutar bot y procesador concurrentemente
            await asyncio.gather(
                self.bot.start(),
                self.queue_processor.start(),
                self._monitor_health()
            )
            
        except Exception as e:
            logger.error(f"❌ Error iniciando servicio: {e}")
            await self.stop()
            
    async def stop(self):
        """Detiene el servicio del bot"""
        logger.info("🛑 Deteniendo STL Telegram Bot...")
        self.running = False
        
        if self.bot:
            await self.bot.stop()
            
        if self.queue_processor:
            await self.queue_processor.stop()
            
        logger.info("✅ Servicio detenido correctamente")
        
    async def _monitor_health(self):
        """Monitor de salud del servicio"""
        while self.running:
            try:
                await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)
                
                # Verificar estado del bot
                if self.bot and not self.bot.is_running():
                    logger.warning("⚠️ Bot no está corriendo, intentando reiniciar...")
                    await self.bot.start()
                    
                # Verificar estado del procesador
                if self.queue_processor and not self.queue_processor.is_running():
                    logger.warning("⚠️ Procesador de cola no está corriendo, intentando reiniciar...")
                    await self.queue_processor.start()
                    
            except Exception as e:
                logger.error(f"Error en monitor de salud: {e}")

async def main():
    """Función principal"""
    service = STLBotService()
    
    # Configurar manejadores de señales para cierre graceful
    def signal_handler(signum, frame):
        logger.info(f"Señal {signum} recibida, iniciando cierre graceful...")
        asyncio.create_task(service.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("Interrupción por teclado detectada")
    finally:
        await service.stop()

if __name__ == "__main__":
    # Verificar configuración mínima
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN no configurado")
        sys.exit(1)
        
    logger.info("🤖 STL Telegram Bot v1.0")
    logger.info(f"📝 Log level: {settings.LOG_LEVEL}")
    logger.info(f"🗄️ Base de datos: {settings.DB_HOST}:{settings.DB_PORT}")
    
    # Ejecutar servicio
    asyncio.run(main())