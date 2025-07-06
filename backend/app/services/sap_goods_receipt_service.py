import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from app.core.database import FirebirdConnection
from app.services.sap_stl_client import sap_stl_client
from app.models.sap_stl_models import GoodsReceiptSTL, GoodsReceiptLineSTL

logger = logging.getLogger(__name__)


class SAPGoodsReceiptService:
    """Servicio para enviar recepciones (GoodsReceipts) a SAP-STL"""
    
    def __init__(self):
        self.db = FirebirdConnection()
    
    def _format_sap_datetime(self, dt: datetime) -> Optional[str]:
        """Formatea datetime al formato esperado por SAP: 2025-07-03T00:00:00Z"""
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    async def get_pending_receipts(self) -> List[Dict[str, Any]]:
        """Obtiene las recepciones pendientes de enviar a SAP desde vw_recepcion_to_sap"""
        query = """
            SELECT numerodocumento,
                   numerobusqueda,
                   fecha,
                   tiporecepcion,
                   codigosuplidor,
                   nombresuplidor,
                   codigoproducto,
                   nombreproducto,
                   codigofamilia,
                   nombrefamilia,
                   cantidad,
                   unidaddemedidaumb,
                   linenum,
                   uomentry,
                   uomcode,
                   diasvencimiento,
                   id_suplidor,
                   id_recepcion,
                   id_recepcion_detalle,
                   id_almacen_origen,
                   estatus,
                   estatus_erp,
                   numero_solucion_erp,
                   mensaje_erp,
                   secuencia_vcl,
                   numero_recepcion_erp,
                   caja_recibida,
                   cantidad_solicitada,
                   cantidad_diferencia
            FROM vw_recepcion_to_sap
            WHERE estatus = 3 AND estatus_erp = 2
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
            logger.error(f"Error obteniendo recepciones pendientes: {str(e)}")
            return []
    
    def _group_receipts_by_id(self, rows: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """Agrupa las filas por id_recepcion para formar la estructura cabecera-detalle"""
        grouped = defaultdict(lambda: {"lines": []})
        
        for row in rows:
            id_recepcion = row['id_recepcion']
            
            # Si es la primera vez que vemos esta recepción, guardar la cabecera
            if not grouped[id_recepcion].get('numeroBusqueda'):
                grouped[id_recepcion].update({
                    'numeroDocumento': row['numerodocumento'],
                    'numeroBusqueda': row['numerobusqueda'],
                    'fecha': self._format_sap_datetime(row['fecha']),
                    'tipoRecepcion': row['tiporecepcion'],
                    'codigoSuplidor': row['codigosuplidor'],
                    'nombreSuplidor': row['nombresuplidor'],
                    'id_recepcion': row['id_recepcion']  # Para referencia interna
                })
            
            # Agregar la línea del producto
            grouped[id_recepcion]['lines'].append({
                'codigoProducto': row['codigoproducto'],
                'nombreProducto': row['nombreproducto'],
                'codigoFamilia': row['codigofamilia'],
                'nombreFamilia': row['nombrefamilia'],
                'cantidad': float(row['cantidad']) if row['cantidad'] else 0,
                'unidadDeMedidaUMB': row['unidaddemedidaumb'],
                'lineNum': row['linenum'] if row['linenum'] is not None else 0,
                'uoMEntry': row['uomentry'] if row['uomentry'] is not None else 0,
                'uoMCode': row['uomcode'],
                'diasVencimiento': row['diasvencimiento']
            })
        
        return dict(grouped)
    
    async def send_receipt_to_sap(self, receipt_data: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        """Envía una recepción a SAP y retorna el resultado"""
        try:
            # Preparar el modelo de datos para SAP
            lines = [GoodsReceiptLineSTL(**line) for line in receipt_data['lines']]
            
            receipt = GoodsReceiptSTL(
                numeroDocumento=receipt_data['numeroDocumento'],
                numeroBusqueda=receipt_data['numeroBusqueda'],
                fecha=receipt_data['fecha'],
                tipoRecepcion=receipt_data['tipoRecepcion'],
                codigoSuplidor=receipt_data['codigoSuplidor'],
                nombreSuplidor=receipt_data['nombreSuplidor'],
                lines=lines
            )
            
            logger.info(f"{'[DRY RUN] ' if dry_run else ''}Procesando GoodsReceipt - Recepción ID: {receipt_data['id_recepcion']}")
            
            # Si es dry_run, solo retornar el JSON que se enviaría
            if dry_run:
                return {
                    'success': True,
                    'code': 200,
                    'message': 'DRY RUN - No se envió a SAP',
                    'response': {
                        'json_to_send': receipt.dict(),
                        'endpoint': '/Transaction/GoodsReceipt',
                        'method': 'POST'
                    }
                }
            
            # Hacer el POST a SAP
            response = await sap_stl_client.create_goods_receipt(receipt)
            
            # Analizar respuesta
            return {
                'success': response['success'],
                'code': response['status_code'],
                'message': response['message'],
                'response': response['data']
            }
                
        except Exception as e:
            logger.error(f"Error enviando recepción a SAP: {str(e)}")
            return {
                'success': False,
                'code': 500,
                'message': f'Error: {str(e)}',
                'response': None
            }
    
    def update_recepcion_status(self, id_recepcion: int, result: Dict[str, Any]) -> bool:
        """Actualiza el estado de la recepción en la base de datos según el resultado"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Limpiar mensaje para evitar errores de conversión en Firebird
                clean_message = str(result['message']).replace('T00:00:00Z', '').replace('2025-07-', '').replace('2025-01-', '')[:200]
                
                if result['success']:
                    # Si fue exitoso, actualizar estatus_erp = 3
                    query = """
                        UPDATE recepciones
                        SET estatus_erp = 3,
                            mensaje_erp = ?,
                            numero_solucion_erp = ?
                        WHERE id_recepcion = ?
                    """
                    params = (clean_message, result['code'], id_recepcion)
                else:
                    # Si falló, solo actualizar mensaje y código
                    query = """
                        UPDATE recepciones
                        SET mensaje_erp = ?,
                            numero_solucion_erp = ?
                        WHERE id_recepcion = ?
                    """
                    params = (clean_message, result['code'], id_recepcion)
                
                cursor.execute(query, params)
                conn.commit()
                
                logger.info(f"Recepción {id_recepcion} actualizada - Éxito: {result['success']}")
                return True
                
        except Exception as e:
            logger.error(f"Error actualizando estado de la recepción {id_recepcion}: {str(e)}")
            return False
    
    async def process_pending_receipts(self, dry_run: bool = True) -> Dict[str, Any]:
        """Procesa todas las recepciones pendientes de enviar a SAP"""
        logger.info(f"{'[DRY RUN] ' if dry_run else ''}Iniciando procesamiento de recepciones pendientes para SAP")
        
        # Obtener recepciones pendientes
        pending_rows = await self.get_pending_receipts()
        
        if not pending_rows:
            logger.info("No hay recepciones pendientes para enviar a SAP")
            return {
                'processed': 0,
                'success': 0,
                'failed': 0,
                'details': []
            }
        
        # Agrupar por recepción
        grouped_receipts = self._group_receipts_by_id(pending_rows)
        
        logger.info(f"Se encontraron {len(grouped_receipts)} recepciones para procesar")
        
        results = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        # Procesar cada recepción
        for id_recepcion, receipt_data in grouped_receipts.items():
            try:
                # Enviar a SAP (o simular si es dry_run)
                result = await self.send_receipt_to_sap(receipt_data, dry_run=dry_run)
                
                # Solo actualizar base de datos si NO es dry_run
                updated = False
                if not dry_run:
                    updated = self.update_recepcion_status(id_recepcion, result)
                
                # Registrar resultado
                results['processed'] += 1
                if result['success']:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                
                results['details'].append({
                    'id_recepcion': id_recepcion,
                    'numeroBusqueda': receipt_data['numeroBusqueda'],
                    'success': result['success'],
                    'message': result['message'],
                    'updated_db': updated,
                    'json_data': result.get('response', {}).get('json_to_send') if dry_run else None
                })
                
            except Exception as e:
                logger.error(f"Error procesando recepción {id_recepcion}: {str(e)}")
                results['failed'] += 1
                results['details'].append({
                    'id_recepcion': id_recepcion,
                    'numeroBusqueda': receipt_data.get('numeroBusqueda'),
                    'success': False,
                    'message': f'Error: {str(e)}',
                    'updated_db': False
                })
        
        logger.info(f"{'[DRY RUN] ' if dry_run else ''}Procesamiento completado - Total: {results['processed']}, "
                   f"Exitosos: {results['success']}, Fallidos: {results['failed']}")
        
        return results


# Instancia global del servicio
sap_goods_receipt_service = SAPGoodsReceiptService()