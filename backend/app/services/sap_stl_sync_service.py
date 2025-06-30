import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging
from contextlib import asynccontextmanager

from app.core.database import FirebirdConnection
from app.services.sap_stl_client import sap_stl_client
from app.models.sap_stl_models import (
    ItemSTL, DispatchSTL, GoodsReceiptSTL, DispatchLineSTL, GoodsReceiptLineSTL
)

logger = logging.getLogger(__name__)


class SAPSTLSyncService:
    def __init__(self):
        self.db = FirebirdConnection()
        
    @asynccontextmanager
    async def get_db_connection(self):
        """Context manager para conexiones de base de datos"""
        conn = None
        try:
            conn = self.db.get_connection()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error en conexión DB: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    async def log_sync_operation(self, entity_type: str, entity_id: str, operation: str, 
                                status: str, error_message: str = None, processing_time: int = None):
        """Registra operaciones de sincronización"""
        try:
            async with self.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = """
                INSERT INTO STL_SYNC_LOG (ENTITY_TYPE, ENTITY_ID, OPERATION, STATUS, 
                                        ERROR_MESSAGE, PROCESSING_TIME, SYNC_DATE)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(sql, (entity_type, entity_id, operation, status, 
                               error_message, processing_time, datetime.now()))
                conn.commit()
        except Exception as e:
            logger.error(f"Error registrando sync log: {str(e)}")
    
    async def get_sync_config(self, entity_type: str) -> Optional[Dict[str, Any]]:
        """Obtiene configuración de sincronización para una entidad"""
        try:
            async with self.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = """
                SELECT SYNC_ENABLED, SYNC_INTERVAL_MINUTES, LAST_SYNC_AT, 
                       BATCH_SIZE, MAX_RETRIES, API_ENDPOINT
                FROM STL_SYNC_CONFIG 
                WHERE ENTITY_TYPE = ?
                """
                cursor.execute(sql, (entity_type,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'sync_enabled': row[0] == 'Y',
                        'sync_interval_minutes': row[1],
                        'last_sync_at': row[2],
                        'batch_size': row[3],
                        'max_retries': row[4],
                        'api_endpoint': row[5]
                    }
                return None
        except Exception as e:
            logger.error(f"Error obteniendo configuración sync: {str(e)}")
            return None
    
    async def update_sync_config(self, entity_type: str, last_sync_at: datetime = None):
        """Actualiza la configuración de sincronización"""
        try:
            async with self.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = """
                UPDATE STL_SYNC_CONFIG 
                SET LAST_SYNC_AT = ?, NEXT_SYNC_AT = ?, UPDATED_AT = ?
                WHERE ENTITY_TYPE = ?
                """
                now = datetime.now()
                config = await self.get_sync_config(entity_type)
                next_sync = now + timedelta(minutes=config['sync_interval_minutes']) if config else now + timedelta(hours=1)
                
                cursor.execute(sql, (last_sync_at or now, next_sync, now, entity_type))
                conn.commit()
        except Exception as e:
            logger.error(f"Error actualizando configuración sync: {str(e)}")
    
    async def sync_items(self) -> Dict[str, int]:
        """Sincroniza artículos desde API STL"""
        start_time = datetime.now()
        stats = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        try:
            # Obtener datos desde API STL
            logger.info("Iniciando sincronización de items")
            items = await sap_stl_client.get_items()
            if not items:
                logger.warning("No se obtuvieron items de la API")
                return stats
            
            logger.info(f"Obtenidos {len(items)} items de la API")
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                for item in items:
                    try:
                        # Verificar si existe
                        cursor.execute("SELECT ID FROM STL_ITEMS WHERE CODIGO_PRODUCTO = ?", (item.codigoProducto,))
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Actualizar
                            sql = """
                            UPDATE STL_ITEMS SET 
                                DESCRIPCION_PRODUCTO = ?, CODIGO_PRODUCTO_ERP = ?,
                                CODIGO_FAMILIA = ?, NOMBRE_FAMILIA = ?, DIAS_VENCIMIENTO = ?,
                                CODIGO_UMB = ?, DESCRIPCION_UMB = ?, CODIGO_FORMA_EMBALAJE = ?,
                                NOMBRE_FORMA_EMBALAJE = ?, UPDATED_AT = ?, SYNC_STATUS = 'SYNCED', 
                                LAST_SYNC_AT = ?
                            WHERE CODIGO_PRODUCTO = ?
                            """
                            cursor.execute(sql, (
                                item.descripcionProducto, item.codigoProductoERP, item.codigoFamilia,
                                item.nombreFamilia, item.diasVencimiento, item.codigoUMB,
                                item.descripcionUMB, item.codigoFormaEmbalaje, item.nombreFormaEmbalaje,
                                datetime.now(), datetime.now(), item.codigoProducto
                            ))
                            stats['updated'] += 1
                        else:
                            # Insertar
                            sql = """
                            INSERT INTO STL_ITEMS (
                                CODIGO_PRODUCTO, DESCRIPCION_PRODUCTO, CODIGO_PRODUCTO_ERP,
                                CODIGO_FAMILIA, NOMBRE_FAMILIA, DIAS_VENCIMIENTO, CODIGO_UMB,
                                DESCRIPCION_UMB, CODIGO_FORMA_EMBALAJE, NOMBRE_FORMA_EMBALAJE,
                                SYNC_STATUS, LAST_SYNC_AT
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SYNCED', ?)
                            """
                            cursor.execute(sql, (
                                item.codigoProducto, item.descripcionProducto, item.codigoProductoERP,
                                item.codigoFamilia, item.nombreFamilia, item.diasVencimiento,
                                item.codigoUMB, item.descripcionUMB, item.codigoFormaEmbalaje,
                                item.nombreFormaEmbalaje, datetime.now()
                            ))
                            stats['inserted'] += 1
                        
                        
                    except Exception as e:
                        logger.error(f"Error sincronizando item {item.codigoProducto}: {str(e)}")
                        stats['errors'] += 1
                
                conn.commit()
                logger.info(f"Sincronización completada. Insertados: {stats['inserted']}, Actualizados: {stats['updated']}, Errores: {stats['errors']}")
            
        except Exception as e:
            logger.error(f"Error en sincronización de items: {str(e)}", exc_info=True)
            stats['errors'] += 1
        
        return stats
    
    async def sync_dispatches(self, tipo_despacho: Optional[int] = None) -> Dict[str, int]:
        """Sincroniza despachos desde API STL"""
        start_time = datetime.now()
        stats = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        try:
            # Obtener datos desde API STL
            logger.info("Iniciando sincronización de despachos")
            dispatches = await sap_stl_client.get_orders(tipo_despacho)
            if not dispatches:
                logger.warning("No se obtuvieron despachos de la API")
                return stats
            
            logger.info(f"Obtenidos {len(dispatches)} despachos de la API")
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                for dispatch in dispatches:
                    try:
                        # Verificar si existe
                        cursor.execute("SELECT ID FROM STL_DISPATCHES WHERE NUMERO_DESPACHO = ? AND TIPO_DESPACHO = ?", 
                                     (dispatch.numeroDespacho, dispatch.tipoDespacho))
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Actualizar
                            sql = """
                            UPDATE STL_DISPATCHES SET 
                                NUMERO_BUSQUEDA = ?, FECHA_CREACION = ?, FECHA_PICKING = ?,
                                FECHA_CARGA = ?, CODIGO_CLIENTE = ?, NOMBRE_CLIENTE = ?,
                                UPDATED_AT = ?, SYNC_STATUS = 'SYNCED', LAST_SYNC_AT = ?
                            WHERE NUMERO_DESPACHO = ? AND TIPO_DESPACHO = ?
                            """
                            cursor.execute(sql, (
                                dispatch.numeroBusqueda, dispatch.fechaCreacion, dispatch.fechaPicking,
                                dispatch.fechaCarga, dispatch.codigoCliente, dispatch.nombreCliente,
                                datetime.now(), datetime.now(), dispatch.numeroDespacho, dispatch.tipoDespacho
                            ))
                            dispatch_id = existing[0]
                            stats['updated'] += 1
                        else:
                            # Insertar
                            sql = """
                            INSERT INTO STL_DISPATCHES (
                                NUMERO_DESPACHO, NUMERO_BUSQUEDA, FECHA_CREACION, FECHA_PICKING,
                                FECHA_CARGA, CODIGO_CLIENTE, NOMBRE_CLIENTE, TIPO_DESPACHO,
                                SYNC_STATUS, LAST_SYNC_AT
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'SYNCED', ?)
                            """
                            cursor.execute(sql, (
                                dispatch.numeroDespacho, dispatch.numeroBusqueda, dispatch.fechaCreacion,
                                dispatch.fechaPicking, dispatch.fechaCarga, dispatch.codigoCliente,
                                dispatch.nombreCliente, dispatch.tipoDespacho, datetime.now()
                            ))
                            # Obtener ID del registro insertado
                            cursor.execute("SELECT GEN_ID(GEN_STL_DISPATCHES_ID, 0) FROM RDB$DATABASE")
                            dispatch_id = cursor.fetchone()[0]
                            stats['inserted'] += 1
                        
                        # Insertar/actualizar líneas de despacho
                        if dispatch.lines:
                            # Eliminar líneas existentes
                            cursor.execute("DELETE FROM STL_DISPATCH_LINES WHERE DISPATCH_ID = ?", (dispatch_id,))
                            
                            # Insertar nuevas líneas
                            for line in dispatch.lines:
                                sql = """
                                INSERT INTO STL_DISPATCH_LINES (
                                    DISPATCH_ID, CODIGO_PRODUCTO, NOMBRE_PRODUCTO, ALMACEN,
                                    CANTIDAD_UMB, LINE_NUM, UOM_CODE, UOM_ENTRY
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """
                                cursor.execute(sql, (
                                    dispatch_id, line.codigoProducto, line.nombreProducto,
                                    line.almacen, line.cantidadUMB, line.lineNum,
                                    line.uoMCode, line.uoMEntry
                                ))
                        
                        await self.log_sync_operation('DISPATCHES', str(dispatch.numeroDespacho), 'FETCH', 'SUCCESS')
                        
                    except Exception as e:
                        logger.error(f"Error sincronizando dispatch {dispatch.numeroDespacho}: {str(e)}")
                        await self.log_sync_operation('DISPATCHES', str(dispatch.numeroDespacho), 'FETCH', 'ERROR', str(e))
                        stats['errors'] += 1
                
                conn.commit()
            
            await self.update_sync_config('DISPATCHES')
            
        except Exception as e:
            logger.error(f"Error en sincronización de dispatches: {str(e)}")
            stats['errors'] += 1
        
        return stats
    
    async def sync_goods_receipts(self, tipo_recepcion: Optional[int] = None) -> Dict[str, int]:
        """Sincroniza recepciones de mercancía desde API STL"""
        start_time = datetime.now()
        stats = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        try:
            # Obtener datos desde API STL
            logger.info("Iniciando sincronización de recepciones de mercancía")
            receipts = await sap_stl_client.get_goods_receipts(tipo_recepcion)
            if not receipts:
                logger.warning("No se obtuvieron recepciones de la API")
                return stats
            
            logger.info(f"Obtenidas {len(receipts)} recepciones de la API")
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                for receipt in receipts:
                    try:
                        # Verificar si existe
                        cursor.execute("SELECT ID FROM STL_GOODS_RECEIPTS WHERE NUMERO_DOCUMENTO = ?", 
                                     (receipt.numeroDocumento,))
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Actualizar
                            sql = """
                            UPDATE STL_GOODS_RECEIPTS SET 
                                NUMERO_BUSQUEDA = ?, FECHA = ?, TIPO_RECEPCION = ?,
                                CODIGO_SUPLIDOR = ?, NOMBRE_SUPLIDOR = ?,
                                UPDATED_AT = ?, SYNC_STATUS = 'SYNCED', LAST_SYNC_AT = ?
                            WHERE NUMERO_DOCUMENTO = ?
                            """
                            cursor.execute(sql, (
                                receipt.numeroBusqueda, receipt.fecha, receipt.tipoRecepcion,
                                receipt.codigoSuplidor, receipt.nombreSuplidor,
                                datetime.now(), datetime.now(), receipt.numeroDocumento
                            ))
                            receipt_id = existing[0]
                            stats['updated'] += 1
                        else:
                            # Insertar
                            sql = """
                            INSERT INTO STL_GOODS_RECEIPTS (
                                NUMERO_DOCUMENTO, NUMERO_BUSQUEDA, FECHA, TIPO_RECEPCION,
                                CODIGO_SUPLIDOR, NOMBRE_SUPLIDOR, SYNC_STATUS, LAST_SYNC_AT
                            ) VALUES (?, ?, ?, ?, ?, ?, 'SYNCED', ?)
                            """
                            cursor.execute(sql, (
                                receipt.numeroDocumento, receipt.numeroBusqueda, receipt.fecha,
                                receipt.tipoRecepcion, receipt.codigoSuplidor, receipt.nombreSuplidor,
                                datetime.now()
                            ))
                            # Obtener ID del registro insertado
                            cursor.execute("SELECT GEN_ID(GEN_STL_GOODS_RECEIPTS_ID, 0) FROM RDB$DATABASE")
                            receipt_id = cursor.fetchone()[0]
                            stats['inserted'] += 1
                        
                        # Insertar/actualizar líneas de recepción
                        if receipt.lines:
                            # Eliminar líneas existentes
                            cursor.execute("DELETE FROM STL_GOODS_RECEIPT_LINES WHERE RECEIPT_ID = ?", (receipt_id,))
                            
                            # Insertar nuevas líneas
                            for line in receipt.lines:
                                sql = """
                                INSERT INTO STL_GOODS_RECEIPT_LINES (
                                    RECEIPT_ID, CODIGO_PRODUCTO, NOMBRE_PRODUCTO, CODIGO_FAMILIA,
                                    NOMBRE_FAMILIA, CANTIDAD, UNIDAD_DE_MEDIDA_UMB, LINE_NUM,
                                    UOM_ENTRY, UOM_CODE, DIAS_VENCIMIENTO
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """
                                cursor.execute(sql, (
                                    receipt_id, line.codigoProducto, line.nombreProducto,
                                    line.codigoFamilia, line.nombreFamilia, line.cantidad,
                                    line.unidadDeMedidaUMB, line.lineNum, line.uoMEntry,
                                    line.uoMCode, line.diasVencimiento
                                ))
                        
                        await self.log_sync_operation('GOODS_RECEIPTS', str(receipt.numeroDocumento), 'FETCH', 'SUCCESS')
                        
                    except Exception as e:
                        logger.error(f"Error sincronizando receipt {receipt.numeroDocumento}: {str(e)}")
                        await self.log_sync_operation('GOODS_RECEIPTS', str(receipt.numeroDocumento), 'FETCH', 'ERROR', str(e))
                        stats['errors'] += 1
                
                conn.commit()
            
            await self.update_sync_config('GOODS_RECEIPTS')
            
        except Exception as e:
            logger.error(f"Error en sincronización de goods receipts: {str(e)}")
            stats['errors'] += 1
        
        return stats
    
    async def sync_all_entities(self) -> Dict[str, Dict[str, int]]:
        """Sincroniza todas las entidades"""
        results = {}
        
        try:
            # Ejecutar sincronizaciones
            tasks = [
                ('items', self.sync_items()),
                ('dispatches', self.sync_dispatches()),
                ('goods_receipts', self.sync_goods_receipts()),
            ]
            
            for entity_name, task in tasks:
                try:
                    results[entity_name] = await task
                    logger.info(f"Sync {entity_name} completado: {results[entity_name]}")
                except Exception as e:
                    logger.error(f"Error en sync {entity_name}: {str(e)}")
                    results[entity_name] = {'inserted': 0, 'updated': 0, 'errors': 1}
            
        except Exception as e:
            logger.error(f"Error en sincronización general: {str(e)}")
        
        return results
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """Obtiene el estado de sincronización"""
        try:
            async with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener configuraciones
                sql = """
                SELECT ENTITY_TYPE, SYNC_ENABLED, LAST_SYNC_AT, NEXT_SYNC_AT,
                       SYNC_INTERVAL_MINUTES, BATCH_SIZE, API_ENDPOINT
                FROM STL_SYNC_CONFIG
                ORDER BY ENTITY_TYPE
                """
                cursor.execute(sql)
                configs = cursor.fetchall()
                
                # Obtener logs recientes
                sql = """
                SELECT ENTITY_TYPE, STATUS, COUNT(*) as COUNT
                FROM STL_SYNC_LOG
                WHERE SYNC_DATE >= ?
                GROUP BY ENTITY_TYPE, STATUS
                ORDER BY ENTITY_TYPE, STATUS
                """
                last_24h = datetime.now() - timedelta(hours=24)
                cursor.execute(sql, (last_24h,))
                logs = cursor.fetchall()
                
                return {
                    'configurations': [
                        {
                            'entity_type': row[0],
                            'sync_enabled': row[1] == 'Y',
                            'last_sync_at': row[2],
                            'next_sync_at': row[3],
                            'interval_minutes': row[4],
                            'batch_size': row[5],
                            'api_endpoint': row[6]
                        }
                        for row in configs
                    ],
                    'recent_logs': [
                        {
                            'entity_type': row[0],
                            'status': row[1],
                            'count': row[2]
                        }
                        for row in logs
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo estado de sync: {str(e)}")
            return {'configurations': [], 'recent_logs': []}


# Instancia global del servicio de sincronización STL
stl_sync_service = SAPSTLSyncService()