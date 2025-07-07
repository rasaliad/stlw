"""
Conexión a base de datos Firebird
"""
import logging
import fdb
import os
from contextlib import contextmanager
from typing import Any, Dict, Optional

from ..config.settings import settings

logger = logging.getLogger(__name__)

class FirebirdConnection:
    """Manejador de conexión a Firebird"""
    
    def __init__(self):
        self.host = settings.DB_HOST
        self.port = settings.DB_PORT
        self.database = settings.DB_PATH
        self.user = settings.DB_USER
        self.password = settings.DB_PASSWORD
        
        # Configurar librería Firebird client
        self._setup_firebird_client()
        
    def _setup_firebird_client(self):
        """Configura la librería de Firebird para Docker"""
        # En Docker, las librerías ya están instaladas en ubicaciones estándar
        # Configurar LD_LIBRARY_PATH si no está definido
        if 'LD_LIBRARY_PATH' not in os.environ:
            os.environ['LD_LIBRARY_PATH'] = '/usr/lib/x86_64-linux-gnu'
            logger.info("Configurado LD_LIBRARY_PATH para Docker")
        else:
            logger.info(f"LD_LIBRARY_PATH ya configurado: {os.environ['LD_LIBRARY_PATH']}")
            
        # En desarrollo (fuera de Docker), buscar fbclient.dll
        if not os.path.exists('/usr/lib/x86_64-linux-gnu/libfbclient.so.2'):
            possible_locations = [
                '/home/rasaliad/app/stlw/stl-telegram-bot/fbclient.dll',
                '/home/rasaliad/app/stlw/backend/fbclient.dll',
                './fbclient.dll',
                '../backend/fbclient.dll'
            ]
            
            for location in possible_locations:
                if os.path.exists(location):
                    os.environ['FIREBIRD_CLIENT_LIB'] = location
                    logger.info(f"Modo desarrollo - Usando librería: {location}")
                    break
            else:
                logger.warning("Modo desarrollo - No se encontró fbclient.dll")
        
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones a la base de datos"""
        conn = None
        try:
            # Construir DSN
            dsn = f"{self.host}/{self.port}:{self.database}"
            
            # Conectar
            conn = fdb.connect(
                dsn=dsn,
                user=self.user,
                password=self.password,
                charset='UTF8'
            )
            
            yield conn
            
        except Exception as e:
            logger.error(f"Error conectando a base de datos: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
                
    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM RDB$DATABASE")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Test de conexión falló: {e}")
            return False

# Instancia global
db = FirebirdConnection()