import httpx
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.models.sap_models import (
    ItemSTLResponse, BusinessPartnerSTLResponse, SalesOrderSTLResponse,
    DispatchSTLResponse, InventorySTLResponse, TransferSTLResponse,
    ServiceCallSTLResponse, InvoiceSTLResponse
)
import base64
import logging

logger = logging.getLogger(__name__)


class SAPSTLClient:
    def __init__(self):
        self.base_url = settings.SAP_STL_URL
        self.username = settings.SAP_STL_USERNAME
        self.password = settings.SAP_STL_PASSWORD
        self.session_id: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=30.0)
        
    def _get_auth_headers(self) -> Dict[str, str]:
        """Genera headers de autenticación básica"""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
    
    async def login(self) -> bool:
        """Autentica con SAP Business One Service Layer"""
        try:
            login_data = {
                "CompanyDB": "STL_DB",
                "UserName": self.username,
                "Password": self.password
            }
            
            response = await self.client.post(
                f"{self.base_url}/Login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("SessionId")
                logger.info("Login exitoso a SAP STL")
                return True
            else:
                logger.error(f"Error en login SAP STL: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción en login SAP STL: {str(e)}")
            return False
    
    def _get_authenticated_headers(self) -> Dict[str, str]:
        """Headers con sesión autenticada"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.session_id:
            headers["B1SESSION"] = self.session_id
        return headers
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Realiza petición HTTP con manejo de errores"""
        try:
            if not self.session_id:
                if not await self.login():
                    logger.error("No se pudo autenticar con SAP STL")
                    return None
            
            headers = self._get_authenticated_headers()
            if 'headers' in kwargs:
                headers.update(kwargs['headers'])
            kwargs['headers'] = headers
            
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = await self.client.request(method, url, **kwargs)
            
            if response.status_code == 401:
                # Token expirado, intentar reautenticar
                logger.info("Sesión expirada, reautenticando...")
                self.session_id = None
                if await self.login():
                    headers = self._get_authenticated_headers()
                    kwargs['headers'] = headers
                    response = await self.client.request(method, url, **kwargs)
                else:
                    return None
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error en petición SAP STL: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción en petición SAP STL: {str(e)}")
            return None
    
    async def get_items(self, filter_params: Optional[str] = None) -> Optional[ItemSTLResponse]:
        """Obtiene artículos de SAP"""
        endpoint = "Items"
        if filter_params:
            endpoint += f"?{filter_params}"
        
        data = await self._make_request("GET", endpoint)
        if data:
            return ItemSTLResponse(**data)
        return None
    
    async def get_business_partners(self, filter_params: Optional[str] = None) -> Optional[BusinessPartnerSTLResponse]:
        """Obtiene socios de negocio de SAP"""
        endpoint = "BusinessPartners"
        if filter_params:
            endpoint += f"?{filter_params}"
        
        data = await self._make_request("GET", endpoint)
        if data:
            return BusinessPartnerSTLResponse(**data)
        return None
    
    async def get_sales_orders(self, filter_params: Optional[str] = None) -> Optional[SalesOrderSTLResponse]:
        """Obtiene órdenes de venta de SAP"""
        endpoint = "Orders"
        if filter_params:
            endpoint += f"?{filter_params}"
        
        data = await self._make_request("GET", endpoint)
        if data:
            return SalesOrderSTLResponse(**data)
        return None
    
    async def get_dispatches(self, filter_params: Optional[str] = None) -> Optional[DispatchSTLResponse]:
        """Obtiene despachos personalizados de SAP"""
        endpoint = "U_DespachoSTL"
        if filter_params:
            endpoint += f"?{filter_params}"
        
        data = await self._make_request("GET", endpoint)
        if data:
            return DispatchSTLResponse(**data)
        return None
    
    async def get_inventory(self, filter_params: Optional[str] = None) -> Optional[InventorySTLResponse]:
        """Obtiene inventario de SAP"""
        endpoint = "StockTransfers"
        if filter_params:
            endpoint += f"?{filter_params}"
        
        data = await self._make_request("GET", endpoint)
        if data:
            return InventorySTLResponse(**data)
        return None
    
    async def get_transfers(self, filter_params: Optional[str] = None) -> Optional[TransferSTLResponse]:
        """Obtiene transferencias de inventario de SAP"""
        endpoint = "StockTransfers"
        if filter_params:
            endpoint += f"?{filter_params}"
        
        data = await self._make_request("GET", endpoint)
        if data:
            return TransferSTLResponse(**data)
        return None
    
    async def get_service_calls(self, filter_params: Optional[str] = None) -> Optional[ServiceCallSTLResponse]:
        """Obtiene llamadas de servicio de SAP"""
        endpoint = "ServiceCalls"
        if filter_params:
            endpoint += f"?{filter_params}"
        
        data = await self._make_request("GET", endpoint)
        if data:
            return ServiceCallSTLResponse(**data)
        return None
    
    async def get_invoices(self, filter_params: Optional[str] = None) -> Optional[InvoiceSTLResponse]:
        """Obtiene facturas de SAP"""
        endpoint = "Invoices"
        if filter_params:
            endpoint += f"?{filter_params}"
        
        data = await self._make_request("GET", endpoint)
        if data:
            return InvoiceSTLResponse(**data)
        return None
    
    async def close(self):
        """Cierra el cliente HTTP"""
        if self.client:
            await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Instancia global del cliente SAP
sap_client = SAPSTLClient()