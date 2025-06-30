from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import logging

from app.services.optimized_sync_service import optimized_sync_service
from app.services.sap_stl_client import sap_stl_client
from app.services.background_sync_service import background_sync_service
from app.models.sap_stl_models import (
    DispatchSTL, GoodsReceiptSTL, InventoryGoodsIssueSTL, 
    InventoryGoodsReceiptSTL, InventoryTransfer
)
from app.core.database import FirebirdConnection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sap-stl", tags=["SAP-STL Integration"])

db = FirebirdConnection()


@router.post("/sync-now")
async def sync_now():
    """Sincronización inmediata con resultados"""
    try:
        # Sincronizar todas las entidades con optimización
        items_results = await optimized_sync_service.sync_items_optimized()
        dispatches_results = await optimized_sync_service.sync_dispatches_optimized()
        receipts_results = await optimized_sync_service.sync_receipts_optimized()
        
        # Contar datos en BD
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM STL_ITEMS")
            total_items = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM STL_DISPATCHES")
            total_dispatches = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM STL_GOODS_RECEIPTS")
            total_receipts = cursor.fetchone()[0]
            
        return {
            "sync_results": {
                "items": items_results,
                "dispatches": dispatches_results,
                "goods_receipts": receipts_results
            },
            "totals_in_db": {
                "items": total_items,
                "dispatches": total_dispatches,
                "goods_receipts": total_receipts
            },
            "api_url": sap_stl_client.base_url,
            "using_mock_data": sap_stl_client.use_mock_data
        }
    except Exception as e:
        return {"error": str(e)}


@router.post("/config/mock-mode")
async def toggle_mock_mode(enabled: bool):
    """Activa o desactiva el modo simulación"""
    try:
        sap_stl_client.use_mock_data = enabled
        return {
            "message": f"Modo simulación {'activado' if enabled else 'desactivado'}",
            "mock_mode_enabled": enabled,
            "api_url": sap_stl_client.base_url
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/config/status")
async def get_config_status():
    """Obtiene el estado actual de la configuración"""
    try:
        return {
            "mock_mode_enabled": sap_stl_client.use_mock_data,
            "api_url": sap_stl_client.base_url,
            "username": sap_stl_client.username,
            "has_token": bool(sap_stl_client.token)
        }
    except Exception as e:
        return {"error": str(e)}


@router.delete("/data/clean")
async def clean_data(entity_type: Optional[str] = None):
    """Limpia datos SAP-STL de la base de datos
    
    Args:
        entity_type: Tipo específico para limpiar (items, dispatches, goods_receipts)
                    Si no se especifica, limpia TODO
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            counts_before = {}
            counts_after = {}
            
            # Obtener conteos antes
            cursor.execute("SELECT COUNT(*) FROM STL_ITEMS")
            counts_before['items'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM STL_DISPATCHES")
            counts_before['dispatches'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM STL_GOODS_RECEIPTS")
            counts_before['goods_receipts'] = cursor.fetchone()[0]
            
            if entity_type == "items":
                cursor.execute("DELETE FROM STL_ITEMS")
            elif entity_type == "dispatches":
                cursor.execute("DELETE FROM STL_DISPATCH_LINES")
                cursor.execute("DELETE FROM STL_DISPATCHES")
            elif entity_type == "goods_receipts":
                cursor.execute("DELETE FROM STL_GOODS_RECEIPT_LINES")
                cursor.execute("DELETE FROM STL_GOODS_RECEIPTS")
            else:
                # Limpiar TODO
                cursor.execute("DELETE FROM STL_GOODS_RECEIPT_LINES")
                cursor.execute("DELETE FROM STL_GOODS_RECEIPTS")
                cursor.execute("DELETE FROM STL_DISPATCH_LINES")
                cursor.execute("DELETE FROM STL_DISPATCHES")
                cursor.execute("DELETE FROM STL_ITEMS")
            
            conn.commit()
            
            # Obtener conteos después
            cursor.execute("SELECT COUNT(*) FROM STL_ITEMS")
            counts_after['items'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM STL_DISPATCHES")
            counts_after['dispatches'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM STL_GOODS_RECEIPTS")
            counts_after['goods_receipts'] = cursor.fetchone()[0]
            
            return {
                "message": f"Datos {'de ' + entity_type if entity_type else 'todos'} limpiados exitosamente",
                "deleted": {
                    "items": counts_before['items'] - counts_after['items'],
                    "dispatches": counts_before['dispatches'] - counts_after['dispatches'],
                    "goods_receipts": counts_before['goods_receipts'] - counts_after['goods_receipts']
                },
                "remaining": counts_after
            }
            
    except Exception as e:
        logger.error(f"Error limpiando datos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error limpiando datos: {str(e)}")


@router.get("/test-connection")
async def test_connection():
    """Test básico de conectividad con API SAP-STL"""
    try:
        # Probar login
        success = await sap_stl_client.login()
        
        if success:
            # Intentar obtener items
            items = await sap_stl_client.get_items()
            return {
                "status": "success",
                "message": "Conectado a API SAP-STL",
                "token_obtained": bool(sap_stl_client.token),
                "items_retrieved": len(items) if items else 0,
                "base_url": sap_stl_client.base_url
            }
        else:
            return {
                "status": "error",
                "message": "Error de autenticación",
                "base_url": sap_stl_client.base_url
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "base_url": sap_stl_client.base_url
        }


@router.post("/sync/all")
async def sync_all_entities(background_tasks: BackgroundTasks):
    """Inicia sincronización de todas las entidades SAP-STL"""
    try:
        async def sync_all():
            await optimized_sync_service.sync_items_optimized()
            await optimized_sync_service.sync_dispatches_optimized()
            await optimized_sync_service.sync_receipts_optimized()
        background_tasks.add_task(sync_all)
        return {"message": "Sincronización iniciada en segundo plano"}
    except Exception as e:
        logger.error(f"Error iniciando sincronización: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error iniciando sincronización: {str(e)}")


@router.post("/sync/{entity_type}")
async def sync_entity(entity_type: str, background_tasks: BackgroundTasks, tipo_filtro: Optional[int] = None):
    """Sincroniza una entidad específica"""
    try:
        if entity_type == "items":
            background_tasks.add_task(optimized_sync_service.sync_items_optimized)
        elif entity_type == "dispatches":
            background_tasks.add_task(optimized_sync_service.sync_dispatches_optimized, tipo_filtro)
        elif entity_type == "goods_receipts":
            background_tasks.add_task(optimized_sync_service.sync_receipts_optimized, tipo_filtro)
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
        status = await stl_sync_service.get_sync_status()
        return status
    except Exception as e:
        logger.error(f"Error obteniendo estado de sync: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")


@router.get("/sync/background/status")
async def get_background_sync_status():
    """Obtiene el estado de sincronización automática en background"""
    try:
        status = background_sync_service.get_job_status()
        return status
    except Exception as e:
        logger.error(f"Error obteniendo estado de background sync: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")


@router.get("/items")
async def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    codigo_familia: Optional[int] = None
):
    """Obtiene artículos sincronizados desde SAP-STL"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Construir query
            where_conditions = []
            params = []
            
            if search:
                where_conditions.append("(UPPER(DESCRIPCION_PRODUCTO) LIKE ? OR UPPER(CODIGO_PRODUCTO) LIKE ?)")
                search_param = f"%{search.upper()}%"
                params.extend([search_param, search_param])
            
            if codigo_familia:
                where_conditions.append("CODIGO_FAMILIA = ?")
                params.append(codigo_familia)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Contar total
            count_sql = f"SELECT COUNT(*) FROM STL_ITEMS {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()[0]
            
            # Obtener datos paginados
            sql = f"""
            SELECT ID, CODIGO_PRODUCTO, DESCRIPCION_PRODUCTO, CODIGO_PRODUCTO_ERP,
                   CODIGO_FAMILIA, NOMBRE_FAMILIA, DIAS_VENCIMIENTO, CODIGO_UMB,
                   DESCRIPCION_UMB, CODIGO_FORMA_EMBALAJE, NOMBRE_FORMA_EMBALAJE,
                   CREATED_AT, LAST_SYNC_AT
            FROM STL_ITEMS {where_clause}
            ORDER BY DESCRIPCION_PRODUCTO
            ROWS {skip + 1} TO {skip + limit}
            """
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            items = []
            for row in rows:
                items.append({
                    "id": row[0],
                    "codigoProducto": row[1],
                    "descripcionProducto": row[2],
                    "codigoProductoERP": row[3],
                    "codigoFamilia": row[4],
                    "nombreFamilia": row[5],
                    "diasVencimiento": row[6],
                    "codigoUMB": row[7],
                    "descripcionUMB": row[8],
                    "codigoFormaEmbalaje": row[9],
                    "nombreFormaEmbalaje": row[10],
                    "created_at": row[11],
                    "last_sync_at": row[12]
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
            SELECT ID, CODIGO_PRODUCTO, DESCRIPCION_PRODUCTO, CODIGO_PRODUCTO_ERP,
                   CODIGO_FAMILIA, NOMBRE_FAMILIA, DIAS_VENCIMIENTO, CODIGO_UMB,
                   DESCRIPCION_UMB, CODIGO_FORMA_EMBALAJE, NOMBRE_FORMA_EMBALAJE,
                   CREATED_AT, LAST_SYNC_AT
            FROM STL_ITEMS 
            WHERE CODIGO_PRODUCTO = ?
            """
            
            cursor.execute(sql, (item_code,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail=f"Artículo {item_code} no encontrado")
            
            return {
                "id": row[0],
                "codigoProducto": row[1],
                "descripcionProducto": row[2],
                "codigoProductoERP": row[3],
                "codigoFamilia": row[4],
                "nombreFamilia": row[5],
                "diasVencimiento": row[6],
                "codigoUMB": row[7],
                "descripcionUMB": row[8],
                "codigoFormaEmbalaje": row[9],
                "nombreFormaEmbalaje": row[10],
                "created_at": row[11],
                "last_sync_at": row[12]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo item {item_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo item: {str(e)}")


@router.get("/dispatches")
async def get_dispatches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    codigo_cliente: Optional[str] = None,
    tipo_despacho: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    """Obtiene despachos sincronizados desde SAP-STL"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            where_conditions = []
            params = []
            
            if codigo_cliente:
                where_conditions.append("CODIGO_CLIENTE = ?")
                params.append(codigo_cliente)
            
            if tipo_despacho:
                where_conditions.append("TIPO_DESPACHO = ?")
                params.append(tipo_despacho)
            
            if from_date:
                where_conditions.append("FECHA_PICKING >= ?")
                params.append(from_date)
            
            if to_date:
                where_conditions.append("FECHA_PICKING <= ?")
                params.append(to_date)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Contar total
            count_sql = f"SELECT COUNT(*) FROM STL_DISPATCHES {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()[0]
            
            # Obtener datos
            sql = f"""
            SELECT ID, NUMERO_DESPACHO, NUMERO_BUSQUEDA, FECHA_CREACION,
                   FECHA_PICKING, FECHA_CARGA, CODIGO_CLIENTE, NOMBRE_CLIENTE,
                   TIPO_DESPACHO, CREATED_AT, LAST_SYNC_AT
            FROM STL_DISPATCHES {where_clause}
            ORDER BY FECHA_PICKING DESC
            ROWS {skip + 1} TO {skip + limit}
            """
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            dispatches = []
            for row in rows:
                dispatches.append({
                    "id": row[0],
                    "numeroDespacho": row[1],
                    "numeroBusqueda": row[2],
                    "fechaCreacion": row[3],
                    "fechaPicking": row[4],
                    "fechaCarga": row[5],
                    "codigoCliente": row[6],
                    "nombreCliente": row[7],
                    "tipoDespacho": row[8],
                    "created_at": row[9],
                    "last_sync_at": row[10]
                })
            
            return {
                "dispatches": dispatches,
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
    except Exception as e:
        logger.error(f"Error obteniendo dispatches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo dispatches: {str(e)}")


@router.get("/dispatches/{dispatch_id}/lines")
async def get_dispatch_lines(dispatch_id: int):
    """Obtiene las líneas de un despacho"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            sql = """
            SELECT ID, CODIGO_PRODUCTO, NOMBRE_PRODUCTO, ALMACEN,
                   CANTIDAD_UMB, LINE_NUM, UOM_CODE, UOM_ENTRY
            FROM STL_DISPATCH_LINES
            WHERE DISPATCH_ID = ?
            ORDER BY LINE_NUM
            """
            
            cursor.execute(sql, (dispatch_id,))
            rows = cursor.fetchall()
            
            lines = []
            for row in rows:
                lines.append({
                    "id": row[0],
                    "codigoProducto": row[1],
                    "nombreProducto": row[2],
                    "almacen": row[3],
                    "cantidadUMB": float(row[4]) if row[4] else 0,
                    "lineNum": row[5],
                    "uoMCode": row[6],
                    "uoMEntry": row[7]
                })
            
            return {"lines": lines}
            
    except Exception as e:
        logger.error(f"Error obteniendo líneas de despacho {dispatch_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo líneas: {str(e)}")


@router.get("/goods-receipts")
async def get_goods_receipts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    codigo_suplidor: Optional[str] = None,
    tipo_recepcion: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    """Obtiene recepciones de mercancía sincronizadas desde SAP-STL"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            where_conditions = []
            params = []
            
            if codigo_suplidor:
                where_conditions.append("CODIGO_SUPLIDOR = ?")
                params.append(codigo_suplidor)
            
            if tipo_recepcion:
                where_conditions.append("TIPO_RECEPCION = ?")
                params.append(tipo_recepcion)
            
            if from_date:
                where_conditions.append("FECHA >= ?")
                params.append(from_date)
            
            if to_date:
                where_conditions.append("FECHA <= ?")
                params.append(to_date)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Contar total
            count_sql = f"SELECT COUNT(*) FROM STL_GOODS_RECEIPTS {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()[0]
            
            # Obtener datos
            sql = f"""
            SELECT ID, NUMERO_DOCUMENTO, NUMERO_BUSQUEDA, FECHA,
                   TIPO_RECEPCION, CODIGO_SUPLIDOR, NOMBRE_SUPLIDOR,
                   CREATED_AT, LAST_SYNC_AT
            FROM STL_GOODS_RECEIPTS {where_clause}
            ORDER BY FECHA DESC
            ROWS {skip + 1} TO {skip + limit}
            """
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            receipts = []
            for row in rows:
                receipts.append({
                    "id": row[0],
                    "numeroDocumento": row[1],
                    "numeroBusqueda": row[2],
                    "fecha": row[3],
                    "tipoRecepcion": row[4],
                    "codigoSuplidor": row[5],
                    "nombreSuplidor": row[6],
                    "created_at": row[7],
                    "last_sync_at": row[8]
                })
            
            return {
                "goods_receipts": receipts,
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
    except Exception as e:
        logger.error(f"Error obteniendo goods receipts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo goods receipts: {str(e)}")


# Endpoints para crear transacciones (proxy a API STL)
@router.post("/delivery-notes")
async def create_delivery_note(dispatch: DispatchSTL):
    """Crea una nota de entrega en SAP-STL"""
    try:
        success = await sap_stl_client.create_delivery_note(dispatch)
        if success:
            return {"message": "Nota de entrega creada exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error creando nota de entrega")
    except Exception as e:
        logger.error(f"Error creando delivery note: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/goods-receipt")
async def create_goods_receipt(receipt: GoodsReceiptSTL):
    """Crea una recepción de mercancía en SAP-STL"""
    try:
        success = await sap_stl_client.create_goods_receipt(receipt)
        if success:
            return {"message": "Recepción de mercancía creada exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error creando recepción")
    except Exception as e:
        logger.error(f"Error creando goods receipt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/inventory-goods-issue")
async def create_inventory_goods_issue(issue: InventoryGoodsIssueSTL):
    """Crea una salida de inventario en SAP-STL"""
    try:
        success = await sap_stl_client.create_inventory_goods_issue(issue)
        if success:
            return {"message": "Salida de inventario creada exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error creando salida de inventario")
    except Exception as e:
        logger.error(f"Error creando inventory issue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/inventory-goods-receipt")
async def create_inventory_goods_receipt(receipt: InventoryGoodsReceiptSTL):
    """Crea una entrada de inventario en SAP-STL"""
    try:
        success = await sap_stl_client.create_inventory_goods_receipt(receipt)
        if success:
            return {"message": "Entrada de inventario creada exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error creando entrada de inventario")
    except Exception as e:
        logger.error(f"Error creando inventory receipt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/inventory-transfer")
async def create_inventory_transfer(transfer: InventoryTransfer):
    """Crea una transferencia de inventario en SAP-STL"""
    try:
        success = await sap_stl_client.create_inventory_transfer(transfer)
        if success:
            return {"message": "Transferencia de inventario creada exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error creando transferencia")
    except Exception as e:
        logger.error(f"Error creando inventory transfer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/analytics/summary")
async def get_analytics_summary():
    """Obtiene resumen analítico de datos SAP-STL"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Contar entidades
            cursor.execute("SELECT COUNT(*) FROM STL_ITEMS")
            total_items = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM STL_DISPATCHES")
            total_dispatches = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM STL_GOODS_RECEIPTS")
            total_receipts = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT CODIGO_CLIENTE) FROM STL_DISPATCHES")
            unique_customers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT CODIGO_SUPLIDOR) FROM STL_GOODS_RECEIPTS")
            unique_suppliers = cursor.fetchone()[0]
            
            # Despachos recientes por tipo
            cursor.execute("""
                SELECT TIPO_DESPACHO, COUNT(*) as CANTIDAD
                FROM STL_DISPATCHES 
                WHERE FECHA_PICKING >= DATEADD(day, -7, CURRENT_DATE)
                GROUP BY TIPO_DESPACHO
                ORDER BY CANTIDAD DESC
            """)
            recent_dispatches_by_type = [
                {"tipo_despacho": row[0], "cantidad": row[1]}
                for row in cursor.fetchall()
            ]
            
            return {
                "summary": {
                    "total_items": total_items,
                    "total_dispatches": total_dispatches,
                    "total_goods_receipts": total_receipts,
                    "unique_customers": unique_customers,
                    "unique_suppliers": unique_suppliers
                },
                "recent_dispatches_by_type": recent_dispatches_by_type
            }
            
    except Exception as e:
        logger.error(f"Error obteniendo analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo analytics: {str(e)}")