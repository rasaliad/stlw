import httpx
from typing import Optional, List
from datetime import datetime
import logging

from app.core.config import settings
from app.models.sap_stl_models import (
    UserLoginRequest, ResponseAuth, ItemSTL, DispatchSTL, 
    GoodsReceiptSTL, InventoryGoodsIssueSTL, InventoryGoodsReceiptSTL, 
    InventoryTransfer
)

logger = logging.getLogger(__name__)


class SAPSTLClient:
    def __init__(self):
        self.base_url = settings.SAP_STL_URL.rstrip('/b1s/v1')  # Usar la URL base sin /b1s/v1
        self.username = settings.SAP_STL_USERNAME
        self.password = settings.SAP_STL_PASSWORD
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def login(self) -> bool:
        """Autenticación con la API STL"""
        try:
            login_data = UserLoginRequest(
                name=self.username,
                password=self.password
            )
            
            response = await self.client.post(
                f"{self.base_url}/Auth/Login",
                json=login_data.dict(),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                auth_response = ResponseAuth(**response.json())
                self.token = auth_response.token
                self.token_expiry = auth_response.expirationDate
                logger.info("Login exitoso a API SAP-STL")
                return True
            else:
                logger.error(f"Error en login SAP-STL: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción en login SAP-STL: {str(e)}")
            return False
    
    def _get_headers(self) -> dict:
        """Headers con token de autenticación"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    async def _ensure_authenticated(self) -> bool:
        """Asegura que tenemos un token válido"""
        if not self.token or (self.token_expiry and datetime.now() >= self.token_expiry):
            return await self.login()
        return True
    
    async def _make_request(self, method: str, endpoint: str, **kwargs):
        """Realiza petición HTTP con manejo de autenticación"""
        try:
            if not await self._ensure_authenticated():
                logger.error("No se pudo autenticar con API SAP-STL")
                return None
            
            headers = self._get_headers()
            if 'headers' in kwargs:
                headers.update(kwargs['headers'])
            kwargs['headers'] = headers
            
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = await self.client.request(method, url, **kwargs)
            
            if response.status_code == 401:
                # Token expirado, reautenticar
                logger.info("Token expirado, reautenticando...")
                self.token = None
                if await self.login():
                    headers = self._get_headers()
                    kwargs['headers'] = headers
                    response = await self.client.request(method, url, **kwargs)
                else:
                    return None
            
            if response.status_code in [200, 201]:
                return response.json() if response.content else {}
            else:
                logger.error(f"Error en API SAP-STL: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción en petición SAP-STL: {str(e)}")
            return None
    
    # Endpoints de MasterData
    async def get_items(self) -> Optional[List[ItemSTL]]:
        """Obtiene todos los artículos"""
        data = await self._make_request("GET", "/MasterData/Items")
        if data and isinstance(data, list):
            return [ItemSTL(**item) for item in data]
        return None
    
    async def get_item_by_code(self, item_code: str) -> Optional[ItemSTL]:
        """Obtiene un artículo específico por código"""
        data = await self._make_request("GET", f"/MasterData/Items/{item_code}")
        if data:
            return ItemSTL(**data)
        return None
    
    # Endpoints de Transaction
    async def get_orders(self, tipo_despacho: Optional[int] = None) -> Optional[List[DispatchSTL]]:
        """Obtiene órdenes/despachos"""
        endpoint = "/Transaction/Orders"
        if tipo_despacho is not None:
            endpoint += f"?tipoDespacho={tipo_despacho}"
        
        data = await self._make_request("GET", endpoint)
        if data and isinstance(data, list):
            return [DispatchSTL(**dispatch) for dispatch in data]
        return None
    
    async def get_order_by_id(self, tipo_despacho: int, doc_entry: int) -> Optional[DispatchSTL]:
        """Obtiene una orden específica"""
        data = await self._make_request("GET", f"/Transaction/Orders/{tipo_despacho}/{doc_entry}")
        if data:
            return DispatchSTL(**data)
        return None
    
    async def create_delivery_note(self, dispatch: DispatchSTL) -> bool:
        """Crea una nota de entrega"""
        data = await self._make_request("POST", "/Transaction/DeliveryNotes", json=dispatch.dict())
        return data is not None
    
    async def get_procurement_orders(self, tipo_recepcion: Optional[int] = None) -> Optional[List[GoodsReceiptSTL]]:
        """Obtiene órdenes de compra"""
        endpoint = "/Transaction/ProcurementOrders"
        if tipo_recepcion is not None:
            endpoint += f"?tipoRecepcion={tipo_recepcion}"
        
        data = await self._make_request("GET", endpoint)
        if data and isinstance(data, list):
            return [GoodsReceiptSTL(**receipt) for receipt in data]
        return None
    
    async def get_procurement_order_by_id(self, tipo_recepcion: int, doc_entry: int) -> Optional[GoodsReceiptSTL]:
        """Obtiene una orden de compra específica"""
        data = await self._make_request("GET", f"/Transaction/ProcurementOrders/{tipo_recepcion}/{doc_entry}")
        if data:
            return GoodsReceiptSTL(**data)
        return None
    
    async def get_goods_receipts(self, tipo_recepcion: Optional[int] = None) -> Optional[List[GoodsReceiptSTL]]:
        """Obtiene recepciones de mercancía"""
        endpoint = "/Transaction/GoodsReceipt"
        if tipo_recepcion is not None:
            endpoint += f"?tipoRecepcion={tipo_recepcion}"
        
        data = await self._make_request("GET", endpoint)
        if data and isinstance(data, list):
            return [GoodsReceiptSTL(**receipt) for receipt in data]
        return None
    
    async def create_goods_receipt(self, receipt: GoodsReceiptSTL) -> bool:
        """Crea una recepción de mercancía"""
        data = await self._make_request("POST", "/Transaction/GoodsReceipt", json=receipt.dict())
        return data is not None
    
    async def create_goods_return(self, receipt: GoodsReceiptSTL) -> Optional[List[GoodsReceiptSTL]]:
        """Crea una devolución de mercancía"""
        data = await self._make_request("POST", "/Transaction/GoodsReturn", json=receipt.dict())
        if data and isinstance(data, list):
            return [GoodsReceiptSTL(**item) for item in data]
        return None
    
    async def create_inventory_goods_issue(self, issue: InventoryGoodsIssueSTL) -> bool:
        """Crea una salida de inventario"""
        data = await self._make_request("POST", "/Transaction/InventoryGoodsIssue", json=issue.dict())
        return data is not None
    
    async def create_inventory_goods_receipt(self, receipt: InventoryGoodsReceiptSTL) -> bool:
        """Crea una entrada de inventario"""
        data = await self._make_request("POST", "/Transaction/InventoryGoodsReceipt", json=receipt.dict())
        return data is not None
    
    async def create_inventory_transfer(self, transfer: InventoryTransfer) -> bool:
        """Crea una transferencia de inventario"""
        data = await self._make_request("POST", "/Transaction/InventoryTransfer", json=transfer.dict())
        return data is not None
    
    async def close(self):
        """Cierra el cliente HTTP"""
        if self.client:
            await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Instancia global del cliente SAP-STL
sap_stl_client = SAPSTLClient()