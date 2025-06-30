from typing import List, Optional
from datetime import datetime
from app.schemas.dispatch import DispatchResponse, DispatchLineResponse, DispatchFilters
from app.core.database import db

class DispatchService:
    def get_dispatches(self, filters: DispatchFilters, skip: int = 0, limit: int = 100) -> List[DispatchResponse]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Construir query con filtros
            query = """
                SELECT ID, NUMERO_DESPACHO, NUMERO_BUSQUEDA, FECHA_CREACION, 
                       FECHA_PICKING, FECHA_CARGA, CODIGO_CLIENTE, NOMBRE_CLIENTE,
                       TIPO_DESPACHO, CREATED_AT, UPDATED_AT, SYNC_STATUS, LAST_SYNC_AT
                FROM STL_DISPATCHES
                WHERE 1=1
            """
            params = []
            
            if filters.fecha_desde:
                query += " AND FECHA_PICKING >= ?"
                params.append(filters.fecha_desde)
            
            if filters.fecha_hasta:
                query += " AND FECHA_PICKING <= ?"
                params.append(filters.fecha_hasta)
            
            if filters.codigo_cliente:
                query += " AND CODIGO_CLIENTE = ?"
                params.append(filters.codigo_cliente)
            
            if filters.tipo_despacho is not None:
                query += " AND TIPO_DESPACHO = ?"
                params.append(filters.tipo_despacho)
            
            if filters.sync_status:
                query += " AND SYNC_STATUS = ?"
                params.append(filters.sync_status)
            
            query += f" ORDER BY FECHA_PICKING DESC ROWS {skip + 1} TO {skip + limit}"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            dispatches = []
            for row in results:
                dispatch = DispatchResponse(
                    id=row[0],
                    numero_despacho=row[1],
                    numero_busqueda=row[2],
                    fecha_creacion=row[3],
                    fecha_picking=row[4],
                    fecha_carga=row[5],
                    codigo_cliente=row[6],
                    nombre_cliente=row[7],
                    tipo_despacho=row[8],
                    created_at=row[9],
                    updated_at=row[10],
                    sync_status=row[11],
                    last_sync_at=row[12],
                    lines=[]
                )
                dispatches.append(dispatch)
            
            # Cargar líneas para cada despacho
            for dispatch in dispatches:
                dispatch.lines = self._get_dispatch_lines(dispatch.id)
            
            return dispatches
    
    def get_dispatch_by_id(self, dispatch_id: int) -> Optional[DispatchResponse]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT ID, NUMERO_DESPACHO, NUMERO_BUSQUEDA, FECHA_CREACION, 
                       FECHA_PICKING, FECHA_CARGA, CODIGO_CLIENTE, NOMBRE_CLIENTE,
                       TIPO_DESPACHO, CREATED_AT, UPDATED_AT, SYNC_STATUS, LAST_SYNC_AT
                FROM STL_DISPATCHES
                WHERE ID = ?
            """
            cursor.execute(query, (dispatch_id,))
            result = cursor.fetchone()
            
            if result:
                dispatch = DispatchResponse(
                    id=result[0],
                    numero_despacho=result[1],
                    numero_busqueda=result[2],
                    fecha_creacion=result[3],
                    fecha_picking=result[4],
                    fecha_carga=result[5],
                    codigo_cliente=result[6],
                    nombre_cliente=result[7],
                    tipo_despacho=result[8],
                    created_at=result[9],
                    updated_at=result[10],
                    sync_status=result[11],
                    last_sync_at=result[12],
                    lines=self._get_dispatch_lines(result[0])
                )
                return dispatch
            return None
    
    def _get_dispatch_lines(self, dispatch_id: int) -> List[DispatchLineResponse]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT ID, DISPATCH_ID, CODIGO_PRODUCTO, NOMBRE_PRODUCTO,
                       ALMACEN, CANTIDAD_UMB, LINE_NUM, UOM_CODE, UOM_ENTRY, CREATED_AT
                FROM STL_DISPATCH_LINES
                WHERE DISPATCH_ID = ?
                ORDER BY LINE_NUM
            """
            cursor.execute(query, (dispatch_id,))
            results = cursor.fetchall()
            
            lines = []
            for row in results:
                line = DispatchLineResponse(
                    id=row[0],
                    dispatch_id=row[1],
                    codigo_producto=row[2],
                    nombre_producto=row[3],
                    almacen=row[4],
                    cantidad_umb=row[5],
                    line_num=row[6],
                    uom_code=row[7],
                    uom_entry=row[8],
                    created_at=row[9]
                )
                lines.append(line)
            
            return lines
    
    def count_dispatches(self, filters: DispatchFilters) -> int:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM STL_DISPATCHES WHERE 1=1"
            params = []
            
            if filters.fecha_desde:
                query += " AND FECHA_PICKING >= ?"
                params.append(filters.fecha_desde)
            
            if filters.fecha_hasta:
                query += " AND FECHA_PICKING <= ?"
                params.append(filters.fecha_hasta)
            
            if filters.codigo_cliente:
                query += " AND CODIGO_CLIENTE = ?"
                params.append(filters.codigo_cliente)
            
            if filters.tipo_despacho is not None:
                query += " AND TIPO_DESPACHO = ?"
                params.append(filters.tipo_despacho)
            
            if filters.sync_status:
                query += " AND SYNC_STATUS = ?"
                params.append(filters.sync_status)
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else 0

dispatch_service = DispatchService()