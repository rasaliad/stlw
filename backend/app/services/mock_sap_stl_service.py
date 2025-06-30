"""
Servicio simulador para datos SAP-STL
Permite trabajar con datos de prueba mientras el servidor externo no está disponible
"""
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.models.sap_stl_models import (
    ItemSTL, DispatchSTL, GoodsReceiptSTL, DispatchLineSTL, GoodsReceiptLineSTL
)

logger = logging.getLogger(__name__)


class MockSAPSTLService:
    def __init__(self):
        self.is_enabled = True  # Se puede cambiar en configuración
        self._items_data = None  # Cache para items
        
    def set_enabled(self, enabled: bool):
        """Habilita o deshabilita el modo simulación"""
        self.is_enabled = enabled
        logger.info(f"Modo simulación {'activado' if enabled else 'desactivado'}")
    
    def get_mock_items(self) -> List[Dict[str, Any]]:
        """Retorna datos simulados de items desde archivo JSON si existe"""
        if self._items_data is None:
            # Intentar cargar desde archivo JSON
            json_path = "/app/response_Items.json"
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        self._items_data = json.load(f)
                    logger.info(f"Cargados {len(self._items_data)} items desde archivo JSON")
                except Exception as e:
                    logger.error(f"Error cargando items desde JSON: {str(e)}")
                    self._items_data = self._get_default_items()
            else:
                self._items_data = self._get_default_items()
        
        return self._items_data
    
    def _get_default_items(self) -> List[Dict[str, Any]]:
        """Retorna items por defecto si no hay archivo JSON"""
        return [
            {
                "codigoProducto": "1003",
                "descripcionProducto": "CEBOLLA EN POLVO BADIA 18OZ",
                "codigoProductoERP": "1003",
                "codigoFamilia": 121,
                "nombreFamilia": "ESPECIAS/ABARROTES",
                "diasVencimiento": 30,
                "codigoUMB": "030",
                "descripcionUMB": "Unidad",
                "codigoFormaEmbalaje": "001",
                "nombreFormaEmbalaje": None
            },
            {
                "codigoProducto": "1004",
                "descripcionProducto": "OREGANO ENTERO 5.5 OZ BADIA",
                "codigoProductoERP": "1004",
                "codigoFamilia": 121,
                "nombreFamilia": "ESPECIAS/ABARROTES",
                "diasVencimiento": 30,
                "codigoUMB": "030",
                "descripcionUMB": "Unidad",
                "codigoFormaEmbalaje": "001",
                "nombreFormaEmbalaje": None
            }
        ]
    
    def get_mock_goods_receipts(self) -> List[Dict[str, Any]]:
        """Retorna datos simulados de recepciones de mercancía"""
        return [
            {
                "numeroDocumento": 4,
                "numeroBusqueda": 1,
                "fecha": "2025-05-06T00:00:00Z",
                "tipoRecepcion": 102,
                "codigoSuplidor": "PV-00001",
                "nombreSuplidor": "CONGELADOS INTERNACIONALES CI",
                "lines": [
                    {
                        "codigoProducto": "1008",
                        "nombreProducto": "NUEZ MOSCADA MOLIDA 16OZ BADIA",
                        "codigoFamilia": 121,
                        "nombreFamilia": "ESPECIAS/ABARROTES",
                        "cantidad": 1,
                        "unidadDeMedidaUMB": None,
                        "lineNum": 0,
                        "uoMEntry": 1,
                        "uoMCode": "Unidad",
                        "diasVencimiento": None
                    },
                    {
                        "codigoProducto": "1004",
                        "nombreProducto": "OREGANO ENTERO 5.5 OZ BADIA",
                        "codigoFamilia": 121,
                        "nombreFamilia": "ESPECIAS/ABARROTES",
                        "cantidad": 1,
                        "unidadDeMedidaUMB": None,
                        "lineNum": 1,
                        "uoMEntry": 1,
                        "uoMCode": "Unidad",
                        "diasVencimiento": None
                    }
                ]
            },
            {
                "numeroDocumento": 12,
                "numeroBusqueda": 3,
                "fecha": "2025-05-13T00:00:00Z",
                "tipoRecepcion": 102,
                "codigoSuplidor": "PV-00020",
                "nombreSuplidor": "AMACA DISTRIBUIDORES",
                "lines": [
                    {
                        "codigoProducto": "1047",
                        "nombreProducto": "STRIPLOIN CAB PRIME PORCIONADO 16 OZ",
                        "codigoFamilia": 112,
                        "nombreFamilia": "RES CAB PRIME PORCIONADA",
                        "cantidad": 400,
                        "unidadDeMedidaUMB": "032",
                        "lineNum": 0,
                        "uoMEntry": 2,
                        "uoMCode": "Libra",
                        "diasVencimiento": None
                    },
                    {
                        "codigoProducto": "1048",
                        "nombreProducto": "CHURRASCO CHOICE PORCIONADO 10 OZ",
                        "codigoFamilia": 106,
                        "nombreFamilia": "RES CHOICE PORCIONADA",
                        "cantidad": 100,
                        "unidadDeMedidaUMB": "032",
                        "lineNum": 1,
                        "uoMEntry": 2,
                        "uoMCode": "Libra",
                        "diasVencimiento": None
                    }
                ]
            },
            {
                "numeroDocumento": 15,
                "numeroBusqueda": 4,
                "fecha": "2025-04-28T00:00:00Z",
                "tipoRecepcion": 103,
                "codigoSuplidor": "PV-00001",
                "nombreSuplidor": "CONGELADOS INTERNACIONALES CI",
                "lines": [
                    {
                        "codigoProducto": "1003",
                        "nombreProducto": "CEBOLLA EN POLVO BADIA 18OZ",
                        "codigoFamilia": 121,
                        "nombreFamilia": "ESPECIAS/ABARROTES",
                        "cantidad": 10,
                        "unidadDeMedidaUMB": "030",
                        "lineNum": 0,
                        "uoMEntry": 1,
                        "uoMCode": "Unidad",
                        "diasVencimiento": None
                    }
                ]
            }
        ]
    
    def get_mock_procurement_orders(self) -> List[Dict[str, Any]]:
        """Retorna datos simulados de órdenes de compra"""
        return [
            {
                "numeroDocumento": 16,
                "numeroBusqueda": 8,
                "fecha": "2025-04-28T00:00:00Z",
                "tipoRecepcion": 102,
                "codigoSuplidor": "PV-00013",
                "nombreSuplidor": "ALL STAR FOODS SRL",
                "lines": [
                    {
                        "codigoProducto": "1068",
                        "nombreProducto": "SHORTLOIN PRIME",
                        "codigoFamilia": None,
                        "nombreFamilia": None,
                        "cantidad": 16,
                        "unidadDeMedidaUMB": None,
                        "lineNum": 0,
                        "uoMEntry": 2,
                        "uoMCode": "Libra",
                        "diasVencimiento": None
                    },
                    {
                        "codigoProducto": "1066",
                        "nombreProducto": "FLAP MEAT PRIME PORCIONADO 12 OZ",
                        "codigoFamilia": None,
                        "nombreFamilia": None,
                        "cantidad": 171,
                        "unidadDeMedidaUMB": None,
                        "lineNum": 1,
                        "uoMEntry": 2,
                        "uoMCode": "Libra",
                        "diasVencimiento": None
                    }
                ]
            },
            {
                "numeroDocumento": 35,
                "numeroBusqueda": 21,
                "fecha": "2025-06-03T00:00:00Z",
                "tipoRecepcion": 102,
                "codigoSuplidor": "PV-00040",
                "nombreSuplidor": "ASOC. PADRES Y TUTORES DEL COL. SAINT JO",
                "lines": [
                    {
                        "codigoProducto": "1078",
                        "nombreProducto": "NUEZ MOSCADA ENTERA 16OZ BADIA",
                        "codigoFamilia": 121,
                        "nombreFamilia": "ESPECIAS/ABARROTES",
                        "cantidad": 1,
                        "unidadDeMedidaUMB": "030",
                        "lineNum": 0,
                        "uoMEntry": 1,
                        "uoMCode": "Unidad",
                        "diasVencimiento": None
                    },
                    {
                        "codigoProducto": "108",
                        "nombreProducto": "HAMBURGUESAS CAB 8 OZ",
                        "codigoFamilia": 109,
                        "nombreFamilia": "RES CAB",
                        "cantidad": 1,
                        "unidadDeMedidaUMB": "032",
                        "lineNum": 1,
                        "uoMEntry": 2,
                        "uoMCode": "Libra",
                        "diasVencimiento": None
                    }
                ]
            }
        ]
    
    def get_mock_orders(self) -> List[Dict[str, Any]]:
        """Retorna datos simulados de órdenes/despachos"""
        return [
            {
                "numeroDespacho": 23,
                "numeroBusqueda": 20,
                "fechaCreacion": "2025-03-28T10:26:00Z",
                "fechaPicking": "2025-03-28T00:00:00Z",
                "fechaCarga": None,
                "codigoCliente": "CL-00047",
                "nombreCliente": "ALIANZA JUVENIL POR EL DEPORTE Y LA C.",
                "tipoDespacho": 201,
                "lines": [
                    {
                        "codigoProducto": "331",
                        "nombreProducto": "STRIPLOIN CHOICE PORCIONADO",
                        "almacen": "01",
                        "cantidadUMB": 10,
                        "lineNum": 0,
                        "uoMCode": "Libra (Lb)",
                        "uoMEntry": 2
                    },
                    {
                        "codigoProducto": "332",
                        "nombreProducto": "RIBEYE CHOICE PORCIONADO",
                        "almacen": "01",
                        "cantidadUMB": 10,
                        "lineNum": 1,
                        "uoMCode": "Libra (Lb)",
                        "uoMEntry": 2
                    },
                    {
                        "codigoProducto": "334",
                        "nombreProducto": "LOMO DE CERDO PORCIONADO",
                        "almacen": "01",
                        "cantidadUMB": 10,
                        "lineNum": 2,
                        "uoMCode": "Libra (Lb)",
                        "uoMEntry": 2
                    }
                ]
            },
            {
                "numeroDespacho": 24,
                "numeroBusqueda": 21,
                "fechaCreacion": "2025-03-29T09:15:00Z",
                "fechaPicking": "2025-03-29T00:00:00Z",
                "fechaCarga": None,
                "codigoCliente": "CL-00048",
                "nombreCliente": "RESTAURANTE EL BUEN SABOR",
                "tipoDespacho": 201,
                "lines": [
                    {
                        "codigoProducto": "337",
                        "nombreProducto": "CHURRASCO CAB PELADO",
                        "almacen": "01",
                        "cantidadUMB": 25,
                        "lineNum": 0,
                        "uoMCode": "Libra (Lb)",
                        "uoMEntry": 2
                    },
                    {
                        "codigoProducto": "338",
                        "nombreProducto": "FLAP MEAT CAB PRIME",
                        "almacen": "01",
                        "cantidadUMB": 15,
                        "lineNum": 1,
                        "uoMCode": "Libra (Lb)",
                        "uoMEntry": 2
                    }
                ]
            }
        ]


# Instancia global del servicio simulador
mock_sap_stl_service = MockSAPSTLService()