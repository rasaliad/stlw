from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.core.security import verify_token
from app.core.database import FirebirdConnection
from app.services.user_service import user_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials.credentials)
    username = payload.get("sub")
    user_id = payload.get("user_id")
    
    if username is None or user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
        )
    
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return user

# Modelo para cambio de estatus
class CambioEstatusRequest(BaseModel):
    nuevo_estatus: int

class PedidoDetalle:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.id_pedido = kwargs.get('id_pedido') 
        self.codigo_producto = kwargs.get('codigo_producto')
        self.nombre_producto = kwargs.get('nombre_producto')
        self.cantidad_pedida = kwargs.get('cantidad_pedida')
        self.cantidad_despachada = kwargs.get('cantidad_despachada')
        self.precio_unitario = kwargs.get('precio_unitario')
        self.total_linea = kwargs.get('total_linea')

class Pedido:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.numero_pedido = kwargs.get('numero_pedido')
        self.fecha_pedido = kwargs.get('fecha_pedido')
        self.fecha_despacho = kwargs.get('fecha_despacho')
        self.codigo_cliente = kwargs.get('codigo_cliente')
        self.nombre_cliente = kwargs.get('nombre_cliente')
        self.estado = kwargs.get('estado')
        self.total_pedido = kwargs.get('total_pedido')
        self.observaciones = kwargs.get('observaciones')
        self.detalles = []

@router.get("/", response_model=List[dict])
async def get_pedidos(
    fecha_desde: Optional[str] = Query(None, description="Fecha desde en formato YYYY-MM-DD"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta en formato YYYY-MM-DD"),
    codigo_cliente: Optional[str] = Query(None, description="Código del cliente"),
    current_user = Depends(get_current_user)
):
    """Obtiene pedidos de las vistas vw_pedidos y vw_pedidos_detalle"""
    
    db = FirebirdConnection()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Construir query base para pedidos
            base_query = """
                SELECT 
                    pv.ID_PEDIDO,
                    pv.NUMERO_PEDIDO_ERP,
                    pv.TIPO,
                    pv.ESTATUS_NOMBRE,
                    pv.CLIENTE_CODIGO,
                    pv.CLIENTE_NOMBRE,
                    pv.FECHA
                FROM VW_PEDIDOS pv
                WHERE 1=1
            """
            
            params = []
            
            # Aplicar filtros
            if fecha_desde:
                base_query += " AND pv.FECHA >= ?"
                params.append(fecha_desde)
                
            if fecha_hasta:
                base_query += " AND pv.FECHA <= ?"
                params.append(fecha_hasta)
                
            if codigo_cliente:
                base_query += " AND pv.CLIENTE_CODIGO LIKE ?"
                params.append(f"%{codigo_cliente}%")
            
            base_query += " ORDER BY pv.NUMERO_PEDIDO_ERP DESC"
            
            # Ejecutar query de pedidos
            cursor.execute(base_query, params)
            pedidos_data = cursor.fetchall()
            
            pedidos = []
            
            for row in pedidos_data:
                pedido = Pedido(
                    id=row[0],
                    numero_pedido=row[1],
                    fecha_pedido=row[6].isoformat() if row[6] else None,
                    fecha_despacho=None,
                    codigo_cliente=row[4],
                    nombre_cliente=row[5],
                    estado=row[3].strip() if row[3] else None,
                    total_pedido=None,
                    observaciones=row[2]
                )
                
                # Obtener detalles del pedido
                detail_query = """
                    SELECT 
                        dv.ID_PEDIDO_DETALLE,
                        dv.ID_PEDIDO,
                        dv.POSICION,
                        dv.CODIGO,
                        dv.PRODUCTO_NOMBRE,
                        dv.CANTIDAD_PEDIDA,
                        dv.CANTIDAD_DESPACHADA,
                        dv.NOMBRE_UNIDAD,
                        dv.DIFERENCIA_STL_ERP
                    FROM VW_PEDIDOS_DETALLE dv
                    WHERE dv.ID_PEDIDO = ?
                    ORDER BY dv.POSICION
                """
                
                cursor.execute(detail_query, (pedido.id,))
                detalles_data = cursor.fetchall()
                
                for detail_row in detalles_data:
                    detalle = PedidoDetalle(
                        id=detail_row[0],
                        id_pedido=detail_row[1],
                        codigo_producto=detail_row[3],
                        nombre_producto=detail_row[4],
                        cantidad_pedida=float(detail_row[5]) if detail_row[5] else None,
                        cantidad_despachada=float(detail_row[6]) if detail_row[6] else None,
                        precio_unitario=None,
                        total_linea=float(detail_row[8]) if detail_row[8] else None
                    )
                    pedido.detalles.append(detalle)
                
                pedidos.append(pedido)
            
            # Convertir a diccionarios para respuesta
            result = []
            for pedido in pedidos:
                result.append({
                    'id': pedido.id,
                    'numero_pedido': pedido.numero_pedido,
                    'fecha_pedido': pedido.fecha_pedido,
                    'fecha_despacho': pedido.fecha_despacho,
                    'codigo_cliente': pedido.codigo_cliente,
                    'nombre_cliente': pedido.nombre_cliente,
                    'estado': pedido.estado,
                    'total_pedido': pedido.total_pedido,
                    'observaciones': pedido.observaciones,
                    'detalles': [
                        {
                            'id': d.id,
                            'id_pedido': d.id_pedido,
                            'codigo_producto': d.codigo_producto,
                            'nombre_producto': d.nombre_producto,
                            'cantidad_pedida': d.cantidad_pedida,
                            'cantidad_despachada': d.cantidad_despachada,
                            'precio_unitario': d.precio_unitario,
                            'total_linea': d.total_linea
                        } for d in pedido.detalles
                    ]
                })
            
            return result
            
    except Exception as e:
        logger.error(f"Error obteniendo pedidos STL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/count")
async def get_pedidos_count(
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    codigo_cliente: Optional[str] = Query(None),
    current_user = Depends(get_current_user)
):
    """Obtiene el conteo total de pedidos con filtros"""
    
    db = FirebirdConnection()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM VW_PEDIDOS WHERE 1=1"
            params = []
            
            if fecha_desde:
                query += " AND FECHA >= ?"
                params.append(fecha_desde)
                
            if fecha_hasta:
                query += " AND FECHA <= ?"
                params.append(fecha_hasta)
                
            if codigo_cliente:
                query += " AND CLIENTE_CODIGO LIKE ?"
                params.append(f"%{codigo_cliente}%")
            
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            
            return {"total": count}
            
    except Exception as e:
        logger.error(f"Error obteniendo conteo de pedidos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/{pedido_id}/estatus")
async def cambiar_estatus_pedido(
    pedido_id: int,
    request: CambioEstatusRequest,
    current_user = Depends(get_current_user)
):
    """Cambia el estatus de un pedido en la tabla PEDIDOS"""
    
    db = FirebirdConnection()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que el pedido existe
            check_query = "SELECT ID_PEDIDO, ESTATUS FROM PEDIDOS WHERE ID_PEDIDO = ?"
            cursor.execute(check_query, (pedido_id,))
            pedido_actual = cursor.fetchone()
            
            if not pedido_actual:
                raise HTTPException(status_code=404, detail="Pedido no encontrado")
            
            estatus_actual = pedido_actual[1]
            
            # Actualizar el estatus en la tabla PEDIDOS
            update_query = """
                UPDATE PEDIDOS 
                SET ESTATUS = ?, 
                    FECHA_CAMBIO = CURRENT_TIMESTAMP,
                    USUARIO_CAMBIO = ?
                WHERE ID_PEDIDO = ?
            """
            
            cursor.execute(update_query, (
                request.nuevo_estatus,
                current_user.username,
                pedido_id
            ))
            
            conn.commit()
            
            logger.info(f"Estatus cambiado - Pedido {pedido_id}: {estatus_actual} → {request.nuevo_estatus} por {current_user.username}")
            
            return {
                "success": True,
                "message": f"Estatus cambiado exitosamente",
                "pedido_id": pedido_id,
                "estatus_anterior": estatus_actual,
                "estatus_nuevo": request.nuevo_estatus
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cambiando estatus del pedido {pedido_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")