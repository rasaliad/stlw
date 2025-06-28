import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging
from contextlib import asynccontextmanager

from app.core.database import FirebirdConnection
from app.services.sap_client import sap_client
from app.models.sap_models import (
    ItemSTL, BusinessPartnerSTL, SalesOrderSTL, DispatchSTL,
    InventorySTL, TransferSTL, ServiceCallSTL, InvoiceSTL
)

logger = logging.getLogger(__name__)


class SAPSyncService:
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
                INSERT INTO SAP_SYNC_LOG (ENTITY_TYPE, ENTITY_ID, OPERATION, STATUS, 
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
                       BATCH_SIZE, MAX_RETRIES, FILTER_QUERY
                FROM SAP_SYNC_CONFIG 
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
                        'filter_query': row[5]
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
                UPDATE SAP_SYNC_CONFIG 
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
        """Sincroniza artículos desde SAP"""
        start_time = datetime.now()
        stats = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        try:
            config = await self.get_sync_config('ITEMS')
            if not config or not config['sync_enabled']:
                return stats
            
            # Obtener datos desde SAP
            filter_query = f"$top={config['batch_size']}"
            if config['last_sync_at']:
                # Filtrar por fecha de actualización
                filter_query += f"&$filter=UpdateDate gt datetime'{config['last_sync_at'].isoformat()}'"
            
            items_response = await sap_client.get_items(filter_query)
            if not items_response:
                return stats
            
            async with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                for item in items_response.value:
                    try:
                        # Verificar si existe
                        cursor.execute("SELECT ID FROM SAP_ITEMS WHERE CODE = ?", (item.Code,))
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Actualizar
                            sql = """
                            UPDATE SAP_ITEMS SET 
                                NAME = ?, FOREIGN_NAME = ?, ITEMS_GROUP_CODE = ?,
                                BAR_CODE = ?, VAT_LIABLE = ?, PURCHASE_ITEM = ?,
                                SALES_ITEM = ?, INVENTORY_ITEM = ?, QUANTITY_ON_STOCK = ?,
                                MIN_INVENTORY = ?, MAX_INVENTORY = ?, LAST_PURCHASE_PRICE = ?,
                                LAST_PURCHASE_DATE = ?, AVG_STD_PRICE = ?, DEFAULT_WAREHOUSE = ?,
                                UPDATED_AT = ?, SYNC_STATUS = 'SYNCED', LAST_SYNC_AT = ?
                            WHERE CODE = ?
                            """
                            cursor.execute(sql, (
                                item.Name, item.ForeignName, item.ItemsGroupCode,
                                item.BarCode, item.VatLiable, item.PurchaseItem,
                                item.SalesItem, item.InventoryItem, item.QuantityOnStock,
                                item.MinInventory, item.MaxInventory, item.LastPurchasePrice,
                                item.LastPurchaseDate, item.AvgStdPrice, item.DefaultWarehouse,
                                datetime.now(), datetime.now(), item.Code
                            ))
                            stats['updated'] += 1
                        else:
                            # Insertar
                            sql = """
                            INSERT INTO SAP_ITEMS (
                                CODE, NAME, FOREIGN_NAME, ITEMS_GROUP_CODE, BAR_CODE,
                                VAT_LIABLE, PURCHASE_ITEM, SALES_ITEM, INVENTORY_ITEM,
                                QUANTITY_ON_STOCK, MIN_INVENTORY, MAX_INVENTORY,
                                LAST_PURCHASE_PRICE, LAST_PURCHASE_DATE, AVG_STD_PRICE,
                                DEFAULT_WAREHOUSE, SYNC_STATUS, LAST_SYNC_AT
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SYNCED', ?)
                            """
                            cursor.execute(sql, (
                                item.Code, item.Name, item.ForeignName, item.ItemsGroupCode,
                                item.BarCode, item.VatLiable, item.PurchaseItem, item.SalesItem,
                                item.InventoryItem, item.QuantityOnStock, item.MinInventory,
                                item.MaxInventory, item.LastPurchasePrice, item.LastPurchaseDate,
                                item.AvgStdPrice, item.DefaultWarehouse, datetime.now()
                            ))
                            stats['inserted'] += 1
                        
                        await self.log_sync_operation('ITEMS', item.Code, 'SYNC', 'SUCCESS')
                        
                    except Exception as e:
                        logger.error(f"Error sincronizando item {item.Code}: {str(e)}")
                        await self.log_sync_operation('ITEMS', item.Code, 'SYNC', 'ERROR', str(e))
                        stats['errors'] += 1
                
                conn.commit()
            
            await self.update_sync_config('ITEMS')
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            await self.log_sync_operation('ITEMS', 'BATCH', 'SYNC', 'SUCCESS', 
                                        f"Procesados: {stats['inserted'] + stats['updated']}", processing_time)
            
        except Exception as e:
            logger.error(f"Error en sincronización de items: {str(e)}")
            await self.log_sync_operation('ITEMS', 'BATCH', 'SYNC', 'ERROR', str(e))
            stats['errors'] += 1
        
        return stats
    
    async def sync_business_partners(self) -> Dict[str, int]:
        """Sincroniza socios de negocio desde SAP"""
        start_time = datetime.now()
        stats = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        try:
            config = await self.get_sync_config('BUSINESS_PARTNERS')
            if not config or not config['sync_enabled']:
                return stats
            
            filter_query = f"$top={config['batch_size']}"
            bp_response = await sap_client.get_business_partners(filter_query)
            if not bp_response:
                return stats
            
            async with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                for bp in bp_response.value:
                    try:
                        cursor.execute("SELECT ID FROM SAP_BUSINESS_PARTNERS WHERE CARD_CODE = ?", (bp.CardCode,))
                        existing = cursor.fetchone()
                        
                        if existing:
                            sql = """
                            UPDATE SAP_BUSINESS_PARTNERS SET 
                                CARD_NAME = ?, CARD_TYPE = ?, GROUP_CODE = ?, ADDRESS = ?,
                                ZIP_CODE = ?, PHONE1 = ?, PHONE2 = ?, EMAIL_ADDRESS = ?,
                                CONTACT_PERSON = ?, CITY = ?, COUNTRY = ?, VAT_STATUS = ?,
                                CURRENCY = ?, CREDIT_LIMIT = ?, DISCOUNT_PERCENT = ?,
                                UPDATED_AT = ?, SYNC_STATUS = 'SYNCED', LAST_SYNC_AT = ?
                            WHERE CARD_CODE = ?
                            """
                            cursor.execute(sql, (
                                bp.CardName, bp.CardType, bp.GroupCode, bp.Address,
                                bp.ZipCode, bp.Phone1, bp.Phone2, bp.EmailAddress,
                                bp.ContactPerson, bp.City, bp.Country, bp.VatStatus,
                                bp.Currency, bp.CreditLimit, bp.DiscountPercent,
                                datetime.now(), datetime.now(), bp.CardCode
                            ))
                            stats['updated'] += 1
                        else:
                            sql = """
                            INSERT INTO SAP_BUSINESS_PARTNERS (
                                CARD_CODE, CARD_NAME, CARD_TYPE, GROUP_CODE, ADDRESS,
                                ZIP_CODE, PHONE1, PHONE2, EMAIL_ADDRESS, CONTACT_PERSON,
                                CITY, COUNTRY, VAT_STATUS, CURRENCY, CREDIT_LIMIT,
                                DISCOUNT_PERCENT, SYNC_STATUS, LAST_SYNC_AT
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SYNCED', ?)
                            """
                            cursor.execute(sql, (
                                bp.CardCode, bp.CardName, bp.CardType, bp.GroupCode,
                                bp.Address, bp.ZipCode, bp.Phone1, bp.Phone2,
                                bp.EmailAddress, bp.ContactPerson, bp.City, bp.Country,
                                bp.VatStatus, bp.Currency, bp.CreditLimit,
                                bp.DiscountPercent, datetime.now()
                            ))
                            stats['inserted'] += 1
                        
                        await self.log_sync_operation('BUSINESS_PARTNERS', bp.CardCode, 'SYNC', 'SUCCESS')
                        
                    except Exception as e:
                        logger.error(f"Error sincronizando BP {bp.CardCode}: {str(e)}")
                        await self.log_sync_operation('BUSINESS_PARTNERS', bp.CardCode, 'SYNC', 'ERROR', str(e))
                        stats['errors'] += 1
                
                conn.commit()
            
            await self.update_sync_config('BUSINESS_PARTNERS')
            
        except Exception as e:
            logger.error(f"Error en sincronización de business partners: {str(e)}")
            stats['errors'] += 1
        
        return stats
    
    async def sync_sales_orders(self) -> Dict[str, int]:
        """Sincroniza órdenes de venta desde SAP"""
        start_time = datetime.now()
        stats = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        try:
            config = await self.get_sync_config('SALES_ORDERS')
            if not config or not config['sync_enabled']:
                return stats
            
            filter_query = f"$top={config['batch_size']}"
            orders_response = await sap_client.get_sales_orders(filter_query)
            if not orders_response:
                return stats
            
            async with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                for order in orders_response.value:
                    try:
                        cursor.execute("SELECT ID FROM SAP_SALES_ORDERS WHERE DOC_ENTRY = ?", (order.DocEntry,))
                        existing = cursor.fetchone()
                        
                        if existing:
                            sql = """
                            UPDATE SAP_SALES_ORDERS SET 
                                DOC_NUM = ?, DOC_DATE = ?, DOC_DUE_DATE = ?, CARD_CODE = ?,
                                CARD_NAME = ?, NUM_AT_CARD = ?, DOC_TOTAL = ?, DOC_CURRENCY = ?,
                                COMMENTS = ?, SALES_PERSON_CODE = ?, CONFIRMED = ?, SERIES = ?,
                                TAX_DATE = ?, CREATION_DATE = ?, UPDATE_DATE = ?, VAT_SUM = ?,
                                DOC_TOTAL_FC = ?, DOC_TOTAL_SYS = ?, STATUS = ?,
                                UPDATED_AT = ?, SYNC_STATUS = 'SYNCED', LAST_SYNC_AT = ?
                            WHERE DOC_ENTRY = ?
                            """
                            cursor.execute(sql, (
                                order.DocNum, order.DocDate, order.DocDueDate, order.CardCode,
                                order.CardName, order.NumAtCard, order.DocTotal, order.DocCurrency,
                                order.Comments, order.SalesPersonCode, order.Confirmed, order.Series,
                                order.TaxDate, order.CreationDate, order.UpdateDate, order.VatSum,
                                order.DocTotalFc, order.DocTotalSys, 'OPEN',
                                datetime.now(), datetime.now(), order.DocEntry
                            ))
                            stats['updated'] += 1
                        else:
                            sql = """
                            INSERT INTO SAP_SALES_ORDERS (
                                DOC_ENTRY, DOC_NUM, DOC_DATE, DOC_DUE_DATE, CARD_CODE,
                                CARD_NAME, NUM_AT_CARD, DOC_TOTAL, DOC_CURRENCY, COMMENTS,
                                SALES_PERSON_CODE, CONFIRMED, SERIES, TAX_DATE, CREATION_DATE,
                                UPDATE_DATE, VAT_SUM, DOC_TOTAL_FC, DOC_TOTAL_SYS, STATUS,
                                SYNC_STATUS, LAST_SYNC_AT
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SYNCED', ?)
                            """
                            cursor.execute(sql, (
                                order.DocEntry, order.DocNum, order.DocDate, order.DocDueDate,
                                order.CardCode, order.CardName, order.NumAtCard, order.DocTotal,
                                order.DocCurrency, order.Comments, order.SalesPersonCode,
                                order.Confirmed, order.Series, order.TaxDate, order.CreationDate,
                                order.UpdateDate, order.VatSum, order.DocTotalFc,
                                order.DocTotalSys, 'OPEN', datetime.now()
                            ))
                            stats['inserted'] += 1
                        
                        await self.log_sync_operation('SALES_ORDERS', str(order.DocEntry), 'SYNC', 'SUCCESS')
                        
                    except Exception as e:
                        logger.error(f"Error sincronizando orden {order.DocEntry}: {str(e)}")
                        await self.log_sync_operation('SALES_ORDERS', str(order.DocEntry), 'SYNC', 'ERROR', str(e))
                        stats['errors'] += 1
                
                conn.commit()
            
            await self.update_sync_config('SALES_ORDERS')
            
        except Exception as e:
            logger.error(f"Error en sincronización de sales orders: {str(e)}")
            stats['errors'] += 1
        
        return stats
    
    async def sync_all_entities(self) -> Dict[str, Dict[str, int]]:
        """Sincroniza todas las entidades"""
        results = {}
        
        try:
            # Ejecutar sincronizaciones en paralelo
            tasks = [
                ('items', self.sync_items()),
                ('business_partners', self.sync_business_partners()),
                ('sales_orders', self.sync_sales_orders()),
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
                       SYNC_INTERVAL_MINUTES, BATCH_SIZE
                FROM SAP_SYNC_CONFIG
                ORDER BY ENTITY_TYPE
                """
                cursor.execute(sql)
                configs = cursor.fetchall()
                
                # Obtener logs recientes
                sql = """
                SELECT ENTITY_TYPE, STATUS, COUNT(*) as COUNT
                FROM SAP_SYNC_LOG
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
                            'batch_size': row[5]
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


# Instancia global del servicio de sincronización
sync_service = SAPSyncService()