import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.core.config import settings
from app.models.sap_stl_models import (
    UserLoginRequest, ResponseAuth, ItemSTL, DispatchSTL, 
    GoodsReceiptSTL, InventoryGoodsIssueSTL, InventoryGoodsReceiptSTL, 
    InventoryTransfer
)
from app.services.mock_sap_stl_service import mock_sap_stl_service

logger = logging.getLogger(__name__)


class SAPSTLClient:
    def __init__(self):
        self.base_url = settings.SAP_STL_URL.rstrip('/b1s/v1')  # Usar la URL base sin /b1s/v1
        self.username = settings.SAP_STL_USERNAME
        self.password = settings.SAP_STL_PASSWORD
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Configuración para modo simulación
        self.use_mock_data = getattr(settings, 'USE_MOCK_SAP_DATA', False)
    
    async def login(self) -> bool:
        """Autenticación con la API STL"""
        try:
            logger.info(f"Intentando login en {self.base_url}/Auth/Login con usuario: {self.username}")
            
            login_data = UserLoginRequest(
                name=self.username,
                password=self.password
            )
            
            response = await self.client.post(
                f"{self.base_url}/Auth/Login",
                json=login_data.dict(),
                headers={"Content-Type": "application/json"}
            )
            
            logger.info(f"Respuesta login: Status {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"Datos de respuesta login: {response_data}")
                
                auth_response = ResponseAuth(**response_data)
                self.token = auth_response.token
                self.token_expiry = auth_response.expirationDate
                
                logger.info(f"Login exitoso. Token: {self.token[:20] if self.token else 'None'}...")
                logger.info(f"Token expira: {self.token_expiry}")
                return True
            else:
                logger.error(f"Error en login SAP-STL: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción en login SAP-STL: {str(e)}", exc_info=True)
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
        if not self.token:
            return await self.login()
        
        if self.token_expiry:
            # Asegurarse de que ambas fechas estén en el mismo formato
            now = datetime.now()
            if self.token_expiry.tzinfo is not None:
                # Si token_expiry tiene timezone, convertir now a UTC
                from datetime import timezone
                now = now.replace(tzinfo=timezone.utc)
            elif now.tzinfo is not None:
                # Si now tiene timezone pero token_expiry no, quitar timezone de now
                now = now.replace(tzinfo=None)
            
            if now >= self.token_expiry:
                return await self.login()
        
        return True
    
    async def _make_request(self, method: str, endpoint: str, **kwargs):
        """Realiza petición HTTP con manejo de autenticación"""
        try:
            logger.info(f"Haciendo petición {method} a {endpoint}")
            
            if not await self._ensure_authenticated():
                logger.error("No se pudo autenticar con API SAP-STL")
                return None
            
            headers = self._get_headers()
            if 'headers' in kwargs:
                headers.update(kwargs['headers'])
            kwargs['headers'] = headers
            
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            logger.info(f"URL completa: {url}")
            
            response = await self.client.request(method, url, **kwargs)
            logger.info(f"Respuesta: Status {response.status_code}")
            
            if response.status_code == 401:
                # Token expirado, reautenticar
                logger.info("Token expirado, reautenticando...")
                self.token = None
                if await self.login():
                    headers = self._get_headers()
                    kwargs['headers'] = headers
                    response = await self.client.request(method, url, **kwargs)
                    logger.info(f"Respuesta después de reauth: Status {response.status_code}")
                else:
                    return None
            
            if response.status_code in [200, 201]:
                content = response.json() if response.content else {}
                if isinstance(content, list):
                    logger.info(f"Contenido recibido: {len(content)} elementos")
                    if len(content) == 0:
                        logger.warning(f"API retornó lista vacía para {endpoint}")
                else:
                    logger.info(f"Contenido recibido: {type(content)}")
                return content
            else:
                logger.error(f"Error en API SAP-STL: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción en petición SAP-STL: {str(e)}", exc_info=True)
            return None
    
    # Endpoints de MasterData
    async def get_items(self) -> Optional[List[ItemSTL]]:
        """Obtiene todos los artículos"""
        if self.use_mock_data:
            logger.info("Usando datos simulados para items")
            mock_data = mock_sap_stl_service.get_mock_items()
            return [ItemSTL(**item) for item in mock_data]
        
        logger.info(f"Iniciando get_items desde {self.base_url}/MasterData/Items")
        data = await self._make_request("GET", "/MasterData/Items")
        
        if data:
            logger.info(f"Items recibidos: {len(data) if isinstance(data, list) else 'No es lista'}")
            if isinstance(data, list) and data:
                logger.info(f"Primer item: {data[0]}")
        else:
            logger.warning("No se recibieron datos de items")
        
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
        if self.use_mock_data:
            logger.info("Usando datos simulados para órdenes/despachos")
            mock_data = mock_sap_stl_service.get_mock_orders()
            # Filtrar por tipo de despacho si se especifica
            if tipo_despacho is not None:
                mock_data = [order for order in mock_data if order.get('tipoDespacho') == tipo_despacho]
            return [DispatchSTL(**dispatch) for dispatch in mock_data]
        
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
    
    async def create_delivery_note(self, dispatch: DispatchSTL) -> Dict[str, Any]:
        """Crea una nota de entrega y retorna la respuesta completa"""
        try:
            response = await self.client.post(
                f"{self.base_url}/Transaction/DeliveryNotes",
                json=dispatch.dict(),
                headers=self._get_headers()
            )
            
            success = response.status_code in [200, 201, 204]  # Solo códigos de éxito reales
            
            # Log detallado para debugging
            logger.info(f"SAP DeliveryNote Response - Status: {response.status_code}, Success: {success}")
            if response.text:
                logger.info(f"SAP DeliveryNote Response Text: {response.text}")
            else:
                logger.info("SAP DeliveryNote Response: Sin contenido")
            
            return {
                'success': success,
                'status_code': response.status_code,
                'data': response.json() if response.content else None,
                'message': response.text if response.status_code not in [200, 201, 204] else 'OK'
            }
        except Exception as e:
            logger.error(f"Error creando DeliveryNote: {str(e)}")
            return {
                'success': False,
                'status_code': 500,
                'data': None,
                'message': str(e)
            }
    
    async def get_procurement_orders(self, tipo_recepcion: Optional[int] = None) -> Optional[List[GoodsReceiptSTL]]:
        """Obtiene órdenes de compra"""
        if self.use_mock_data:
            logger.info("Usando datos simulados para órdenes de compra")
            mock_data = mock_sap_stl_service.get_mock_procurement_orders()
            # Filtrar por tipo de recepción si se especifica
            if tipo_recepcion is not None:
                mock_data = [order for order in mock_data if order.get('tipoRecepcion') == tipo_recepcion]
            return [GoodsReceiptSTL(**receipt) for receipt in mock_data]
        
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
        if self.use_mock_data:
            logger.info("Usando datos simulados para recepciones de mercancía")
            mock_data = mock_sap_stl_service.get_mock_goods_receipts()
            # Filtrar por tipo de recepción si se especifica
            if tipo_recepcion is not None:
                mock_data = [receipt for receipt in mock_data if receipt.get('tipoRecepcion') == tipo_recepcion]
            return [GoodsReceiptSTL(**receipt) for receipt in mock_data]
        
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