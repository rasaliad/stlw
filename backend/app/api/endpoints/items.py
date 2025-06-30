from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

from app.core.database import FirebirdConnection
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()
db = FirebirdConnection()

@router.get("/")
async def get_items(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    codigo_familia: Optional[int] = Query(None)
):
    """Obtiene items/productos con filtros y paginación"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Construir condiciones WHERE
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
                    "codigo_producto": row[1],
                    "descripcion_producto": row[2],
                    "codigo_producto_erp": row[3],
                    "codigo_familia": row[4],
                    "nombre_familia": row[5],
                    "dias_vencimiento": row[6],
                    "codigo_umb": row[7],
                    "descripcion_umb": row[8],
                    "codigo_forma_embalaje": row[9],
                    "nombre_forma_embalaje": row[10],
                    "created_at": row[11].isoformat() if row[11] else None,
                    "last_sync_at": row[12].isoformat() if row[12] else None
                })
            
            return {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo items: {str(e)}")

@router.get("/count")
async def get_items_count(
    current_user: User = Depends(get_current_user),
    search: Optional[str] = Query(None),
    codigo_familia: Optional[int] = Query(None)
):
    """Obtiene el conteo total de items"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
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
            
            query = f"SELECT COUNT(*) FROM STL_ITEMS {where_clause}"
            cursor.execute(query, params)
            total = cursor.fetchone()[0]
            
            return {"total": total}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo conteo: {str(e)}")

@router.get("/{item_code}")
async def get_item_by_code(
    item_code: str,
    current_user: User = Depends(get_current_user)
):
    """Obtiene un item específico por código"""
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
                raise HTTPException(status_code=404, detail=f"Item {item_code} no encontrado")
            
            return {
                "id": row[0],
                "codigo_producto": row[1],
                "descripcion_producto": row[2],
                "codigo_producto_erp": row[3],
                "codigo_familia": row[4],
                "nombre_familia": row[5],
                "dias_vencimiento": row[6],
                "codigo_umb": row[7],
                "descripcion_umb": row[8],
                "codigo_forma_embalaje": row[9],
                "nombre_forma_embalaje": row[10],
                "created_at": row[11].isoformat() if row[11] else None,
                "last_sync_at": row[12].isoformat() if row[12] else None
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo item: {str(e)}")