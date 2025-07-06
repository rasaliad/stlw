from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.api.deps import get_current_user
from app.models.user import User
from app.services.sap_delivery_service import sap_delivery_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/send-pending-deliveries")
async def send_pending_deliveries(
    dry_run: bool = True,  # Por defecto en modo dry_run
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Envía todos los pedidos pendientes a SAP-STL.
    Solo procesa pedidos con estatus = 3 y estatus_erp = 2
    
    Args:
        dry_run: Si es True, solo muestra el JSON sin enviar. Si es False, envía realmente a SAP.
    """
    if current_user.role not in ["ADMINISTRADOR"]:
        raise HTTPException(
            status_code=403,
            detail="Solo administradores pueden ejecutar esta acción"
        )
    
    try:
        mode = "DRY RUN" if dry_run else "ENVÍO REAL"
        logger.info(f"Usuario {current_user.username} iniciando {mode} de pedidos a SAP")
        
        # Procesar pedidos pendientes
        result = await sap_delivery_service.process_pending_deliveries(dry_run=dry_run)
        
        return {
            "success": True,
            "mode": mode,
            "message": f"{mode} completado - {result['success']} exitosos, {result['failed']} fallidos",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error en envío manual de pedidos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando pedidos: {str(e)}"
        )

@router.get("/pending-deliveries")
async def get_pending_deliveries(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene la lista de pedidos pendientes de enviar a SAP
    """
    try:
        pending = await sap_delivery_service.get_pending_deliveries()
        
        # Agrupar por pedido para mostrar resumen
        grouped = sap_delivery_service._group_deliveries_by_order(pending)
        
        summary = []
        for id_pedido, data in grouped.items():
            summary.append({
                'id_pedido': id_pedido,
                'numeroBusqueda': data['numeroBusqueda'],
                'tipoDespacho': data['tipoDespacho'],
                'codigoCliente': data['codigoCliente'],
                'nombreCliente': data['nombreCliente'],
                'cantidadLineas': len(data['lines']),
                'fechaPicking': data['fechaPicking']
            })
        
        return {
            "success": True,
            "totalPedidos": len(grouped),
            "totalLineas": len(pending),
            "pedidos": summary
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo pedidos pendientes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo pedidos pendientes: {str(e)}"
        )