"""
Servicio para sincronización manual de despachos desde SAP
"""
import logging
from typing import Dict, Any
from datetime import datetime

from app.core.database import FirebirdConnection
from app.models.manual_dispatch_models import DispatchManual, DispatchSyncResponse

logger = logging.getLogger(__name__)


class ManualDispatchService:
    """Servicio para sincronizar manualmente despachos desde SAP"""
    
    def __init__(self):
        self.db = FirebirdConnection()
    
    def _parse_date(self, date_str: str) -> str:
        """Extrae solo la fecha YYYY-MM-DD de una fecha ISO"""
        if not date_str:
            return None
        return date_str[:10]
    
    def sync_dispatch_from_json(self, dispatch_data: DispatchManual) -> DispatchSyncResponse:
        """
        Sincroniza un despacho desde JSON insertando en STL_DISPATCHES y STL_DISPATCH_LINES
        """
        logger.info(f"Iniciando sincronización manual - Despacho: {dispatch_data.numeroDespacho}, Tipo: {dispatch_data.tipoDespacho}")
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si el despacho ya existe
                cursor.execute("""
                    SELECT ID FROM STL_DISPATCHES 
                    WHERE NUMERO_BUSQUEDA = ? AND TIPO_DESPACHO = ? AND NUMERO_DESPACHO = ?
                """, (dispatch_data.numeroBusqueda, dispatch_data.tipoDespacho, dispatch_data.numeroDespacho))
                
                existing = cursor.fetchone()
                if existing:
                    return DispatchSyncResponse(
                        success=False,
                        message=f"El despacho {dispatch_data.numeroDespacho} tipo {dispatch_data.tipoDespacho} ya existe",
                        dispatch_id=existing[0]
                    )
                
                # Insertar cabecera del despacho
                cursor.execute("""
                    INSERT INTO STL_DISPATCHES (
                        NUMERO_DESPACHO,
                        NUMERO_BUSQUEDA,
                        FECHA_CREACION,
                        FECHA_PICKING,
                        FECHA_CARGA,
                        CODIGO_CLIENTE,
                        NOMBRE_CLIENTE,
                        TIPO_DESPACHO,
                        SYNC_STATUS,
                        LAST_SYNC_AT
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    dispatch_data.numeroDespacho,
                    dispatch_data.numeroBusqueda,
                    self._parse_date(dispatch_data.fechaCreacion),
                    self._parse_date(dispatch_data.fechaPicking),
                    self._parse_date(dispatch_data.fechaCarga) if dispatch_data.fechaCarga else None,
                    dispatch_data.codigoCliente,
                    dispatch_data.nombreCliente,
                    dispatch_data.tipoDespacho,
                    'SYNCED',
                    datetime.now()
                ))
                
                # Obtener el ID del despacho recién insertado
                cursor.execute("""
                    SELECT ID FROM STL_DISPATCHES 
                    WHERE NUMERO_BUSQUEDA = ? AND TIPO_DESPACHO = ? AND NUMERO_DESPACHO = ?
                """, (dispatch_data.numeroBusqueda, dispatch_data.tipoDespacho, dispatch_data.numeroDespacho))
                
                dispatch_id = cursor.fetchone()[0]
                
                # Insertar líneas del despacho
                lines_inserted = 0
                for line in dispatch_data.lines:
                    cursor.execute("""
                        INSERT INTO STL_DISPATCH_LINES (
                            DISPATCH_ID,
                            CODIGO_PRODUCTO,
                            NOMBRE_PRODUCTO,
                            ALMACEN,
                            CANTIDAD_UMB,
                            LINE_NUM,
                            UOM_CODE,
                            UOM_ENTRY
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        dispatch_id,
                        line.codigoProducto,
                        line.nombreProducto,
                        line.almacen,
                        line.cantidadUMB,
                        line.lineNum,
                        line.uoMCode,
                        line.uoMEntry
                    ))
                    lines_inserted += 1
                
                # Confirmar transacción
                conn.commit()
                
                logger.info(f"✅ Despacho {dispatch_data.numeroDespacho} sincronizado exitosamente. ID: {dispatch_id}, Líneas: {lines_inserted}")
                
                return DispatchSyncResponse(
                    success=True,
                    message=f"Despacho {dispatch_data.numeroDespacho} sincronizado exitosamente",
                    dispatch_id=dispatch_id,
                    lines_inserted=lines_inserted,
                    details={
                        "numeroDespacho": dispatch_data.numeroDespacho,
                        "tipoDespacho": dispatch_data.tipoDespacho,
                        "cliente": dispatch_data.nombreCliente,
                        "fechaCreacion": self._parse_date(dispatch_data.fechaCreacion),
                        "lineas": lines_inserted
                    }
                )
                
        except Exception as e:
            logger.error(f"Error sincronizando despacho {dispatch_data.numeroDespacho}: {str(e)}")
            return DispatchSyncResponse(
                success=False,
                message=f"Error al sincronizar: {str(e)}",
                dispatch_id=None,
                lines_inserted=0
            )


# Instancia global del servicio
manual_dispatch_service = ManualDispatchService()