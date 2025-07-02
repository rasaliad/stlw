import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from app.core.database import FirebirdConnection
from app.services.sap_stl_client import sap_stl_client
from app.models.sap_stl_models import DispatchSTL, DispatchLineSTL

logger = logging.getLogger(__name__)


class SAPDeliveryService:
    """Servicio para enviar pedidos (DeliveryNotes) a SAP-STL"""
    
    def __init__(self):
        self.db = FirebirdConnection()
    
    def _format_sap_datetime(self, dt: datetime) -> Optional[str]:
        """Formatea datetime al formato esperado por SAP: 2025-07-01T00:00:00Z"""
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    async def get_pending_deliveries(self) -> List[Dict[str, Any]]:
        """Obtiene los pedidos pendientes de enviar a SAP desde vw_pedidos_to_sap"""
        query = """
            SELECT numerodespacho,
                   numerobusqueda,
                   fechacreacion,
                   fechapicking,
                   fechacarga,
                   codigocliente,
                   nombrecliente,
                   tipodespacho,
                   codigoproducto,
                   nombreproducto,
                   almacen,
                   cantidadumb,
                   linenum,
                   uomcode,
                   uomentry,
                   id_cliente,
                   id_pedido,
                   id_pedido_detalle,
                   id_almacen_origen,
                   estatus,
                   estatus_erp,
                   numero_solucion_erp,
                   mensaje_erp,
                   secuencia_vcl
            FROM vw_pedidos_to_sap p
            WHERE p.estatus = 3 AND p.estatus_erp = 2
            ORDER BY secuencia_vcl
        """
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                
                columns = [desc[0].lower() for desc in cursor.description]
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                return results
                
        except Exception as e:
            logger.error(f"Error obteniendo pedidos pendientes: {str(e)}")
            return []
    
    def _group_deliveries_by_order(self, rows: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """Agrupa las filas por id_pedido para formar la estructura cabecera-detalle"""
        grouped = defaultdict(lambda: {"lines": []})
        
        for row in rows:
            id_pedido = row['id_pedido']
            
            # Si es la primera vez que vemos este pedido, guardar la cabecera
            if not grouped[id_pedido].get('numeroDespacho'):
                grouped[id_pedido].update({
                    'numeroDespacho': row['numerodespacho'],
                    'numeroBusqueda': row['numerobusqueda'],
                    'fechaCreacion': self._format_sap_datetime(row['fechacreacion']),
                    'fechaPicking': self._format_sap_datetime(row['fechapicking']),
                    'fechaCarga': self._format_sap_datetime(row['fechacarga']),
                    'codigoCliente': row['codigocliente'],
                    'nombreCliente': row['nombrecliente'],
                    'tipoDespacho': row['tipodespacho'],
                    'id_pedido': row['id_pedido']  # Para referencia interna
                })
            
            # Agregar la línea del producto
            grouped[id_pedido]['lines'].append({
                'codigoProducto': row['codigoproducto'],
                'nombreProducto': row['nombreproducto'],
                'almacen': row['almacen'],
                'cantidadUMB': float(row['cantidadumb']) if row['cantidadumb'] else 0,
                'lineNum': row['linenum'],
                'uoMCode': row['uomcode'],
                'uoMEntry': row['uomentry']
            })
        
        return dict(grouped)
    
    async def send_delivery_to_sap(self, delivery_data: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        """Envía un pedido a SAP y retorna el resultado"""
        try:
            # Preparar el modelo de datos para SAP
            lines = [DispatchLineSTL(**line) for line in delivery_data['lines']]
            
            dispatch = DispatchSTL(
                numeroDespacho=delivery_data['numeroDespacho'],
                numeroBusqueda=delivery_data['numeroBusqueda'],
                fechaCreacion=delivery_data['fechaCreacion'],
                fechaPicking=delivery_data['fechaPicking'],
                fechaCarga=delivery_data['fechaCarga'],
                codigoCliente=delivery_data['codigoCliente'],
                nombreCliente=delivery_data['nombreCliente'],
                tipoDespacho=delivery_data['tipoDespacho'],
                lines=lines
            )
            
            logger.info(f"{'[DRY RUN] ' if dry_run else ''}Procesando DeliveryNote - Pedido ID: {delivery_data['id_pedido']}")
            
            # Si es dry_run, solo retornar el JSON que se enviaría
            if dry_run:
                return {
                    'success': True,
                    'code': 200,
                    'message': 'DRY RUN - No se envió a SAP',
                    'response': {
                        'json_to_send': dispatch.dict(),
                        'endpoint': '/Transaction/DeliveryNotes',
                        'method': 'POST'
                    }
                }
            
            # Hacer el POST a SAP
            response = await sap_stl_client.create_delivery_note(dispatch)
            
            # Analizar respuesta
            return {
                'success': response['success'],
                'code': response['status_code'],
                'message': response['message'],
                'response': response['data']
            }
                
        except Exception as e:
            logger.error(f"Error enviando pedido a SAP: {str(e)}")
            return {
                'success': False,
                'code': 500,
                'message': f'Error: {str(e)}',
                'response': None
            }
    
    def update_pedido_status(self, id_pedido: int, result: Dict[str, Any]) -> bool:
        """Actualiza el estado del pedido en la base de datos según el resultado"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                if result['success']:
                    # Si fue exitoso, actualizar estatus_erp = 3
                    query = """
                        UPDATE pedidos
                        SET estatus_erp = 3,
                            mensaje_erp = ?,
                            numero_solucion_erp = ?
                        WHERE id_pedido = ?
                    """
                    params = (result['message'], result['code'], id_pedido)
                else:
                    # Si falló, solo actualizar mensaje y código
                    query = """
                        UPDATE pedidos
                        SET mensaje_erp = ?,
                            numero_solucion_erp = ?
                        WHERE id_pedido = ?
                    """
                    params = (result['message'], result['code'], id_pedido)
                
                cursor.execute(query, params)
                conn.commit()
                
                logger.info(f"Pedido {id_pedido} actualizado - Éxito: {result['success']}")
                return True
                
        except Exception as e:
            logger.error(f"Error actualizando estado del pedido {id_pedido}: {str(e)}")
            return False
    
    async def process_pending_deliveries(self, dry_run: bool = True) -> Dict[str, Any]:
        """Procesa todos los pedidos pendientes de enviar a SAP"""
        logger.info(f"{'[DRY RUN] ' if dry_run else ''}Iniciando procesamiento de pedidos pendientes para SAP")
        
        # Obtener pedidos pendientes
        pending_rows = await self.get_pending_deliveries()
        
        if not pending_rows:
            logger.info("No hay pedidos pendientes para enviar a SAP")
            return {
                'processed': 0,
                'success': 0,
                'failed': 0,
                'details': []
            }
        
        # Agrupar por pedido
        grouped_deliveries = self._group_deliveries_by_order(pending_rows)
        
        logger.info(f"Se encontraron {len(grouped_deliveries)} pedidos para procesar")
        
        results = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        # Procesar cada pedido
        for id_pedido, delivery_data in grouped_deliveries.items():
            try:
                # Enviar a SAP (o simular si es dry_run)
                result = await self.send_delivery_to_sap(delivery_data, dry_run=dry_run)
                
                # Solo actualizar base de datos si NO es dry_run
                updated = False
                if not dry_run:
                    updated = self.update_pedido_status(id_pedido, result)
                
                # Registrar resultado
                results['processed'] += 1
                if result['success']:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                
                results['details'].append({
                    'id_pedido': id_pedido,
                    'numeroDespacho': delivery_data['numeroDespacho'],
                    'success': result['success'],
                    'message': result['message'],
                    'updated_db': updated,
                    'json_data': result.get('response', {}).get('json_to_send') if dry_run else None
                })
                
            except Exception as e:
                logger.error(f"Error procesando pedido {id_pedido}: {str(e)}")
                results['failed'] += 1
                results['details'].append({
                    'id_pedido': id_pedido,
                    'numeroDespacho': delivery_data.get('numeroDespacho'),
                    'success': False,
                    'message': f'Error: {str(e)}',
                    'updated_db': False
                })
        
        logger.info(f"{'[DRY RUN] ' if dry_run else ''}Procesamiento completado - Total: {results['processed']}, "
                   f"Exitosos: {results['success']}, Fallidos: {results['failed']}")
        
        return results


# Instancia global del servicio
sap_delivery_service = SAPDeliveryService()