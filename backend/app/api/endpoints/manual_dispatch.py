"""
Endpoints para sincronización manual de despachos desde SAP
"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.manual_dispatch_models import DispatchManual, DispatchSyncResponse
from app.services.manual_dispatch_service import manual_dispatch_service

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)


@router.post("/sync-dispatch", response_model=DispatchSyncResponse)
async def sync_manual_dispatch(
    dispatch_data: DispatchManual,
    current_user: User = Depends(get_current_active_user)
):
    """
    Sincroniza manualmente un despacho desde JSON de SAP.
    
    Inserta directamente en las tablas STL_DISPATCHES y STL_DISPATCH_LINES.
    
    Ejemplo de JSON:
    ```json
    {
        "numeroDespacho": 818,
        "numeroBusqueda": 687,
        "fechaCreacion": "2025-07-08T13:03:00Z",
        "fechaPicking": "2025-07-08T00:00:00Z",
        "fechaCarga": null,
        "codigoCliente": "CL-01473",
        "nombreCliente": "CONSUMIDOR FINAL ADM",
        "tipoDespacho": 201,
        "lines": [
            {
                "codigoProducto": "466",
                "nombreProducto": "PECHUGA DE POLLO AMERICANA",
                "almacen": "01",
                "cantidadUMB": 40,
                "lineNum": 0,
                "uoMCode": "Libra",
                "uoMEntry": 2
            }
        ]
    }
    ```
    """
    try:
        logger.info(f"Usuario {current_user.username} iniciando sincronización manual de despacho {dispatch_data.numeroDespacho}")
        
        # Ejecutar sincronización
        result = manual_dispatch_service.sync_dispatch_from_json(dispatch_data)
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en sincronización manual: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )


@router.get("/dispatch/{tipo_despacho}/{numero_despacho}")
async def check_dispatch_exists(
    tipo_despacho: int,
    numero_despacho: int,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Verifica si un despacho ya existe en la base de datos.
    
    Útil para verificar antes de sincronizar.
    """
    try:
        from app.core.database import FirebirdConnection
        db = FirebirdConnection()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ID, NUMERO_BUSQUEDA, CODIGO_CLIENTE, NOMBRE_CLIENTE, 
                       FECHA_CREACION, SYNC_STATUS, LAST_SYNC_AT
                FROM STL_DISPATCHES 
                WHERE NUMERO_DESPACHO = ? AND TIPO_DESPACHO = ?
            """, (numero_despacho, tipo_despacho))
            
            row = cursor.fetchone()
            
            if not row:
                return {
                    "exists": False,
                    "message": f"Despacho {numero_despacho} tipo {tipo_despacho} no existe"
                }
            
            # Contar líneas
            cursor.execute("""
                SELECT COUNT(*) FROM STL_DISPATCH_LINES WHERE DISPATCH_ID = ?
            """, (row[0],))
            
            line_count = cursor.fetchone()[0]
            
            return {
                "exists": True,
                "dispatch_id": row[0],
                "numero_busqueda": row[1],
                "codigo_cliente": row[2],
                "nombre_cliente": row[3],
                "fecha_creacion": row[4],
                "sync_status": row[5],
                "last_sync_at": row[6],
                "lines_count": line_count
            }
            
    except Exception as e:
        logger.error(f"Error verificando despacho: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verificando despacho: {str(e)}"
        )