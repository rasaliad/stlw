from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from datetime import datetime
from app.schemas.dispatch import DispatchResponse, DispatchFilters
from app.services.dispatch_service import dispatch_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[DispatchResponse])
async def get_dispatches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    codigo_cliente: Optional[str] = None,
    tipo_despacho: Optional[int] = None,
    sync_status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Obtener lista de despachos con filtros opcionales"""
    filters = DispatchFilters(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        codigo_cliente=codigo_cliente,
        tipo_despacho=tipo_despacho,
        sync_status=sync_status
    )
    return dispatch_service.get_dispatches(filters, skip, limit)

@router.get("/count")
async def count_dispatches(
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    codigo_cliente: Optional[str] = None,
    tipo_despacho: Optional[int] = None,
    sync_status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Contar total de despachos con filtros opcionales"""
    filters = DispatchFilters(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        codigo_cliente=codigo_cliente,
        tipo_despacho=tipo_despacho,
        sync_status=sync_status
    )
    total = dispatch_service.count_dispatches(filters)
    return {"total": total}

@router.get("/{dispatch_id}", response_model=DispatchResponse)
async def get_dispatch(dispatch_id: int, current_user: User = Depends(get_current_user)):
    """Obtener un despacho específico con sus líneas"""
    dispatch = dispatch_service.get_dispatch_by_id(dispatch_id)
    if not dispatch:
        raise HTTPException(status_code=404, detail="Despacho no encontrado")
    
    return dispatch