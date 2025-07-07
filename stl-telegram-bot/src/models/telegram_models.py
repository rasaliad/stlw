"""
Modelos de datos para el bot de Telegram
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class TelegramUser:
    """Usuario del bot de Telegram"""
    id: Optional[int] = None
    telegram_user_id: int = 0
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    linked_user_id: Optional[int] = None
    verification_code: Optional[str] = None
    is_verified: bool = False
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None

@dataclass
class TelegramSubscription:
    """Suscripción a notificaciones"""
    id: Optional[int] = None
    user_id: int = 0
    notification_type: str = ""  # DELIVERY_NOTES, GOODS_RECEIPTS, ERRORS, ALL
    is_active: bool = True
    created_at: Optional[datetime] = None

@dataclass
class TelegramMessage:
    """Mensaje en cola de Telegram"""
    id: Optional[int] = None
    chat_id: int = 0
    message_type: str = ""
    message_text: str = ""
    priority: int = 1  # 1=normal, 2=alta, 3=crítica
    sent: bool = False
    created_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

@dataclass
class TelegramCommand:
    """Comando ejecutado por usuario"""
    id: Optional[int] = None
    user_id: int = 0
    command: str = ""
    parameters: Optional[str] = None
    response: Optional[str] = None
    executed_at: Optional[datetime] = None

@dataclass
class BotConfig:
    """Configuración del bot"""
    id: Optional[int] = None
    bot_token: str = ""
    bot_username: Optional[str] = None
    webhook_url: Optional[str] = None
    is_active: bool = True
    last_updated: Optional[datetime] = None