import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging
import hashlib
import json
from contextlib import asynccontextmanager

from app.core.database import FirebirdConnection
from app.services.sap_stl_client import sap_stl_client
from app.models.sap_stl_models import (
    ItemSTL, DispatchSTL, GoodsReceiptSTL, DispatchLineSTL, GoodsReceiptLineSTL
)
from app.services.sap_delivery_service import sap_delivery_service

logger = logging.getLogger(__name__)

class OptimizedSyncService:
    def __init__(self):
        self.db = FirebirdConnection()
    
    def _calculate_hash(self, data: dict) -> str:
        """Calcula hash MD5 de los datos para detectar cambios"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _parse_iso_date(self, iso_string_or_datetime) -> Optional[datetime]:
        """Convierte string ISO o datetime a datetime para Firebird"""
        if not iso_string_or_datetime:
            return None
        
        # Si ya es datetime, retornarlo directamente
        if isinstance(iso_string_or_datetime, datetime):
            return iso_string_or_datetime
        
        # Si es string, parsearlo
        if isinstance(iso_string_or_datetime, str):
            try:
                # Manejar diferentes formatos ISO
                if 'T' in iso_string_or_datetime:
                    if iso_string_or_datetime.endswith('Z'):
                        # Formato: 2025-07-02T00:00:00Z
                        return datetime.strptime(iso_string_or_datetime, '%Y-%m-%dT%H:%M:%SZ')
                    else:
                        # Formato: 2025-07-02T00:00:00
                        return datetime.strptime(iso_string_or_datetime, '%Y-%m-%dT%H:%M:%S')
                else:
                    # Formato: 2025-07-02
                    return datetime.strptime(iso_string_or_datetime, '%Y-%m-%d')
            except ValueError as e:
                logger.error(f"Error parseando fecha ISO '{iso_string_or_datetime}': {str(e)}")
                return None
        
        logger.warning(f"Tipo de fecha no esperado: {type(iso_string_or_datetime)}")
        return None
    
    def _item_to_dict(self, item: ItemSTL) -> dict:
        """Convierte item a diccionario para comparación"""
        return {
            'descripcionProducto': item.descripcionProducto,
            'codigoProductoERP': item.codigoProductoERP,
            'codigoFamilia': item.codigoFamilia,
            'nombreFamilia': item.nombreFamilia,
            'diasVencimiento': item.diasVencimiento,
            'codigoUMB': item.codigoUMB,
            'descripcionUMB': item.descripcionUMB,
            'codigoFormaEmbalaje': item.codigoFormaEmbalaje,
            'nombreFormaEmbalaje': item.nombreFormaEmbalaje
        }
    
    def _dispatch_to_dict(self, dispatch: DispatchSTL) -> dict:
        """Convierte despacho a diccionario para comparación"""
        return {
            'numeroBusqueda': dispatch.numeroBusqueda,
            'fechaCreacion': dispatch.fechaCreacion,
            'fechaPicking': dispatch.fechaPicking,
            'fechaCarga': dispatch.fechaCarga,
            'codigoCliente': dispatch.codigoCliente,
            'nombreCliente': dispatch.nombreCliente
        }
    
    def _receipt_to_dict(self, receipt: GoodsReceiptSTL) -> dict:
        """Convierte recepción a diccionario para comparación"""
        return {
            'numeroBusqueda': receipt.numeroBusqueda,
            'fecha': receipt.fecha,
            'codigoSuplidor': receipt.codigoSuplidor,
            'nombreSuplidor': receipt.nombreSuplidor
        }
    
    async def sync_items_optimized(self) -> Dict[str, int]:
        """Sincroniza items solo si hay cambios reales"""
        start_time = datetime.now()
        stats = {'inserted': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        try:
            logger.info("Iniciando sincronización OPTIMIZADA de items")
            items = await sap_stl_client.get_items()
            if not items:
                logger.warning("No se obtuvieron items de la API")
                return stats
            
            logger.info(f"Obtenidos {len(items)} items de la API")
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                for item in items:
                    try:
                        # Verificar si existe y obtener hash actual
                        cursor.execute("""
                            SELECT ID, DATA_HASH FROM STL_ITEMS 
                            WHERE CODIGO_PRODUCTO = ?
                        """, (item.codigoProducto,))
                        existing = cursor.fetchone()
                        
                        # Calcular hash de datos nuevos
                        item_data = self._item_to_dict(item)
                        new_hash = self._calculate_hash(item_data)
                        
                        if existing:
                            existing_hash = existing[1] if existing[1] else ""
                            
                            if new_hash != existing_hash:
                                # Hay cambios reales - actualizar
                                sql = """
                                UPDATE STL_ITEMS SET 
                                    DESCRIPCION_PRODUCTO = ?, CODIGO_PRODUCTO_ERP = ?,
                                    CODIGO_FAMILIA = ?, NOMBRE_FAMILIA = ?, DIAS_VENCIMIENTO = ?,
                                    CODIGO_UMB = ?, DESCRIPCION_UMB = ?, CODIGO_FORMA_EMBALAJE = ?,
                                    NOMBRE_FORMA_EMBALAJE = ?, UPDATED_AT = ?, SYNC_STATUS = 'SYNCED', 
                                    LAST_SYNC_AT = ?, DATA_HASH = ?
                                WHERE CODIGO_PRODUCTO = ?
                                """
                                cursor.execute(sql, (
                                    item.descripcionProducto, item.codigoProductoERP, item.codigoFamilia,
                                    item.nombreFamilia, item.diasVencimiento, item.codigoUMB,
                                    item.descripcionUMB, item.codigoFormaEmbalaje, item.nombreFormaEmbalaje,
                                    datetime.now(), datetime.now(), new_hash, item.codigoProducto
                                ))
                                stats['updated'] += 1
                                logger.debug(f"Item actualizado: {item.codigoProducto}")
                            else:
                                # Sin cambios - NO tocar el registro para evitar triggers
                                stats['skipped'] += 1
                                logger.debug(f"Item sin cambios: {item.codigoProducto}")
                        else:
                            # Nuevo item - insertar
                            sql = """
                            INSERT INTO STL_ITEMS (
                                CODIGO_PRODUCTO, DESCRIPCION_PRODUCTO, CODIGO_PRODUCTO_ERP,
                                CODIGO_FAMILIA, NOMBRE_FAMILIA, DIAS_VENCIMIENTO, CODIGO_UMB,
                                DESCRIPCION_UMB, CODIGO_FORMA_EMBALAJE, NOMBRE_FORMA_EMBALAJE,
                                SYNC_STATUS, LAST_SYNC_AT, DATA_HASH
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SYNCED', ?, ?)
                            """
                            cursor.execute(sql, (
                                item.codigoProducto, item.descripcionProducto, item.codigoProductoERP,
                                item.codigoFamilia, item.nombreFamilia, item.diasVencimiento,
                                item.codigoUMB, item.descripcionUMB, item.codigoFormaEmbalaje,
                                item.nombreFormaEmbalaje, datetime.now(), new_hash
                            ))
                            stats['inserted'] += 1
                            logger.debug(f"Item insertado: {item.codigoProducto}")
                            
                    except Exception as e:
                        logger.error(f"Error procesando item {item.codigoProducto}: {str(e)}")
                        stats['errors'] += 1
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error en sincronización de items: {str(e)}")
            stats['errors'] += 1
        
        duration = datetime.now() - start_time
        logger.info(f"Sincronización items completada en {duration.total_seconds():.2f}s - Stats: {stats}")
        return stats

    async def sync_dispatches_optimized(self, tipo_despacho: Optional[int] = None) -> Dict[str, int]:
        """Sincroniza despachos y líneas solo si hay cambios reales"""
        start_time = datetime.now()
        stats = {'inserted': 0, 'updated': 0, 'skipped': 0, 'lines_inserted': 0, 'lines_updated': 0, 'lines_skipped': 0, 'errors': 0}
        
        try:
            logger.info("Iniciando sincronización OPTIMIZADA de despachos")
            dispatches = await sap_stl_client.get_orders(tipo_despacho)
            if not dispatches:
                return stats
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                for dispatch in dispatches:
                    try:
                        cursor.execute("""
                            SELECT ID, DATA_HASH FROM STL_DISPATCHES 
                            WHERE NUMERO_BUSQUEDA = ? AND TIPO_DESPACHO = ? AND NUMERO_DESPACHO = ?
                        """, (dispatch.numeroBusqueda, dispatch.tipoDespacho, dispatch.numeroDespacho))
                        existing = cursor.fetchone()
                        
                        dispatch_data = self._dispatch_to_dict(dispatch)
                        new_hash = self._calculate_hash(dispatch_data)
                        
                        if existing:
                            dispatch_id = existing[0]
                            existing_hash = existing[1] if existing[1] else ""
                            
                            if new_hash != existing_hash:
                                # Actualizar despacho
                                sql = """
                                UPDATE STL_DISPATCHES SET 
                                    NUMERO_BUSQUEDA = ?, FECHA_CREACION = ?, FECHA_PICKING = ?,
                                    FECHA_CARGA = ?, CODIGO_CLIENTE = ?, NOMBRE_CLIENTE = ?,
                                    UPDATED_AT = ?, SYNC_STATUS = 'SYNCED', LAST_SYNC_AT = ?, DATA_HASH = ?
                                WHERE ID = ?
                                """
                                # Convertir fechas ISO string a datetime para Firebird
                                fecha_creacion = self._parse_iso_date(dispatch.fechaCreacion) if dispatch.fechaCreacion else None
                                fecha_picking = self._parse_iso_date(dispatch.fechaPicking) if dispatch.fechaPicking else None
                                fecha_carga = self._parse_iso_date(dispatch.fechaCarga) if dispatch.fechaCarga else None
                                
                                cursor.execute(sql, (
                                    dispatch.numeroBusqueda, fecha_creacion, fecha_picking,
                                    fecha_carga, dispatch.codigoCliente, dispatch.nombreCliente,
                                    datetime.now(), datetime.now(), new_hash, dispatch_id
                                ))
                                stats['updated'] += 1
                            else:
                                # Sin cambios - NO tocar el registro para evitar triggers
                                stats['skipped'] += 1
                        else:
                            # Insertar nuevo despacho
                            sql = """
                            INSERT INTO STL_DISPATCHES (
                                NUMERO_DESPACHO, NUMERO_BUSQUEDA, FECHA_CREACION, FECHA_PICKING,
                                FECHA_CARGA, CODIGO_CLIENTE, NOMBRE_CLIENTE, TIPO_DESPACHO,
                                SYNC_STATUS, LAST_SYNC_AT, DATA_HASH
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'SYNCED', ?, ?)
                            """
                            # Convertir fechas ISO string a datetime para Firebird
                            fecha_creacion = self._parse_iso_date(dispatch.fechaCreacion) if dispatch.fechaCreacion else None
                            fecha_picking = self._parse_iso_date(dispatch.fechaPicking) if dispatch.fechaPicking else None
                            fecha_carga = self._parse_iso_date(dispatch.fechaCarga) if dispatch.fechaCarga else None
                            
                            cursor.execute(sql, (
                                dispatch.numeroDespacho, dispatch.numeroBusqueda, fecha_creacion,
                                fecha_picking, fecha_carga, dispatch.codigoCliente,
                                dispatch.nombreCliente, dispatch.tipoDespacho, datetime.now(), new_hash
                            ))
                            cursor.execute("SELECT GEN_ID(GEN_STL_DISPATCHES_ID, 0) FROM RDB$DATABASE")
                            dispatch_id = cursor.fetchone()[0]
                            stats['inserted'] += 1
                        
                        # Optimizar líneas de despacho
                        if dispatch.lines:
                            await self._sync_dispatch_lines_optimized(cursor, dispatch_id, dispatch.lines, stats)
                            
                    except Exception as e:
                        logger.error(f"Error procesando despacho {dispatch.numeroBusqueda}: {str(e)}")
                        logger.error(f"Datos del despacho: fechaCreacion={dispatch.fechaCreacion}, fechaPicking={dispatch.fechaPicking}, fechaCarga={dispatch.fechaCarga}")
                        stats['errors'] += 1
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error en sincronización de despachos: {str(e)}")
            stats['errors'] += 1
        
        duration = datetime.now() - start_time
        logger.info(f"Sincronización despachos completada en {duration.total_seconds():.2f}s - Stats: {stats}")
        return stats
    
    async def _sync_dispatch_lines_optimized(self, cursor, dispatch_id: int, lines: List[DispatchLineSTL], stats: Dict):
        """Sincroniza líneas de despacho de forma optimizada"""
        # Obtener líneas existentes con hash
        cursor.execute("""
            SELECT ID, LINE_NUM, DATA_HASH FROM STL_DISPATCH_LINES 
            WHERE DISPATCH_ID = ? ORDER BY LINE_NUM
        """, (dispatch_id,))
        existing_lines = {row[1]: (row[0], row[2]) for row in cursor.fetchall()}
        
        processed_lines = set()
        
        for line in lines:
            line_data = {
                'codigoProducto': line.codigoProducto,
                'nombreProducto': line.nombreProducto,
                'almacen': line.almacen,
                'cantidadUMB': line.cantidadUMB,
                'uoMCode': line.uoMCode,
                'uoMEntry': line.uoMEntry
            }
            new_hash = self._calculate_hash(line_data)
            processed_lines.add(line.lineNum)
            
            if line.lineNum in existing_lines:
                line_id, existing_hash = existing_lines[line.lineNum]
                
                if new_hash != existing_hash:
                    # Actualizar línea
                    sql = """
                    UPDATE STL_DISPATCH_LINES SET 
                        CODIGO_PRODUCTO = ?, NOMBRE_PRODUCTO = ?, ALMACEN = ?,
                        CANTIDAD_UMB = ?, UOM_CODE = ?, UOM_ENTRY = ?, DATA_HASH = ?
                    WHERE ID = ?
                    """
                    cursor.execute(sql, (
                        line.codigoProducto, line.nombreProducto, line.almacen,
                        line.cantidadUMB, line.uoMCode, line.uoMEntry, new_hash, line_id
                    ))
                    stats['lines_updated'] += 1
                else:
                    stats['lines_skipped'] += 1
            else:
                # Insertar nueva línea
                sql = """
                INSERT INTO STL_DISPATCH_LINES (
                    DISPATCH_ID, CODIGO_PRODUCTO, NOMBRE_PRODUCTO, ALMACEN,
                    CANTIDAD_UMB, LINE_NUM, UOM_CODE, UOM_ENTRY, DATA_HASH
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(sql, (
                    dispatch_id, line.codigoProducto, line.nombreProducto,
                    line.almacen, line.cantidadUMB, line.lineNum,
                    line.uoMCode, line.uoMEntry, new_hash
                ))
                stats['lines_inserted'] += 1
        
        # Eliminar líneas que ya no existen en el API
        for line_num, (line_id, _) in existing_lines.items():
            if line_num not in processed_lines:
                cursor.execute("DELETE FROM STL_DISPATCH_LINES WHERE ID = ?", (line_id,))
    
    async def sync_receipts_optimized(self, tipo_recepcion: Optional[int] = None) -> Dict[str, int]:
        """Sincroniza recepciones de forma optimizada"""
        start_time = datetime.now()
        stats = {'inserted': 0, 'updated': 0, 'skipped': 0, 'lines_inserted': 0, 'lines_updated': 0, 'lines_skipped': 0, 'errors': 0}
        
        try:
            logger.info("Iniciando sincronización OPTIMIZADA de recepciones")
            receipts = await sap_stl_client.get_goods_receipts(tipo_recepcion)
            if not receipts:
                logger.warning("No se obtuvieron recepciones del API SAP-STL")
                return stats
            
            logger.info(f"Obtenidas {len(receipts)} recepciones del API SAP-STL")
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                for receipt in receipts:
                    try:
                        cursor.execute("""
                            SELECT ID, DATA_HASH FROM STL_GOODS_RECEIPTS 
                            WHERE NUMERO_BUSQUEDA = ? AND TIPO_RECEPCION = ? AND NUMERO_DOCUMENTO = ?
                        """, (receipt.numeroBusqueda, receipt.tipoRecepcion, receipt.numeroDocumento))
                        existing = cursor.fetchone()
                        
                        receipt_data = self._receipt_to_dict(receipt)
                        new_hash = self._calculate_hash(receipt_data)
                        
                        if existing:
                            receipt_id = existing[0]
                            existing_hash = existing[1] if existing[1] else ""
                            
                            if new_hash != existing_hash:
                                sql = """
                                UPDATE STL_GOODS_RECEIPTS SET 
                                    NUMERO_BUSQUEDA = ?, FECHA = ?, CODIGO_SUPLIDOR = ?,
                                    NOMBRE_SUPLIDOR = ?, UPDATED_AT = ?, SYNC_STATUS = 'SYNCED', 
                                    LAST_SYNC_AT = ?, DATA_HASH = ?
                                WHERE ID = ?
                                """
                                # Convertir fecha ISO string a datetime para Firebird
                                fecha_receipt = self._parse_iso_date(receipt.fecha) if receipt.fecha else None
                                
                                cursor.execute(sql, (
                                    receipt.numeroBusqueda, fecha_receipt, receipt.codigoSuplidor,
                                    receipt.nombreSuplidor, datetime.now(), datetime.now(), 
                                    new_hash, receipt_id
                                ))
                                stats['updated'] += 1
                            else:
                                # Sin cambios - NO tocar el registro para evitar triggers
                                stats['skipped'] += 1
                        else:
                            sql = """
                            INSERT INTO STL_GOODS_RECEIPTS (
                                NUMERO_DOCUMENTO, NUMERO_BUSQUEDA, FECHA, TIPO_RECEPCION,
                                CODIGO_SUPLIDOR, NOMBRE_SUPLIDOR, SYNC_STATUS, LAST_SYNC_AT, DATA_HASH
                            ) VALUES (?, ?, ?, ?, ?, ?, 'SYNCED', ?, ?)
                            """
                            # Convertir fecha ISO string a datetime para Firebird
                            fecha_receipt = self._parse_iso_date(receipt.fecha) if receipt.fecha else None
                            
                            cursor.execute(sql, (
                                receipt.numeroDocumento, receipt.numeroBusqueda, fecha_receipt,
                                receipt.tipoRecepcion, receipt.codigoSuplidor, receipt.nombreSuplidor,
                                datetime.now(), new_hash
                            ))
                            cursor.execute("SELECT GEN_ID(GEN_STL_GOODS_RECEIPTS_ID, 0) FROM RDB$DATABASE")
                            receipt_id = cursor.fetchone()[0]
                            stats['inserted'] += 1
                        
                        if receipt.lines:
                            await self._sync_receipt_lines_optimized(cursor, receipt_id, receipt.lines, stats)
                            
                    except Exception as e:
                        logger.error(f"Error procesando recepción {receipt.numeroBusqueda}: {str(e)}")
                        stats['errors'] += 1
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error en sincronización de recepciones: {str(e)}")
            stats['errors'] += 1
        
        duration = datetime.now() - start_time
        logger.info(f"Sincronización recepciones completada en {duration.total_seconds():.2f}s - Stats: {stats}")
        return stats
    
    async def _sync_receipt_lines_optimized(self, cursor, receipt_id: int, lines: List[GoodsReceiptLineSTL], stats: Dict):
        """Sincroniza líneas de recepción de forma optimizada"""
        cursor.execute("""
            SELECT ID, LINE_NUM, DATA_HASH FROM STL_GOODS_RECEIPT_LINES 
            WHERE RECEIPT_ID = ? ORDER BY LINE_NUM
        """, (receipt_id,))
        existing_lines = {row[1]: (row[0], row[2]) for row in cursor.fetchall()}
        
        processed_lines = set()
        
        for line in lines:
            line_data = {
                'codigoProducto': line.codigoProducto,
                'nombreProducto': line.nombreProducto,
                'cantidad': line.cantidad,
                'uoMCode': line.uoMCode
            }
            new_hash = self._calculate_hash(line_data)
            processed_lines.add(line.lineNum)
            
            if line.lineNum in existing_lines:
                line_id, existing_hash = existing_lines[line.lineNum]
                
                if new_hash != existing_hash:
                    sql = """
                    UPDATE STL_GOODS_RECEIPT_LINES SET 
                        CODIGO_PRODUCTO = ?, NOMBRE_PRODUCTO = ?, CANTIDAD = ?,
                        UOM_CODE = ?, DATA_HASH = ?
                    WHERE ID = ?
                    """
                    cursor.execute(sql, (
                        line.codigoProducto, line.nombreProducto, line.cantidad,
                        line.uoMCode, new_hash, line_id
                    ))
                    stats['lines_updated'] += 1
                else:
                    stats['lines_skipped'] += 1
            else:
                sql = """
                INSERT INTO STL_GOODS_RECEIPT_LINES (
                    RECEIPT_ID, CODIGO_PRODUCTO, NOMBRE_PRODUCTO, CANTIDAD,
                    LINE_NUM, UOM_CODE, DATA_HASH
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(sql, (
                    receipt_id, line.codigoProducto, line.nombreProducto,
                    line.cantidad, line.lineNum, line.uoMCode, new_hash
                ))
                stats['lines_inserted'] += 1
        
        # Eliminar líneas que ya no existen
        for line_num, (line_id, _) in existing_lines.items():
            if line_num not in processed_lines:
                cursor.execute("DELETE FROM STL_GOODS_RECEIPT_LINES WHERE ID = ?", (line_id,))

    async def sync_procurement_orders_optimized(self, tipo_recepcion: Optional[int] = None) -> Dict[str, int]:
        """Sincroniza órdenes de compra (ProcurementOrders) - usa mismas tablas que recepciones"""
        start_time = datetime.now()
        stats = {'inserted': 0, 'updated': 0, 'skipped': 0, 'lines_inserted': 0, 'lines_updated': 0, 'lines_skipped': 0, 'errors': 0}
        
        try:
            logger.info("Iniciando sincronización OPTIMIZADA de órdenes de compra (ProcurementOrders)")
            # Usa get_procurement_orders en lugar de get_goods_receipts
            orders = await sap_stl_client.get_procurement_orders(tipo_recepcion)
            if not orders:
                logger.warning("No se obtuvieron órdenes de compra del API SAP-STL")
                return stats
            
            logger.info(f"Obtenidas {len(orders)} órdenes de compra del API SAP-STL")
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                for order in orders:
                    try:
                        # Usa las mismas tablas que GOODS_RECEIPTS
                        cursor.execute("""
                            SELECT ID, DATA_HASH FROM STL_GOODS_RECEIPTS 
                            WHERE NUMERO_BUSQUEDA = ? AND TIPO_RECEPCION = ? AND NUMERO_DOCUMENTO = ?
                        """, (order.numeroBusqueda, order.tipoRecepcion, order.numeroDocumento))
                        existing = cursor.fetchone()
                        
                        order_data = self._receipt_to_dict(order)
                        new_hash = self._calculate_hash(order_data)
                        
                        if existing:
                            order_id = existing[0]
                            existing_hash = existing[1] if existing[1] else ""
                            
                            if new_hash != existing_hash:
                                sql = """
                                UPDATE STL_GOODS_RECEIPTS SET 
                                    NUMERO_BUSQUEDA = ?, FECHA = ?, CODIGO_SUPLIDOR = ?,
                                    NOMBRE_SUPLIDOR = ?, UPDATED_AT = ?, SYNC_STATUS = 'SYNCED', 
                                    LAST_SYNC_AT = ?, DATA_HASH = ?
                                WHERE ID = ?
                                """
                                # Convertir fecha ISO string a datetime para Firebird
                                fecha_order = self._parse_iso_date(order.fecha) if order.fecha else None
                                
                                cursor.execute(sql, (
                                    order.numeroBusqueda, fecha_order, order.codigoSuplidor,
                                    order.nombreSuplidor, datetime.now(), datetime.now(), 
                                    new_hash, order_id
                                ))
                                stats['updated'] += 1
                                logger.debug(f"Orden de compra actualizada: {order.numeroBusqueda}")
                            else:
                                stats['skipped'] += 1
                                logger.debug(f"Orden de compra sin cambios: {order.numeroBusqueda}")
                        else:
                            sql = """
                            INSERT INTO STL_GOODS_RECEIPTS (
                                NUMERO_DOCUMENTO, NUMERO_BUSQUEDA, FECHA, TIPO_RECEPCION,
                                CODIGO_SUPLIDOR, NOMBRE_SUPLIDOR, SYNC_STATUS, LAST_SYNC_AT, DATA_HASH
                            ) VALUES (?, ?, ?, ?, ?, ?, 'SYNCED', ?, ?)
                            """
                            # Convertir fecha ISO string a datetime para Firebird
                            fecha_order = self._parse_iso_date(order.fecha) if order.fecha else None
                            
                            cursor.execute(sql, (
                                order.numeroDocumento, order.numeroBusqueda, fecha_order,
                                order.tipoRecepcion, order.codigoSuplidor, order.nombreSuplidor,
                                datetime.now(), new_hash
                            ))
                            cursor.execute("SELECT GEN_ID(GEN_STL_GOODS_RECEIPTS_ID, 0) FROM RDB$DATABASE")
                            order_id = cursor.fetchone()[0]
                            stats['inserted'] += 1
                            logger.debug(f"Orden de compra insertada: {order.numeroBusqueda}")
                        
                        if order.lines:
                            await self._sync_receipt_lines_optimized(cursor, order_id, order.lines, stats)
                            
                    except Exception as e:
                        logger.error(f"Error procesando orden de compra {order.numeroBusqueda}: {str(e)}")
                        stats['errors'] += 1
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error en sincronización de órdenes de compra: {str(e)}")
            stats['errors'] += 1
        
        duration = datetime.now() - start_time
        logger.info(f"Sincronización órdenes de compra completada en {duration.total_seconds():.2f}s - Stats: {stats}")
        return stats

# Singleton
optimized_sync_service = OptimizedSyncService()