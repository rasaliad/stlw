from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

from app.core.database import FirebirdConnection
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()
db = FirebirdConnection()

@router.get("/")
async def get_goods_receipts(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    codigo_suplidor: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None)
):
    """Obtiene recepciones de mercancía con sus líneas"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Construir condiciones WHERE
            where_conditions = []
            params = []
            
            if codigo_suplidor:
                where_conditions.append("r.CODIGO_SUPLIDOR = ?")
                params.append(codigo_suplidor)
            
            if from_date:
                where_conditions.append("r.FECHA >= ?")
                params.append(from_date)
            
            if to_date:
                where_conditions.append("r.FECHA <= ?")
                params.append(to_date)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # Query principal para recepciones
            receipts_query = f"""
            SELECT r.ID, r.NUMERO_DOCUMENTO, r.NUMERO_BUSQUEDA, r.FECHA,
                   r.TIPO_RECEPCION, r.CODIGO_SUPLIDOR, r.NOMBRE_SUPLIDOR,
                   'SYNCED' as SYNC_STATUS
            FROM STL_GOODS_RECEIPTS r
            {where_clause}
            ORDER BY r.FECHA DESC
            ROWS {skip + 1} TO {skip + limit}
            """
            
            cursor.execute(receipts_query, params)
            receipts_data = cursor.fetchall()
            
            receipts = []
            for row in receipts_data:
                receipt_id = row[0]
                
                # Obtener líneas de la recepción
                lines_query = """
                SELECT l.ID, l.RECEIPT_ID, l.CODIGO_PRODUCTO, l.NOMBRE_PRODUCTO,
                       l.CODIGO_FAMILIA, l.CANTIDAD, l.LINE_NUM, l.UOM_CODE
                FROM STL_GOODS_RECEIPT_LINES l
                WHERE l.RECEIPT_ID = ?
                ORDER BY l.LINE_NUM
                """
                
                cursor.execute(lines_query, (receipt_id,))
                lines_data = cursor.fetchall()
                
                lines = []
                for line_row in lines_data:
                    lines.append({
                        "id": line_row[0],
                        "goods_receipt_id": line_row[1],
                        "codigo_producto": line_row[2],
                        "nombre_producto": line_row[3],
                        "almacen": f"FAM-{line_row[4]}" if line_row[4] else "GENERAL",
                        "cantidad_umb": float(line_row[5]) if line_row[5] else None,
                        "line_num": line_row[6],
                        "uom_code": line_row[7]
                    })
                
                receipts.append({
                    "id": row[0],
                    "numero_documento": row[1],
                    "numero_busqueda": row[2],
                    "fecha": row[3].isoformat() if row[3] else None,
                    "tipo_recepcion": row[4],
                    "codigo_suplidor": row[5],
                    "nombre_suplidor": row[6],
                    "sync_status": row[7],
                    "lines": lines
                })
            
            return receipts
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo recepciones: {str(e)}")

@router.get("/count")
async def get_goods_receipts_count(
    current_user: User = Depends(get_current_user),
    codigo_suplidor: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None), 
    to_date: Optional[date] = Query(None)
):
    """Obtiene el conteo total de recepciones"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            where_conditions = []
            params = []
            
            if codigo_suplidor:
                where_conditions.append("CODIGO_SUPLIDOR = ?")
                params.append(codigo_suplidor)
            
            if from_date:
                where_conditions.append("FECHA >= ?")
                params.append(from_date)
            
            if to_date:
                where_conditions.append("FECHA <= ?")
                params.append(to_date)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            query = f"SELECT COUNT(*) FROM STL_GOODS_RECEIPTS {where_clause}"
            cursor.execute(query, params)
            total = cursor.fetchone()[0]
            
            return {"total": total}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo conteo: {str(e)}")

@router.get("/{receipt_id}")
async def get_goods_receipt(
    receipt_id: int,
    current_user: User = Depends(get_current_user)
):
    """Obtiene una recepción específica con sus líneas"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener recepción principal
            receipt_query = """
            SELECT ID, NUMERO_DOCUMENTO, NUMERO_BUSQUEDA, FECHA,
                   TIPO_RECEPCION, CODIGO_SUPLIDOR, NOMBRE_SUPLIDOR
            FROM STL_GOODS_RECEIPTS
            WHERE ID = ?
            """
            
            cursor.execute(receipt_query, (receipt_id,))
            receipt_data = cursor.fetchone()
            
            if not receipt_data:
                raise HTTPException(status_code=404, detail="Recepción no encontrada")
            
            # Obtener líneas
            lines_query = """
            SELECT ID, RECEIPT_ID, CODIGO_PRODUCTO, NOMBRE_PRODUCTO,
                   CODIGO_FAMILIA, CANTIDAD, LINE_NUM, UOM_CODE
            FROM STL_GOODS_RECEIPT_LINES
            WHERE RECEIPT_ID = ?
            ORDER BY LINE_NUM
            """
            
            cursor.execute(lines_query, (receipt_id,))
            lines_data = cursor.fetchall()
            
            lines = []
            for line_row in lines_data:
                lines.append({
                    "id": line_row[0],
                    "goods_receipt_id": line_row[1],
                    "codigo_producto": line_row[2],
                    "nombre_producto": line_row[3],
                    "almacen": f"FAM-{line_row[4]}" if line_row[4] else "GENERAL",
                    "cantidad_umb": float(line_row[5]) if line_row[5] else None,
                    "line_num": line_row[6],
                    "uom_code": line_row[7]
                })
            
            return {
                "id": receipt_data[0],
                "numero_documento": receipt_data[1],
                "numero_busqueda": receipt_data[2],
                "fecha": receipt_data[3].isoformat() if receipt_data[3] else None,
                "tipo_recepcion": receipt_data[4],
                "codigo_suplidor": receipt_data[5],
                "nombre_suplidor": receipt_data[6],
                "sync_status": "SYNCED",
                "lines": lines
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo recepción: {str(e)}")