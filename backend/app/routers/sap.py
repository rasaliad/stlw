from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import logging

from app.services.sap_sync_service import sync_service
from app.core.database import FirebirdConnection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sap", tags=["SAP Integration"])

db = FirebirdConnection()


@router.post("/sync/all")
async def sync_all_entities(background_tasks: BackgroundTasks):
    """Inicia sincronización de todas las entidades SAP"""
    try:
        background_tasks.add_task(sync_service.sync_all_entities)
        return {"message": "Sincronización iniciada en segundo plano"}
    except Exception as e:
        logger.error(f"Error iniciando sincronización: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error iniciando sincronización: {str(e)}")


@router.post("/sync/{entity_type}")
async def sync_entity(entity_type: str, background_tasks: BackgroundTasks):
    """Sincroniza una entidad específica"""
    try:
        if entity_type == "items":
            background_tasks.add_task(sync_service.sync_items)
        elif entity_type == "business_partners":
            background_tasks.add_task(sync_service.sync_business_partners)
        elif entity_type == "sales_orders":
            background_tasks.add_task(sync_service.sync_sales_orders)
        else:
            raise HTTPException(status_code=400, detail=f"Tipo de entidad no válido: {entity_type}")
        
        return {"message": f"Sincronización de {entity_type} iniciada"}
    except Exception as e:
        logger.error(f"Error sincronizando {entity_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sincronizando {entity_type}: {str(e)}")


@router.get("/sync/status")
async def get_sync_status():
    """Obtiene el estado de sincronización"""
    try:
        status = await sync_service.get_sync_status()
        return status
    except Exception as e:
        logger.error(f"Error obteniendo estado de sync: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")


@router.get("/items")
async def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    item_group: Optional[int] = None,
    active_only: bool = True
):
    """Obtiene artículos sincronizados desde SAP"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Construir query
            where_conditions = []
            params = []
            
            if search:
                where_conditions.append("(UPPER(NAME) LIKE ? OR UPPER(CODE) LIKE ?)")
                search_param = f"%{search.upper()}%"
                params.extend([search_param, search_param])
            
            if item_group:
                where_conditions.append("ITEMS_GROUP_CODE = ?")
                params.append(item_group)
            
            if active_only:
                where_conditions.append("(FROZEN IS NULL OR FROZEN = 'N')")
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Contar total
            count_sql = f"SELECT COUNT(*) FROM SAP_ITEMS {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()[0]
            
            # Obtener datos paginados
            sql = f"""
            SELECT ID, CODE, NAME, FOREIGN_NAME, ITEMS_GROUP_CODE, BAR_CODE,
                   QUANTITY_ON_STOCK, MIN_INVENTORY, MAX_INVENTORY, LAST_PURCHASE_PRICE,
                   LAST_PURCHASE_DATE, AVG_STD_PRICE, DEFAULT_WAREHOUSE, SALES_ITEM,
                   PURCHASE_ITEM, INVENTORY_ITEM, CREATED_AT, LAST_SYNC_AT
            FROM SAP_ITEMS {where_clause}
            ORDER BY NAME
            ROWS {skip + 1} TO {skip + limit}
            """
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            items = []
            for row in rows:
                items.append({
                    "id": row[0],
                    "code": row[1],
                    "name": row[2],
                    "foreign_name": row[3],
                    "items_group_code": row[4],
                    "bar_code": row[5],
                    "quantity_on_stock": float(row[6]) if row[6] else 0,
                    "min_inventory": float(row[7]) if row[7] else 0,
                    "max_inventory": float(row[8]) if row[8] else 0,
                    "last_purchase_price": float(row[9]) if row[9] else 0,
                    "last_purchase_date": row[10],
                    "avg_std_price": float(row[11]) if row[11] else 0,
                    "default_warehouse": row[12],
                    "sales_item": row[13] == 'Y',
                    "purchase_item": row[14] == 'Y',
                    "inventory_item": row[15] == 'Y',
                    "created_at": row[16],
                    "last_sync_at": row[17]
                })
            
            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
    except Exception as e:
        logger.error(f"Error obteniendo items: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo items: {str(e)}")


@router.get("/items/{item_code}")
async def get_item_by_code(item_code: str):
    """Obtiene un artículo específico por código"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            sql = """
            SELECT ID, CODE, NAME, FOREIGN_NAME, ITEMS_GROUP_CODE, BAR_CODE,
                   QUANTITY_ON_STOCK, MIN_INVENTORY, MAX_INVENTORY, LAST_PURCHASE_PRICE,
                   LAST_PURCHASE_DATE, AVG_STD_PRICE, DEFAULT_WAREHOUSE, SALES_ITEM,
                   PURCHASE_ITEM, INVENTORY_ITEM, VAT_LIABLE, MANAGE_SERIAL_NUMBERS,
                   MANAGE_BATCH_NUMBERS, FROZEN, CREATED_AT, LAST_SYNC_AT
            FROM SAP_ITEMS 
            WHERE CODE = ?
            """
            
            cursor.execute(sql, (item_code,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Artículo {item_code} no encontrado")
            
            return {
                "id": row[0],
                "code": row[1],
                "name": row[2],
                "foreign_name": row[3],
                "items_group_code": row[4],
                "bar_code": row[5],
                "quantity_on_stock": float(row[6]) if row[6] else 0,
                "min_inventory": float(row[7]) if row[7] else 0,
                "max_inventory": float(row[8]) if row[8] else 0,
                "last_purchase_price": float(row[9]) if row[9] else 0,
                "last_purchase_date": row[10],
                "avg_std_price": float(row[11]) if row[11] else 0,
                "default_warehouse": row[12],
                "sales_item": row[13] == 'Y',
                "purchase_item": row[14] == 'Y',
                "inventory_item": row[15] == 'Y',
                "vat_liable": row[16] == 'Y',
                "manage_serial_numbers": row[17] == 'Y',
                "manage_batch_numbers": row[18] == 'Y',
                "frozen": row[19] == 'Y',
                "created_at": row[20],
                "last_sync_at": row[21]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo item {item_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo item: {str(e)}")


@router.get("/business-partners")
async def get_business_partners(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    card_type: Optional[str] = None
):
    """Obtiene socios de negocio sincronizados desde SAP"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            where_conditions = []
            params = []
            
            if search:
                where_conditions.append("(UPPER(CARD_NAME) LIKE ? OR CARD_CODE LIKE ?)")
                search_param = f"%{search.upper()}%"
                params.extend([search_param, search_param])
            
            if card_type:
                where_conditions.append("CARD_TYPE = ?")
                params.append(card_type)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Contar total
            count_sql = f"SELECT COUNT(*) FROM SAP_BUSINESS_PARTNERS {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()[0]
            
            # Obtener datos
            sql = f"""
            SELECT ID, CARD_CODE, CARD_NAME, CARD_TYPE, PHONE1, EMAIL_ADDRESS,
                   CITY, COUNTRY, CREDIT_LIMIT, CURRENCY, CONTACT_PERSON,
                   CREATED_AT, LAST_SYNC_AT
            FROM SAP_BUSINESS_PARTNERS {where_clause}
            ORDER BY CARD_NAME
            ROWS {skip + 1} TO {skip + limit}
            """
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            partners = []
            for row in rows:
                partners.append({
                    "id": row[0],
                    "card_code": row[1],
                    "card_name": row[2],
                    "card_type": row[3],
                    "phone1": row[4],
                    "email_address": row[5],
                    "city": row[6],
                    "country": row[7],
                    "credit_limit": float(row[8]) if row[8] else 0,
                    "currency": row[9],
                    "contact_person": row[10],
                    "created_at": row[11],
                    "last_sync_at": row[12]
                })
            
            return {
                "business_partners": partners,
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
    except Exception as e:
        logger.error(f"Error obteniendo business partners: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo business partners: {str(e)}")


@router.get("/sales-orders")
async def get_sales_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    card_code: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    status: Optional[str] = None
):
    """Obtiene órdenes de venta sincronizadas desde SAP"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            where_conditions = []
            params = []
            
            if card_code:
                where_conditions.append("CARD_CODE = ?")
                params.append(card_code)
            
            if from_date:
                where_conditions.append("DOC_DATE >= ?")
                params.append(from_date)
            
            if to_date:
                where_conditions.append("DOC_DATE <= ?")
                params.append(to_date)
            
            if status:
                where_conditions.append("STATUS = ?")
                params.append(status)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Contar total
            count_sql = f"SELECT COUNT(*) FROM SAP_SALES_ORDERS {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()[0]
            
            # Obtener datos
            sql = f"""
            SELECT ID, DOC_ENTRY, DOC_NUM, DOC_DATE, DOC_DUE_DATE, CARD_CODE,
                   CARD_NAME, DOC_TOTAL, DOC_CURRENCY, VAT_SUM, STATUS,
                   CREATION_DATE, LAST_SYNC_AT
            FROM SAP_SALES_ORDERS {where_clause}
            ORDER BY DOC_DATE DESC
            ROWS {skip + 1} TO {skip + limit}
            """
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            orders = []
            for row in rows:
                orders.append({
                    "id": row[0],
                    "doc_entry": row[1],
                    "doc_num": row[2],
                    "doc_date": row[3],
                    "doc_due_date": row[4],
                    "card_code": row[5],
                    "card_name": row[6],
                    "doc_total": float(row[7]) if row[7] else 0,
                    "doc_currency": row[8],
                    "vat_sum": float(row[9]) if row[9] else 0,
                    "status": row[10],
                    "creation_date": row[11],
                    "last_sync_at": row[12]
                })
            
            return {
                "sales_orders": orders,
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
    except Exception as e:
        logger.error(f"Error obteniendo sales orders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo sales orders: {str(e)}")


@router.get("/inventory")
async def get_inventory(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    item_code: Optional[str] = None,
    warehouse: Optional[str] = None,
    low_stock_only: bool = False
):
    """Obtiene inventario sincronizado desde SAP"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            where_conditions = []
            params = []
            
            if item_code:
                where_conditions.append("ITEM_CODE = ?")
                params.append(item_code)
            
            if warehouse:
                where_conditions.append("WHS_CODE = ?")
                params.append(warehouse)
            
            if low_stock_only:
                where_conditions.append("ON_HAND < MIN_STOCK")
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Contar total
            count_sql = f"SELECT COUNT(*) FROM SAP_INVENTORY {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()[0]
            
            # Obtener datos
            sql = f"""
            SELECT ID, ITEM_CODE, WHS_CODE, ON_HAND, IS_COMMITED, ON_ORDER,
                   MIN_STOCK, MAX_STOCK, AVG_PRICE, STOCK_VALUE, LAST_PUR_PRC,
                   LAST_PUR_DAT, FROZEN, LAST_SYNC_AT
            FROM SAP_INVENTORY {where_clause}
            ORDER BY ITEM_CODE, WHS_CODE
            ROWS {skip + 1} TO {skip + limit}
            """
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            inventory = []
            for row in rows:
                inventory.append({
                    "id": row[0],
                    "item_code": row[1],
                    "warehouse_code": row[2],
                    "on_hand": float(row[3]) if row[3] else 0,
                    "is_committed": float(row[4]) if row[4] else 0,
                    "on_order": float(row[5]) if row[5] else 0,
                    "min_stock": float(row[6]) if row[6] else 0,
                    "max_stock": float(row[7]) if row[7] else 0,
                    "avg_price": float(row[8]) if row[8] else 0,
                    "stock_value": float(row[9]) if row[9] else 0,
                    "last_purchase_price": float(row[10]) if row[10] else 0,
                    "last_purchase_date": row[11],
                    "frozen": row[12] == 'Y',
                    "last_sync_at": row[13]
                })
            
            return {
                "inventory": inventory,
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
    except Exception as e:
        logger.error(f"Error obteniendo inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo inventory: {str(e)}")


@router.get("/analytics/summary")
async def get_analytics_summary():
    """Obtiene resumen analítico de datos SAP"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Contar entidades
            cursor.execute("SELECT COUNT(*) FROM SAP_ITEMS WHERE SALES_ITEM = 'Y'")
            total_items = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM SAP_BUSINESS_PARTNERS")
            total_partners = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM SAP_SALES_ORDERS WHERE STATUS = 'OPEN'")
            open_orders = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(DOC_TOTAL) FROM SAP_SALES_ORDERS WHERE STATUS = 'OPEN'")
            open_orders_value = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM SAP_INVENTORY WHERE ON_HAND < MIN_STOCK AND MIN_STOCK > 0")
            low_stock_items = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(STOCK_VALUE) FROM SAP_INVENTORY")
            total_inventory_value = cursor.fetchone()[0] or 0
            
            # Top clientes por ventas
            cursor.execute("""
                SELECT CARD_CODE, CARD_NAME, SUM(DOC_TOTAL) as TOTAL_SALES
                FROM SAP_SALES_ORDERS 
                WHERE DOC_DATE >= DATEADD(month, -3, CURRENT_DATE)
                GROUP BY CARD_CODE, CARD_NAME
                ORDER BY TOTAL_SALES DESC
                ROWS 1 TO 5
            """)
            top_customers = [
                {"card_code": row[0], "card_name": row[1], "total_sales": float(row[2])}
                for row in cursor.fetchall()
            ]
            
            return {
                "summary": {
                    "total_items": total_items,
                    "total_partners": total_partners,
                    "open_orders": open_orders,
                    "open_orders_value": float(open_orders_value),
                    "low_stock_items": low_stock_items,
                    "total_inventory_value": float(total_inventory_value)
                },
                "top_customers": top_customers
            }
            
    except Exception as e:
        logger.error(f"Error obteniendo analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo analytics: {str(e)}")