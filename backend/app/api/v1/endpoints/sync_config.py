from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.sync_config import SyncConfigResponse, SyncConfigUpdate
from app.services.sync_config_service import sync_config_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[SyncConfigResponse])
async def get_sync_configs(current_user: User = Depends(get_current_user)):
    """Obtener todas las configuraciones de sincronización"""
    if current_user.role != "ADMINISTRADOR":
        raise HTTPException(status_code=403, detail="Solo administradores pueden ver la configuración")
    
    return sync_config_service.get_all_configs()

@router.get("/{entity_type}", response_model=SyncConfigResponse)
async def get_sync_config(entity_type: str, current_user: User = Depends(get_current_user)):
    """Obtener configuración de una entidad específica"""
    if current_user.role != "ADMINISTRADOR":
        raise HTTPException(status_code=403, detail="Solo administradores pueden ver la configuración")
    
    config = sync_config_service.get_config_by_entity(entity_type)
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    
    return config

@router.put("/{entity_type}", response_model=SyncConfigResponse)
async def update_sync_config(
    entity_type: str, 
    config_data: SyncConfigUpdate,
    current_user: User = Depends(get_current_user)
):
    """Actualizar configuración de sincronización"""
    if current_user.role != "ADMINISTRADOR":
        raise HTTPException(status_code=403, detail="Solo administradores pueden modificar la configuración")
    
    updated_config = sync_config_service.update_config(entity_type, config_data)
    if not updated_config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    
    return updated_config