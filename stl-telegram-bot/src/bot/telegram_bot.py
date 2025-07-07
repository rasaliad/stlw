"""
Bot principal de Telegram para STL
"""
import logging
from datetime import datetime
from typing import Optional, List

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

from ..database.connection import db
from ..models.telegram_models import TelegramUser, TelegramSubscription, TelegramCommand
from ..config.settings import settings

logger = logging.getLogger(__name__)

class STLTelegramBot:
    """Bot principal de Telegram para STL"""
    
    def __init__(self):
        self.application: Optional[Application] = None
        self.running = False
        
    async def initialize(self):
        """Inicializa el bot"""
        try:
            if not settings.TELEGRAM_BOT_TOKEN:
                raise ValueError("TELEGRAM_BOT_TOKEN no configurado")
                
            # Crear aplicación
            self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
            
            # Registrar handlers
            self._register_handlers()
            
            # Handler para TODOS los mensajes (debug) - debe ir DESPUÉS de los comandos
            logger.info("🔧 Agregando handler de debug...")
            from telegram.ext import MessageHandler, filters
            self.application.add_handler(MessageHandler(filters.ALL, self._debug_all_messages))
            
            logger.info("✅ Bot de Telegram inicializado")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando bot: {e}")
            raise
            
    def _register_handlers(self):
        """Registra los manejadores de comandos"""
        if not self.application:
            return
            
        # Comandos básicos
        self.application.add_handler(CommandHandler("start", self._cmd_start))
        self.application.add_handler(CommandHandler("help", self._cmd_help))
        #self.application.add_handler(CommandHandler("status", self._cmd_status))
        
        # Comandos de vinculación
        self.application.add_handler(CommandHandler("vincular", self._cmd_vincular))
        
        # Comandos de suscripción
        self.application.add_handler(CommandHandler("suscribir", self._cmd_suscribir))
        self.application.add_handler(CommandHandler("desuscribir", self._cmd_desuscribir))
        
        # Comandos de consulta
        self.application.add_handler(CommandHandler("consultar", self._cmd_consultar))
        
        logger.info("📝 Handlers de comandos registrados")
        
        # Debug: remover handlers problemáticos temporalmente
        logger.info("🔧 Handlers configurados sin debug adicional")
        
    async def _debug_all_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Debug: captura TODOS los comandos"""
        try:
            user = update.effective_user
            message = update.effective_message
            if user and message:
                logger.info(f"🎯 COMANDO INTERCEPTADO - Usuario: {user.id} - Comando: '{message.text}'")
        except Exception as e:
            logger.error(f"Error en debug command handler: {e}")
    
    async def _debug_all_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Debug: captura TODOS los mensajes"""
        try:
            user = update.effective_user
            message = update.effective_message
            if user and message:
                logger.info(f"🔥 MENSAJE RECIBIDO - Usuario: {user.id} (@{user.username}) - Texto: '{message.text}'")
        except Exception as e:
            logger.error(f"Error en debug handler: {e}")
        
    async def start(self):
        """Inicia el bot"""
        if not self.application:
            raise RuntimeError("Bot no inicializado")
            
        try:
            self.running = True
            logger.info("🤖 Iniciando bot de Telegram...")
            
            # Inicializar y ejecutar
            await self.application.initialize()
            await self.application.start()
            
            # Obtener información del bot
            bot_info = await self.application.bot.get_me()
            logger.info(f"✅ Bot iniciado: @{bot_info.username}")
            
            # Ejecutar bot (polling)
            await self.application.updater.start_polling(drop_pending_updates=True)
            
            # Mantener corriendo - usar asyncio.Event en lugar de idle()
            import asyncio
            stop_event = asyncio.Event()
            await stop_event.wait()
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando bot: {e}")
            raise
            
    async def stop(self):
        """Detiene el bot"""
        if self.application and self.running:
            logger.info("🛑 Deteniendo bot...")
            self.running = False
            
            try:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            except Exception as e:
                logger.debug(f"Error al detener bot (normal): {e}")
            
            logger.info("✅ Bot detenido")
            
    def is_running(self) -> bool:
        """Verifica si el bot está corriendo"""
        return self.running
        
    # Comandos del bot
    
    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Registra usuario"""
        try:
            user = update.effective_user
            if not user:
                return
                
            # Registrar usuario en base de datos
            telegram_user = self._register_user(user)
            
            welcome_msg = f"""
🏭 <b>¡Bienvenido al Bot STL!</b>

Hola {user.first_name}, has sido registrado en el sistema.

<b>Próximos pasos:</b>
1. Solicita un código de vinculación al administrador
2. Usa /vincular &lt;código&gt; para vincular tu cuenta
3. Espera que el administrador active tu cuenta
4. Usa /suscribir para recibir notificaciones

<b>Comandos disponibles:</b>
/help - Ver ayuda completa
/status - Ver estado de tu cuenta
/vincular &lt;código&gt; - Vincular cuenta
"""
            
            await update.message.reply_text(welcome_msg, parse_mode=ParseMode.HTML)
            
            # Registrar comando
            # self._log_command(telegram_user.id, "start", None, "Usuario registrado")
            
        except Exception as e:
            logger.error(f"Error en /start: {e}")
            await update.message.reply_text("❌ Error procesando comando")
            
    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Muestra ayuda"""
        help_msg = """
🤖 <b>Ayuda del Bot STL</b>

<b>Comandos básicos:</b>
/start - Registrarse en el sistema
/status - Ver estado de tu cuenta
/help - Mostrar esta ayuda

<b>Vinculación:</b>
/vincular &lt;código&gt; - Vincular con usuario del sistema

<b>Notificaciones:</b>
/suscribir &lt;tipo&gt; - Suscribirse a notificaciones
/desuscribir &lt;tipo&gt; - Cancelar suscripción

<b>Tipos de notificación:</b>
• DELIVERY_NOTES - Envíos de pedidos
• GOODS_RECEIPTS - Recepciones
• ERRORS - Solo errores
• ALL - Todas las notificaciones

<b>Consultas:</b>
/consultar producto &lt;código&gt; - Info de producto
/consultar pedido &lt;número&gt; - Estado de pedido
/consultar existencia &lt;código&gt; - Stock actual

<b>Ejemplos:</b>
/vincular ABC123
/suscribir ALL
/consultar producto PRD001
"""
        
        await update.message.reply_text(help_msg, parse_mode=ParseMode.HTML)
        
    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status - Muestra estado del usuario"""
        try:
            user = update.effective_user
            if not user:
                return
                
            telegram_user = self._get_user_by_telegram_id(user.id)
            
            if not telegram_user:
                await update.message.reply_text("❌ Usuario no encontrado. Usa /start para registrarte.")
                return
                
            # Obtener suscripciones
            subscriptions = self._get_user_subscriptions(telegram_user.id)
            
            status_msg = f"""
👤 <b>Estado de tu cuenta</b>

<b>Usuario:</b> {user.first_name} {user.last_name or ''}
<b>Username:</b> @{user.username or 'N/A'}
<b>Registrado:</b> {telegram_user.created_at.strftime('%d/%m/%Y') if telegram_user.created_at else 'N/A'}

<b>Vinculación:</b> {'✅ Verificado' if telegram_user.is_verified else '❌ No verificado'}
<b>Estado:</b> {'🟢 Activo' if telegram_user.is_active else '🔴 Esta Inactivo'}

<b>Suscripciones activas:</b>
"""
            
            if subscriptions:
                for sub in subscriptions:
                    status_msg += f"• {sub.notification_type}\\n"
            else:
                status_msg += "• Ninguna\\n"
                
            status_msg += "\\n💡 Usa /help para ver comandos disponibles"
            
            await update.message.reply_text(status_msg, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            logger.error(f"Error en /status: {e}")
            await update.message.reply_text("❌ Error obteniendo estado")
            
    async def _cmd_vincular(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /vincular - Vincula usuario con código"""
        logger.info(f"🔥 COMANDO VINCULAR RECIBIDO!")
        
        # Respuesta directa de debug para confirmar que el handler funciona
        await update.message.reply_text("🚀 FUNCIONA! Este es el handler de /vincular de Claude. El bot está respondiendo correctamente.")
        
        try:
            if not context.args or len(context.args) != 1:
                await update.message.reply_text("❌ Uso: /vincular &lt;código&gt;", parse_mode=ParseMode.HTML)
                return
                
            code = context.args[0].upper()
            user = update.effective_user
            
            if not user:
                return
            
            logger.info(f"📱 Usuario {user.id} ({user.username}) intentando vincular con código: {code}")
                
            # Verificar código en base de datos
            success = self._verify_and_link_user(user.id, code)
            logger.info(f"🔍 Resultado de verificación: {success}")
            
            if success:
                await update.message.reply_text("""
✅ <b>¡Código verificado!</b>

Tu cuenta ha sido vinculada correctamente.
Ahora espera que el administrador active tu cuenta.

Usa /status para verificar tu estado.
""", parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text("❌ Verificación falló")
                
        except Exception as e:
            logger.error(f"Error en /vincular: {e}")
            await update.message.reply_text("❌ Error procesando vinculación")
            
    async def _cmd_suscribir(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /suscribir - Suscribe a notificaciones"""
        try:
            if not context.args or len(context.args) != 1:
                await update.message.reply_text("""
❌ <b>Uso incorrecto</b>

Uso: /suscribir &lt;tipo&gt;

<b>Tipos disponibles:</b>
• DELIVERY_NOTES - Envíos de pedidos
• GOODS_RECEIPTS - Recepciones  
• ERRORS - Solo errores
• ALL - Todas las notificaciones
""", parse_mode=ParseMode.HTML)
                return
                
            notification_type = context.args[0].upper()
            valid_types = ['DELIVERY_NOTES', 'GOODS_RECEIPTS', 'ERRORS', 'ALL']
            
            if notification_type not in valid_types:
                await update.message.reply_text(f"❌ Tipo inválido. Usa: {', '.join(valid_types)}")
                return
                
            user = update.effective_user
            if not user:
                return
                
            # Verificar que el usuario esté verificado y activo
            telegram_user = self._get_user_by_telegram_id(user.id)
            if not telegram_user or not telegram_user.is_verified or not telegram_user.is_active:
                await update.message.reply_text("❌ Tu cuenta debe estar verificada y activa para suscribirte.")
                return
                
            # Crear suscripción
            success = self._create_subscription(telegram_user.id, notification_type)
            
            if success:
                await update.message.reply_text(f"✅ Suscrito a notificaciones de <b>{notification_type}</b>", parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text("❌ Error creando suscripción o ya existe.")
                
        except Exception as e:
            logger.error(f"Error en /suscribir: {e}")
            await update.message.reply_text("❌ Error procesando suscripción")
            
    async def _cmd_desuscribir(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /desuscribir - Cancela suscripción"""
        try:
            if not context.args or len(context.args) != 1:
                await update.message.reply_text("❌ Uso: /desuscribir &lt;tipo&gt;", parse_mode=ParseMode.HTML)
                return
                
            notification_type = context.args[0].upper()
            user = update.effective_user
            
            if not user:
                return
                
            telegram_user = self._get_user_by_telegram_id(user.id)
            if not telegram_user:
                await update.message.reply_text("❌ Usuario no encontrado")
                return
                
            # Cancelar suscripción
            success = self._cancel_subscription(telegram_user.id, notification_type)
            
            if success:
                await update.message.reply_text(f"✅ Suscripción a <b>{notification_type}</b> cancelada", parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text("❌ No se encontró esa suscripción")
                
        except Exception as e:
            logger.error(f"Error en /desuscribir: {e}")
            await update.message.reply_text("❌ Error cancelando suscripción")
            
    async def _cmd_consultar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /consultar - Realiza consultas al sistema"""
        try:
            if not context.args or len(context.args) < 2:
                await update.message.reply_text("""
❌ <b>Uso incorrecto</b>

Uso: /consultar &lt;tipo&gt; &lt;valor&gt;

<b>Tipos disponibles:</b>
• producto &lt;código&gt; - Info de producto
• pedido &lt;número&gt; - Estado de pedido
• existencia &lt;código&gt; - Stock actual

<b>Ejemplos:</b>
/consultar producto PRD001
/consultar pedido 12345
/consultar existencia PRD001
""", parse_mode=ParseMode.HTML)
                return
                
            query_type = context.args[0].lower()
            query_value = ' '.join(context.args[1:])
            
            user = update.effective_user
            if not user:
                return
                
            # Verificar que el usuario esté activo
            telegram_user = self._get_user_by_telegram_id(user.id)
            if not telegram_user or not telegram_user.is_verified or not telegram_user.is_active:
                await update.message.reply_text("❌ Tu cuenta debe estar verificada y activa para realizar consultas.")
                return
                
            # Procesar consulta
            result = await self._process_query(query_type, query_value)
            
            await update.message.reply_text(result, parse_mode=ParseMode.HTML)
            
            # Registrar comando
            # self._log_command(telegram_user.id, "consultar", f"{query_type} {query_value}", "Consulta procesada")
            
        except Exception as e:
            logger.error(f"Error en /consultar: {e}")
            await update.message.reply_text("❌ Error procesando consulta")
            
    # Métodos auxiliares de base de datos
    
    def _register_user(self, telegram_user) -> TelegramUser:
        """Registra un nuevo usuario de Telegram"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si ya existe
                cursor.execute("SELECT ID FROM STL_TELEGRAM_USERS WHERE TELEGRAM_ID = ?", (telegram_user.id,))
                existing = cursor.fetchone()
                
                if existing:
                    return self._get_user_by_telegram_id(telegram_user.id)
                    
                # Insertar nuevo usuario
                cursor.execute("""
                    INSERT INTO STL_TELEGRAM_USERS 
                    (TELEGRAM_ID, TELEGRAM_USERNAME, TELEGRAM_FIRST_NAME, TELEGRAM_LAST_NAME, CREATED_AT)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    telegram_user.id,
                    telegram_user.username,
                    telegram_user.first_name,
                    telegram_user.last_name,
                    datetime.now()
                ))
                conn.commit()
                
                return self._get_user_by_telegram_id(telegram_user.id)
                
        except Exception as e:
            logger.error(f"Error registrando usuario: {e}")
            raise
            
    def _get_user_by_telegram_id(self, telegram_id: int) -> Optional[TelegramUser]:
        """Obtiene usuario por ID de Telegram"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ID, TELEGRAM_ID, TELEGRAM_USERNAME, TELEGRAM_FIRST_NAME, TELEGRAM_LAST_NAME,
                           USER_ID, VERIFICATION_CODE, IS_VERIFIED, IS_ACTIVE, CREATED_AT
                    FROM STL_TELEGRAM_USERS 
                    WHERE TELEGRAM_ID = ?
                """, (telegram_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                    
                return TelegramUser(
                    id=row[0],
                    telegram_user_id=row[1],
                    telegram_username=row[2],
                    first_name=row[3],
                    last_name=row[4],
                    linked_user_id=row[5],
                    verification_code=row[6],
                    is_verified=row[7] == 1,
                    is_active=row[8] == 1,
                    created_at=row[9]
                )
                
        except Exception as e:
            logger.error(f"Error obteniendo usuario: {e}")
            return None
            
    def _verify_and_link_user(self, telegram_id: int, code: str) -> bool:
        """Verifica código y vincula usuario"""
        logger.info(f"🚀 INICIANDO VERIFICACIÓN - telegram_id: {telegram_id}, code: '{code}'")
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Buscar usuario con código correcto
                cursor.execute("""
                    SELECT ID, VERIFICATION_CODE, IS_VERIFIED, IS_ACTIVE 
                    FROM STL_TELEGRAM_USERS 
                    WHERE TELEGRAM_ID = ? AND VERIFICATION_CODE = ?
                """, (telegram_id, code))
                
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"❌ No se encontró usuario con telegram_id {telegram_id} y código '{code}'")
                    return False
                
                user_id, stored_code, is_verified, is_active = row
                logger.info(f"✅ Usuario encontrado - ID: {user_id}, Code: {stored_code}, Verified: {is_verified}, Active: {is_active}")
                
                # Si ya está verificado, devolver true
                if is_verified == 1:
                    logger.info(f"✅ Usuario ya verificado!")
                    return True
                
                # Si no está verificado, marcarlo como verificado
                cursor.execute("""
                    UPDATE STL_TELEGRAM_USERS 
                    SET IS_VERIFIED = 1
                    WHERE ID = ?
                """, (user_id,))
                conn.commit()
                
                rows = cursor.rowcount
                logger.info(f"✅ Usuario verificado! Filas actualizadas: {rows}")
                return rows > 0
                
        except Exception as e:
            logger.error(f"Error en verificación: {e}")
            return False
            
    def _get_user_subscriptions(self, user_id: int) -> List[TelegramSubscription]:
        """Obtiene suscripciones de un usuario"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ID, TELEGRAM_USER_ID, NOTIFICATION_TYPE, IS_ACTIVE, CREATED_AT
                    FROM STL_TELEGRAM_SUBSCRIPTIONS 
                    WHERE TELEGRAM_USER_ID = ? AND IS_ACTIVE = 1
                """, (user_id,))
                
                rows = cursor.fetchall()
                subscriptions = []
                
                for row in rows:
                    sub = TelegramSubscription(
                        id=row[0],
                        user_id=row[1],
                        notification_type=row[2],
                        is_active=row[3] == 1,
                        created_at=row[4]
                    )
                    subscriptions.append(sub)
                    
                return subscriptions
                
        except Exception as e:
            logger.error(f"Error obteniendo suscripciones: {e}")
            return []
            
    def _create_subscription(self, user_id: int, notification_type: str) -> bool:
        """Crea nueva suscripción"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si ya existe
                cursor.execute("""
                    SELECT ID FROM STL_TELEGRAM_SUBSCRIPTIONS 
                    WHERE TELEGRAM_USER_ID = ? AND NOTIFICATION_TYPE = ? AND IS_ACTIVE = 1
                """, (user_id, notification_type))
                
                if cursor.fetchone():
                    return False  # Ya existe
                    
                # Crear nueva suscripción
                cursor.execute("""
                    INSERT INTO STL_TELEGRAM_SUBSCRIPTIONS 
                    (TELEGRAM_USER_ID, NOTIFICATION_TYPE, IS_ACTIVE, CREATED_AT)
                    VALUES (?, ?, 1, ?)
                """, (user_id, notification_type, datetime.now()))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error creando suscripción: {e}")
            return False
            
    def _cancel_subscription(self, user_id: int, notification_type: str) -> bool:
        """Cancela suscripción"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE STL_TELEGRAM_SUBSCRIPTIONS 
                    SET IS_ACTIVE = 0 
                    WHERE TELEGRAM_USER_ID = ? AND NOTIFICATION_TYPE = ? AND IS_ACTIVE = 1
                """, (user_id, notification_type))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error cancelando suscripción: {e}")
            return False
            
    def _log_command(self, user_id: int, command: str, parameters: Optional[str], response: str):
        """Registra comando ejecutado"""
        # TODO: Implementar tabla STL_TELEGRAM_COMMANDS
        logger.info(f"📋 Comando ejecutado - Usuario: {user_id}, Comando: {command}, Params: {parameters}")
            
    async def _process_query(self, query_type: str, query_value: str) -> str:
        """Procesa consultas al sistema"""
        try:
            if query_type == "producto":
                return await self._query_product(query_value)
            elif query_type == "pedido":
                return await self._query_order(query_value)
            elif query_type == "existencia":
                return await self._query_stock(query_value)
            else:
                return "❌ Tipo de consulta no válido"
                
        except Exception as e:
            logger.error(f"Error procesando consulta {query_type}: {e}")
            return "❌ Error procesando consulta"
            
    async def _query_product(self, product_code: str) -> str:
        """Consulta información de producto"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ITEM_CODE, ITEM_NAME, ITEM_TYPE, INVENTORY_UNIT, PURCHASE_UNIT
                    FROM STL_ITEMS 
                    WHERE ITEM_CODE = ?
                """, (product_code,))
                
                row = cursor.fetchone()
                if not row:
                    return f"❌ Producto {product_code} no encontrado"
                    
                return f"""
📦 <b>Producto {row[0]}</b>

<b>Nombre:</b> {row[1]}
<b>Tipo:</b> {row[2] or 'N/A'}
<b>Unidad inventario:</b> {row[3] or 'N/A'}
<b>Unidad compra:</b> {row[4] or 'N/A'}
"""
                
        except Exception as e:
            logger.error(f"Error consultando producto: {e}")
            return "❌ Error consultando producto"
            
    async def _query_order(self, order_number: str) -> str:
        """Consulta estado de pedido"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT numero_pedido, fecha_pedido, estado, observaciones
                    FROM pedidos 
                    WHERE numero_pedido = ?
                """, (order_number,))
                
                row = cursor.fetchone()
                if not row:
                    return f"❌ Pedido {order_number} no encontrado"
                    
                return f"""
📋 <b>Pedido {row[0]}</b>

<b>Fecha:</b> {row[1].strftime('%d/%m/%Y') if row[1] else 'N/A'}
<b>Estado:</b> {row[2] or 'N/A'}
<b>Observaciones:</b> {row[3] or 'Ninguna'}
"""
                
        except Exception as e:
            logger.error(f"Error consultando pedido: {e}")
            return "❌ Error consultando pedido"
            
    async def _query_stock(self, product_code: str) -> str:
        """Consulta existencia de producto"""
        # Placeholder - implementar según estructura de BD
        return f"📊 <b>Existencia de {product_code}</b>\\n\\n⚠️ Funcionalidad en desarrollo"