"""
Modelos para sincronización manual de despachos desde SAP
"""
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class DispatchLineManual(BaseModel):
    """Línea de despacho desde SAP"""
    codigoProducto: str
    nombreProducto: str
    almacen: str
    cantidadUMB: float
    lineNum: int
    uoMCode: str
    uoMEntry: int


class DispatchManual(BaseModel):
    """Despacho completo desde SAP para sincronización manual"""
    numeroDespacho: int
    numeroBusqueda: int
    fechaCreacion: str
    fechaPicking: str
    fechaCarga: Optional[str] = None
    codigoCliente: str
    nombreCliente: str
    tipoDespacho: int
    lines: List[DispatchLineManual]


class DispatchSyncResponse(BaseModel):
    """Respuesta de sincronización manual"""
    success: bool
    message: str
    dispatch_id: Optional[int] = None
    lines_inserted: int = 0
    details: Optional[dict] = None