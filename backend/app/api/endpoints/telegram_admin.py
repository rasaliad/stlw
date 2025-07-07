"""
Endpoints de administración para el bot de Telegram
"""
import random
import string
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.core.database import FirebirdConnection
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()
security = HTTPBearer()
db = FirebirdConnection()


@router.get("/telegram-users")
async def get_telegram_users(current_user: User = Depends(get_current_active_user)):
    """Obtiene lista de usuarios de Telegram"""
    if current_user.role != "ADMINISTRADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver usuarios de Telegram"
        )
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ID, TELEGRAM_ID, TELEGRAM_USERNAME, TELEGRAM_FIRST_NAME, 
                       TELEGRAM_LAST_NAME, USER_ID, IS_ACTIVE, IS_VERIFIED, 
                       VERIFICATION_CODE, CREATED_AT
                FROM STL_TELEGRAM_USERS 
                ORDER BY CREATED_AT DESC
            """)
            
            columns = [desc[0].lower() for desc in cursor.description]
            rows = cursor.fetchall()
            
            users = []
            for row in rows:
                user_dict = dict(zip(columns, row))
                users.append({
                    'id': user_dict['id'],
                    'telegram_id': user_dict['telegram_id'],
                    'telegram_username': user_dict['telegram_username'],
                    'telegram_first_name': user_dict['telegram_first_name'],
                    'telegram_last_name': user_dict['telegram_last_name'],
                    'user_id': user_dict['user_id'],
                    'is_active': bool(user_dict['is_active']),
                    'is_verified': bool(user_dict['is_verified']),
                    'verification_code': user_dict['verification_code'],
                    'created_at': user_dict['created_at'],
                    'full_name': f"{user_dict['telegram_first_name'] or ''} {user_dict['telegram_last_name'] or ''}".strip()
                })
            
            return {
                'users': users,
                'total': len(users)
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo usuarios: {str(e)}"
        )


@router.post("/telegram-users/{user_id}/generate-code")
async def generate_verification_code(
    user_id: int, 
    current_user: User = Depends(get_current_active_user)
):
    """Genera código de verificación para un usuario de Telegram"""
    if current_user.role != "ADMINISTRADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden generar códigos"
        )
    
    try:
        # Generar código aleatorio de 6 caracteres
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que el usuario existe
            cursor.execute("SELECT ID, TELEGRAM_USERNAME, TELEGRAM_FIRST_NAME FROM STL_TELEGRAM_USERS WHERE ID = ?", (user_id,))
            user_info = cursor.fetchone()
            
            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # Actualizar código de verificación
            cursor.execute("""
                UPDATE STL_TELEGRAM_USERS 
                SET VERIFICATION_CODE = ? 
                WHERE ID = ?
            """, (code, user_id))
            
            conn.commit()
            
            return {
                'message': 'Código generado exitosamente',
                'code': code,
                'user_info': {
                    'id': user_info[0],
                    'telegram_username': user_info[1],
                    'telegram_first_name': user_info[2]
                },
                'instructions': f'El usuario debe usar el comando: /vincular {code}'
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando código: {str(e)}"
        )


@router.post("/telegram-users/{user_id}/activate")
async def activate_telegram_user(
    user_id: int, 
    current_user: User = Depends(get_current_active_user)
):
    """Activa un usuario de Telegram después de la verificación"""
    if current_user.role != "ADMINISTRADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden activar usuarios"
        )
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que el usuario existe y está verificado
            cursor.execute("""
                SELECT ID, TELEGRAM_USERNAME, IS_VERIFIED, IS_ACTIVE 
                FROM STL_TELEGRAM_USERS 
                WHERE ID = ?
            """, (user_id,))
            
            user_info = cursor.fetchone()
            
            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            if not user_info[2]:  # IS_VERIFIED
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Usuario debe estar verificado antes de activar"
                )
            
            # Activar usuario
            cursor.execute("""
                UPDATE STL_TELEGRAM_USERS 
                SET IS_ACTIVE = 1, VERIFIED_AT = ? 
                WHERE ID = ?
            """, (datetime.now(), user_id))
            
            conn.commit()
            
            return {
                'message': 'Usuario activado exitosamente',
                'user_info': {
                    'id': user_info[0],
                    'telegram_username': user_info[1],
                    'is_active': True
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activando usuario: {str(e)}"
        )


@router.post("/telegram-users/{user_id}/deactivate")
async def deactivate_telegram_user(
    user_id: int, 
    current_user: User = Depends(get_current_active_user)
):
    """Desactiva un usuario de Telegram"""
    if current_user.role != "ADMINISTRADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden desactivar usuarios"
        )
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE STL_TELEGRAM_USERS 
                SET IS_ACTIVE = 0 
                WHERE ID = ?
            """, (user_id,))
            
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            return {'message': 'Usuario desactivado exitosamente'}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error desactivando usuario: {str(e)}"
        )


@router.get("/telegram-queue")
async def get_telegram_queue(current_user: User = Depends(get_current_active_user)):
    """Obtiene mensajes en cola de Telegram"""
    if current_user.role != "ADMINISTRADOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver la cola"
        )
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ID, CHAT_ID, MESSAGE_TYPE, MESSAGE_TEXT, PRIORITY, 
                       STATUS, CREATED_AT, SENT_AT, ERROR_MESSAGE
                FROM STL_TELEGRAM_QUEUE 
                ORDER BY CREATED_AT DESC
                ROWS 100
            """)
            
            columns = [desc[0].lower() for desc in cursor.description]
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                msg_dict = dict(zip(columns, row))
                messages.append({
                    'id': msg_dict['id'],
                    'chat_id': msg_dict['chat_id'],
                    'message_type': msg_dict['message_type'],
                    'message_text': msg_dict['message_text'][:100] + '...' if len(msg_dict['message_text'] or '') > 100 else msg_dict['message_text'],
                    'priority': msg_dict['priority'],
                    'status': msg_dict['status'],
                    'created_at': msg_dict['created_at'],
                    'sent_at': msg_dict['sent_at'],
                    'error_message': msg_dict['error_message']
                })
            
            # Contar por estado
            cursor.execute("""
                SELECT STATUS, COUNT(*) 
                FROM STL_TELEGRAM_QUEUE 
                GROUP BY STATUS
            """)
            
            status_counts = dict(cursor.fetchall())
            
            return {
                'messages': messages,
                'total': len(messages),
                'status_counts': status_counts
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo cola: {str(e)}"
        )