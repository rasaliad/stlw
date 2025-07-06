from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.api.deps import get_current_user
from app.models.user import User
from app.services.sap_goods_receipt_service import sap_goods_receipt_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/send-pending-receipts")
async def send_pending_receipts(
    dry_run: bool = True,  # Por defecto en modo dry_run
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Envía todas las recepciones pendientes a SAP-STL.
    Solo procesa recepciones con estatus = 3 y estatus_erp = 2
    
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
        logger.info(f"Usuario {current_user.username} iniciando {mode} de recepciones a SAP")
        
        # Procesar recepciones pendientes
        result = await sap_goods_receipt_service.process_pending_receipts(dry_run=dry_run)
        
        return {
            "success": True,
            "mode": mode,
            "message": f"{mode} completado - {result['success']} exitosos, {result['failed']} fallidos",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error en envío manual de recepciones: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando recepciones: {str(e)}"
        )

@router.get("/pending-receipts")
async def get_pending_receipts(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene la lista de recepciones pendientes de enviar a SAP
    """
    try:
        pending = await sap_goods_receipt_service.get_pending_receipts()
        
        # Agrupar por recepción para mostrar resumen
        grouped = sap_goods_receipt_service._group_receipts_by_id(pending)
        
        summary = []
        for id_recepcion, data in grouped.items():
            summary.append({
                'id_recepcion': id_recepcion,
                'numeroDocumento': data['numeroDocumento'],
                'codigoSuplidor': data['codigoSuplidor'],
                'nombreSuplidor': data['nombreSuplidor'],
                'cantidadLineas': len(data['lines']),
                'fecha': data['fecha']
            })
        
        return {
            "success": True,
            "totalRecepciones": len(grouped),
            "totalLineas": len(pending),
            "recepciones": summary
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo recepciones pendientes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo recepciones pendientes: {str(e)}"
        )