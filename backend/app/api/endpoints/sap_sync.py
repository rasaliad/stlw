from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import User
from app.services.optimized_sync_service import OptimizedSyncService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class SingleDispatchSyncRequest(BaseModel):
    tipoDespacho: int
    docNum: int

@router.post("/single-dispatch")
async def sync_single_dispatch(
    request: SingleDispatchSyncRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Sincroniza un pedido específico desde SAP usando tipoDespacho + docNum.
    Invoca GET /Transaction/Orders/{tipoDespacho}/{docNum} y lo inserta/actualiza en STL.
    
    Args:
        tipoDespacho: Tipo de despacho del pedido en SAP
        docNum: Número de documento del pedido en SAP
    
    Returns:
        Resultado de la sincronización (insertado/actualizado/error)
    """
    if current_user.role not in ["ADMINISTRADOR"]:
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden ejecutar esta acción"
        )
    
    try:
        logger.info(f"Usuario {current_user.username} iniciando sync individual - tipoDespacho: {request.tipoDespacho}, docNum: {request.docNum}")
        
        # Crear instancia del servicio de sincronización
        sync_service = OptimizedSyncService()
        
        # Ejecutar sincronización individual
        result = await sync_service.sync_single_dispatch(request.tipoDespacho, request.docNum)
        
        if result['success']:
            logger.info(f"Sync individual exitoso: {result['message']}")
            return {
                "success": True,
                "message": result['message'],
                "data": result['data']
            }
        else:
            logger.warning(f"Sync individual falló: {result['message']}")
            return {
                "success": False,
                "message": result['message'],
                "data": result['data']
            }
        
    except Exception as e:
        logger.error(f"Error en endpoint sync individual: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando sincronización: {str(e)}"
        )

@router.get("/dispatch-types")
async def get_dispatch_types(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retorna los tipos de despacho más comunes para el formulario.
    Esto es informativo para ayudar al usuario a seleccionar el tipo correcto.
    """
    try:
        # Tipos de despacho comunes basados en la documentación del proyecto
        dispatch_types = [
            {"value": 201, "label": "Despacho Normal (201)"},
            {"value": 202, "label": "Despacho Urgente (202)"},
            {"value": 203, "label": "Despacho Express (203)"},
            {"value": 204, "label": "Transferencia (204)"}
        ]
        
        return {
            "success": True,
            "data": dispatch_types,
            "message": "Tipos de despacho disponibles"
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo tipos de despacho: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo tipos de despacho: {str(e)}"
        )