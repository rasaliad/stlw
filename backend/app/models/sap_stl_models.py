from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Autenticación
class UserLoginRequest(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None


class ResponseAuth(BaseModel):
    token: Optional[str] = None
    expirationDate: datetime
    userName: Optional[str] = None


# Items/Artículos
class ItemSTL(BaseModel):
    codigoProducto: Optional[str] = None
    descripcionProducto: Optional[str] = None
    codigoProductoERP: Optional[str] = None
    codigoFamilia: Optional[int] = None
    nombreFamilia: Optional[str] = None
    diasVencimiento: Optional[int] = None
    codigoUMB: Optional[str] = None
    descripcionUMB: Optional[str] = None
    codigoFormaEmbalaje: Optional[str] = None
    nombreFormaEmbalaje: Optional[str] = None


# Líneas de Despacho
class DispatchLineSTL(BaseModel):
    codigoProducto: Optional[str] = None
    nombreProducto: Optional[str] = None
    almacen: Optional[str] = None
    cantidadUMB: Optional[float] = None
    lineNum: Optional[int] = None
    uoMCode: Optional[str] = None
    uoMEntry: Optional[int] = None


# Despachos
class DispatchSTL(BaseModel):
    numeroDespacho: Optional[int] = None
    numeroBusqueda: Optional[int] = None
    fechaCreacion: Optional[str] = None
    fechaPicking: Optional[datetime] = None
    fechaCarga: Optional[str] = None
    codigoCliente: Optional[str] = None
    nombreCliente: Optional[str] = None
    tipoDespacho: int
    lines: Optional[List[DispatchLineSTL]] = None


# Líneas de Recepción de Mercancía
class GoodsReceiptLineSTL(BaseModel):
    codigoProducto: Optional[str] = None
    nombreProducto: Optional[str] = None
    codigoFamilia: Optional[int] = None
    nombreFamilia: Optional[str] = None
    cantidad: Optional[float] = None
    unidadDeMedidaUMB: Optional[str] = None
    lineNum: Optional[int] = None
    uoMEntry: Optional[int] = None
    uoMCode: Optional[str] = None
    diasVencimiento: Optional[int] = None


# Recepción de Mercancía
class GoodsReceiptSTL(BaseModel):
    numeroDocumento: Optional[int] = None
    numeroBusqueda: Optional[int] = None
    fecha: Optional[datetime] = None
    tipoRecepcion: Optional[int] = None
    codigoSuplidor: Optional[str] = None
    nombreSuplidor: Optional[str] = None
    lines: Optional[List[GoodsReceiptLineSTL]] = None


# Líneas de Salida de Inventario
class InventoryGoodsIssueLineSTL(BaseModel):
    codigoProducto: Optional[str] = None
    cantidadUMB: float


# Salida de Inventario
class InventoryGoodsIssueSTL(BaseModel):
    fechaCreacion: Optional[datetime] = None
    tipoDespacho: int
    lines: Optional[List[InventoryGoodsIssueLineSTL]] = None


# Líneas de Entrada de Inventario
class InventoryGoodsReceiptLineSTL(BaseModel):
    codigoProducto: Optional[str] = None
    cantidadUMB: float


# Entrada de Inventario
class InventoryGoodsReceiptSTL(BaseModel):
    fechaCreacion: Optional[datetime] = None
    tipoRecepcion: int
    lines: Optional[List[InventoryGoodsReceiptLineSTL]] = None


# Líneas de Transferencia de Inventario
class InventoryTransferLine(BaseModel):
    codigoProducto: Optional[str] = None
    cantidadUMB: float
    almacen: Optional[str] = None


# Transferencia de Inventario
class InventoryTransfer(BaseModel):
    fechaCreacion: Optional[datetime] = None
    tipoDespacho: int
    lines: Optional[List[InventoryTransferLine]] = None


# Responses para listas
class ItemSTLListResponse(BaseModel):
    items: List[ItemSTL] = []


class DispatchSTLListResponse(BaseModel):
    dispatches: List[DispatchSTL] = []


class GoodsReceiptSTLListResponse(BaseModel):
    goodsReceipts: List[GoodsReceiptSTL] = []