"""
Procesador de cola de mensajes de Telegram
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from telegram import Bot
from telegram.error import TelegramError

from ..database.connection import db
from ..models.telegram_models import TelegramMessage, TelegramUser, TelegramSubscription
from ..config.settings import settings

logger = logging.getLogger(__name__)

class QueueProcessor:
    """Procesador de cola de mensajes de Telegram"""
    
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.running = False
        
    async def initialize(self):
        """Inicializa el procesador"""
        if settings.TELEGRAM_BOT_TOKEN:
            self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            logger.info("✅ Procesador de cola inicializado")
        else:
            logger.error("❌ No se pudo inicializar: falta TELEGRAM_BOT_TOKEN")
            
    async def start(self):
        """Inicia el procesamiento de cola"""
        if not self.bot:
            await self.initialize()
            
        if not self.bot:
            logger.error("❌ No se puede iniciar sin bot configurado")
            return
            
        self.running = True
        logger.info("🔄 Iniciando procesamiento de cola...")
        
        while self.running:
            try:
                await self._process_pending_messages()
                await asyncio.sleep(settings.QUEUE_PROCESS_INTERVAL)
            except Exception as e:
                logger.error(f"Error en procesamiento de cola: {e}")
                await asyncio.sleep(5)  # Pausa corta antes de reintentar
                
    async def stop(self):
        """Detiene el procesamiento"""
        self.running = False
        logger.info("🛑 Procesamiento de cola detenido")
        
    def is_running(self) -> bool:
        """Verifica si está ejecutándose"""
        return self.running
        
    async def _process_pending_messages(self):
        """Procesa mensajes pendientes en la cola"""
        try:
            # Obtener mensajes pendientes
            pending_messages = self._get_pending_messages()
            
            if not pending_messages:
                logger.debug("📭 No hay mensajes pendientes")
                return
                
            logger.info(f"📨 Procesando {len(pending_messages)} mensajes pendientes")
            
            for message in pending_messages:
                try:
                    await self._send_message(message)
                except Exception as e:
                    logger.error(f"Error enviando mensaje {message.id}: {e}")
                    self._mark_message_error(message.id, str(e))
                    
        except Exception as e:
            logger.error(f"Error obteniendo mensajes pendientes: {e}")
            
    def _get_pending_messages(self) -> List[TelegramMessage]:
        """Obtiene mensajes pendientes de la base de datos"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener mensajes no enviados, ordenados por prioridad y fecha
                cursor.execute("""
                    SELECT ID, CHAT_ID, MESSAGE_TYPE, MESSAGE_TEXT, PRIORITY, 
                           CREATED_AT, ERROR_MESSAGE
                    FROM STL_TELEGRAM_QUEUE 
                    WHERE STATUS = 'PENDING' 
                    ORDER BY PRIORITY DESC, CREATED_AT ASC
                    ROWS 50
                """)
                rows = cursor.fetchall()
                
                messages = []
                for row in rows:
                    message = TelegramMessage(
                        id=row[0],
                        chat_id=row[1],
                        message_type=row[2],
                        message_text=row[3],
                        priority=row[4],
                        created_at=row[5],
                        error_message=row[6]
                    )
                    messages.append(message)
                    
                return messages
                
        except Exception as e:
            logger.error(f"Error obteniendo mensajes pendientes: {e}")
            return []
            
    async def _send_message(self, message: TelegramMessage):
        """Envía un mensaje específico"""
        try:
            # Si chat_id es 0, enviar a todos los usuarios suscritos
            if message.chat_id == 0:
                await self._send_to_subscribers(message)
            else:
                # Enviar a chat específico
                await self.bot.send_message(
                    chat_id=message.chat_id,
                    text=message.message_text,
                    parse_mode='HTML'
                )
                
            # Marcar como enviado
            self._mark_message_sent(message.id)
            logger.debug(f"✅ Mensaje {message.id} enviado correctamente")
            
        except TelegramError as e:
            logger.error(f"Error de Telegram enviando mensaje {message.id}: {e}")
            self._mark_message_error(message.id, str(e))
        except Exception as e:
            logger.error(f"Error enviando mensaje {message.id}: {e}")
            self._mark_message_error(message.id, str(e))
            
    async def _send_to_subscribers(self, message: TelegramMessage):
        """Envía mensaje a usuarios suscritos según el tipo"""
        try:
            subscribers = self._get_subscribers_for_type(message.message_type)
            
            if not subscribers:
                logger.debug(f"📭 No hay suscriptores para {message.message_type}")
                return
                
            logger.info(f"📢 Enviando a {len(subscribers)} suscriptores de {message.message_type}")
            
            for subscriber in subscribers:
                try:
                    await self.bot.send_message(
                        chat_id=subscriber.telegram_user_id,
                        text=message.message_text,
                        parse_mode='HTML'
                    )
                    await asyncio.sleep(0.1)  # Evitar rate limiting
                except TelegramError as e:
                    logger.warning(f"No se pudo enviar a usuario {subscriber.telegram_user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error enviando a suscriptores: {e}")
            
    def _get_subscribers_for_type(self, message_type: str) -> List[TelegramUser]:
        """Obtiene usuarios suscritos a un tipo de notificación"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT DISTINCT u.TELEGRAM_ID, u.TELEGRAM_USERNAME, 
                           u.TELEGRAM_FIRST_NAME, u.TELEGRAM_LAST_NAME
                    FROM STL_TELEGRAM_USERS u
                    INNER JOIN STL_TELEGRAM_SUBSCRIPTIONS s ON u.ID = s.TELEGRAM_USER_ID
                    WHERE u.IS_ACTIVE = 1 
                      AND u.IS_VERIFIED = 1
                      AND s.IS_ACTIVE = 1
                      AND (s.NOTIFICATION_TYPE = ? OR s.NOTIFICATION_TYPE = 'ALL')
                """, (message_type,))
                
                rows = cursor.fetchall()
                
                users = []
                for row in rows:
                    user = TelegramUser(
                        telegram_user_id=row[0],
                        telegram_username=row[1],
                        first_name=row[2],
                        last_name=row[3]
                    )
                    users.append(user)
                    
                return users
                
        except Exception as e:
            logger.error(f"Error obteniendo suscriptores: {e}")
            return []
            
    def _mark_message_sent(self, message_id: int):
        """Marca mensaje como enviado"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE STL_TELEGRAM_QUEUE 
                    SET STATUS = 'SENT', SENT_AT = ? 
                    WHERE ID = ?
                """, (datetime.now(), message_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error marcando mensaje {message_id} como enviado: {e}")
            
    def _mark_message_error(self, message_id: int, error_message: str):
        """Marca mensaje con error"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE STL_TELEGRAM_QUEUE 
                    SET STATUS = 'ERROR', ERROR_MESSAGE = ? 
                    WHERE ID = ?
                """, (error_message[:500], message_id))  # Limitar longitud del error
                conn.commit()
        except Exception as e:
            logger.error(f"Error marcando mensaje {message_id} con error: {e}")