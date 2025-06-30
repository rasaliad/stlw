from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class DispatchLineResponse(BaseModel):
    id: int
    dispatch_id: int
    codigo_producto: Optional[str] = None
    nombre_producto: Optional[str] = None
    almacen: Optional[str] = None
    cantidad_umb: Optional[Decimal] = None
    line_num: Optional[int] = None
    uom_code: Optional[str] = None
    uom_entry: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class DispatchResponse(BaseModel):
    id: int
    numero_despacho: Optional[int] = None
    numero_busqueda: Optional[int] = None
    fecha_creacion: Optional[str] = None
    fecha_picking: Optional[datetime] = None
    fecha_carga: Optional[str] = None
    codigo_cliente: Optional[str] = None
    nombre_cliente: Optional[str] = None
    tipo_despacho: int
    created_at: datetime
    updated_at: datetime
    sync_status: str = 'PENDING'
    last_sync_at: Optional[datetime] = None
    lines: List[DispatchLineResponse] = []
    
    class Config:
        from_attributes = True

class DispatchFilters(BaseModel):
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    codigo_cliente: Optional[str] = None
    tipo_despacho: Optional[int] = None
    sync_status: Optional[str] = None