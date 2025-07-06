import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.sync_config_service import sync_config_service
from app.services.optimized_sync_service import optimized_sync_service

logger = logging.getLogger(__name__)

class BackgroundSyncService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.active_jobs: Dict[str, Any] = {}
        
    async def start_scheduler(self):
        """Inicia el scheduler y configura jobs automáticos"""
        try:
            self.scheduler.start()
            logger.info("Background sync scheduler iniciado")
            
            # Cargar configuraciones existentes y crear jobs
            await self.load_sync_configurations()
            
            # Job para verificar cambios en configuración cada 2 minutos
            self.scheduler.add_job(
                self.check_config_changes,
                IntervalTrigger(minutes=2),
                id="config_checker",
                name="Configuration Changes Checker",
                max_instances=1,
                coalesce=True,
                misfire_grace_time=120  # 2 minutos de gracia
            )
            
        except Exception as e:
            logger.error(f"Error iniciando scheduler: {e}")
    
    async def stop_scheduler(self):
        """Detiene el scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Background sync scheduler detenido")
        except Exception as e:
            logger.error(f"Error deteniendo scheduler: {e}")
    
    async def load_sync_configurations(self):
        """Carga todas las configuraciones y crea jobs automáticos"""
        try:
            configs = sync_config_service.get_all_configs()
            
            for config in configs:
                if config.sync_enabled:
                    await self.schedule_sync_job(
                        config.entity_type, 
                        config.sync_interval_minutes
                    )
                    
            enabled_configs = [c for c in configs if c.sync_enabled]
            logger.info(f"Configuradas {len(enabled_configs)} sincronizaciones automáticas:")
            for config in enabled_configs:
                logger.info(f"   - {config.entity_type}: cada {config.sync_interval_minutes} minutos")
            
        except Exception as e:
            logger.error(f"Error cargando configuraciones de sync: {e}")
    
    async def schedule_sync_job(self, entity_type: str, interval_minutes: int):
        """Programa un job de sincronización para una entidad específica"""
        try:
            job_id = f"sync_{entity_type.lower()}"
            
            # Remover job existente si existe
            if job_id in self.active_jobs:
                self.scheduler.remove_job(job_id)
                del self.active_jobs[job_id]
            
            # Crear nuevo job
            job = self.scheduler.add_job(
                self.sync_entity,
                IntervalTrigger(minutes=interval_minutes),
                args=[entity_type],
                id=job_id,
                name=f"Auto Sync {entity_type}",
                max_instances=1,  # Solo una instancia por entidad
                coalesce=True,    # Combinar ejecuciones pendientes
                misfire_grace_time=300  # 5 minutos de gracia para missed jobs
            )
            
            self.active_jobs[job_id] = job
            logger.info(f"Job programado para {entity_type} cada {interval_minutes} minutos")
            
        except Exception as e:
            logger.error(f"Error programando job para {entity_type}: {e}")
    
    async def remove_sync_job(self, entity_type: str):
        """Remueve un job de sincronización"""
        try:
            job_id = f"sync_{entity_type.lower()}"
            
            if job_id in self.active_jobs:
                self.scheduler.remove_job(job_id)
                del self.active_jobs[job_id]
                logger.info(f"Job removido para {entity_type}")
                
        except Exception as e:
            logger.error(f"Error removiendo job para {entity_type}: {e}")
    
    async def sync_entity(self, entity_type: str):
        """Ejecuta la sincronización para una entidad específica"""
        try:
            logger.info(f"Iniciando sincronización automática para {entity_type}")
            start_time = datetime.now()
            
            # Ejecutar sincronización OPTIMIZADA según el tipo de entidad
            result = {}
            if entity_type == "DISPATCHES":
                result = await optimized_sync_service.sync_dispatches_optimized()
            elif entity_type == "GOODS_RECEIPTS":
                result = await optimized_sync_service.sync_receipts_optimized()
            elif entity_type == "ITEMS":
                result = await optimized_sync_service.sync_items_optimized()
            elif entity_type == "PROCUREMENT_ORDERS":
                # Sincronizar órdenes de compra (usa mismas tablas que GOODS_RECEIPTS)
                result = await optimized_sync_service.sync_procurement_orders_optimized()
            elif entity_type == "DELIVERY_NOTES":
                # Envío de pedidos a SAP (DeliveryNotes)
                from app.services.sap_delivery_service import sap_delivery_service
                logger.info("DELIVERY_NOTES - Iniciando sincronización - Procesando pedidos pendientes...")
                result = await sap_delivery_service.process_pending_deliveries(dry_run=False)
                logger.info(f"DELIVERY_NOTES resultado: Procesados={result.get('processed', 0)}, Exitosos={result.get('success', 0)}, Fallidos={result.get('failed', 0)}")
                
                # Log detalles de cada pedido si hay errores
                if result.get('failed', 0) > 0:
                    for detail in result.get('details', []):
                        if not detail.get('success', True):
                            logger.error(f"ERROR - Pedido {detail.get('id_pedido')} falló: {detail.get('message')}")
                
                # Convertir formato del resultado para compatibilidad
                result = {
                    'inserted': result.get('success', 0),
                    'updated': 0,
                    'skipped': 0,
                    'errors': result.get('failed', 0)
                }
            elif entity_type == "GOODS_RECEIPTS_SENT":
                # Envío de recepciones a SAP (GoodsReceipts)
                from app.services.sap_goods_receipt_service import sap_goods_receipt_service
                logger.info("GOODS_RECEIPTS_SENT - Iniciando sincronización - Procesando recepciones pendientes...")
                result = await sap_goods_receipt_service.process_pending_receipts(dry_run=False)
                logger.info(f"GOODS_RECEIPTS_SENT resultado: Procesados={result.get('processed', 0)}, Exitosos={result.get('success', 0)}, Fallidos={result.get('failed', 0)}")
                
                # Log detalles de cada recepción si hay errores
                if result.get('failed', 0) > 0:
                    for detail in result.get('details', []):
                        if not detail.get('success', True):
                            logger.error(f"ERROR - Recepción {detail.get('id_recepcion')} falló: {detail.get('message')}")
                
                # Convertir formato del resultado para compatibilidad
                result = {
                    'inserted': result.get('success', 0),
                    'updated': 0,
                    'skipped': 0,
                    'errors': result.get('failed', 0)
                }
            
            success = result.get('errors', 0) == 0
            
            # Actualizar timestamp de última sincronización
            if success:
                sync_config_service.update_last_sync(entity_type)
                
            duration = datetime.now() - start_time
            status = "exitosa" if success else "fallida"
            logger.info(f"Sincronización automática {status} para {entity_type} en {duration.total_seconds():.2f}s")
            
        except Exception as e:
            logger.error(f"Error en sincronización automática de {entity_type}: {e}")
    
    async def check_config_changes(self):
        """Verifica cambios en la configuración y actualiza jobs"""
        logger.info("Verificando cambios en configuración de sincronización...")
        try:
            configs = sync_config_service.get_all_configs()
            current_jobs = set(self.active_jobs.keys())
            
            for config in configs:
                job_id = f"sync_{config.entity_type.lower()}"
                
                if config.sync_enabled:
                    # Si está habilitado pero no hay job, crearlo
                    if job_id not in current_jobs:
                        await self.schedule_sync_job(
                            config.entity_type, 
                            config.sync_interval_minutes
                        )
                    else:
                        # Verificar si cambió el intervalo
                        existing_job = self.scheduler.get_job(job_id)
                        if existing_job and hasattr(existing_job.trigger, 'interval'):
                            current_interval = existing_job.trigger.interval.total_seconds() / 60
                            if current_interval != config.sync_interval_minutes:
                                logger.info(f"Cambiando intervalo {config.entity_type}: {current_interval}min -> {config.sync_interval_minutes}min")
                                # Reprogramar con nuevo intervalo
                                await self.schedule_sync_job(
                                    config.entity_type, 
                                    config.sync_interval_minutes
                                )
                else:
                    # Si está deshabilitado y hay job, removerlo
                    if job_id in current_jobs:
                        await self.remove_sync_job(config.entity_type)
                        
        except Exception as e:
            logger.error(f"Error verificando cambios de configuración: {e}")
    
    def get_job_status(self) -> Dict[str, Any]:
        """Retorna el estado de todos los jobs activos"""
        status = {
            "scheduler_running": self.scheduler.running,
            "active_jobs": [],
            "next_executions": {}
        }
        
        for job_id, job in self.active_jobs.items():
            try:
                job_info = self.scheduler.get_job(job_id)
                if job_info:
                    status["active_jobs"].append({
                        "id": job_id,
                        "name": job_info.name,
                        "next_run": job_info.next_run_time.isoformat() if job_info.next_run_time else None
                    })
            except Exception as e:
                logger.error(f"Error obteniendo status de job {job_id}: {e}")
        
        return status

# Singleton instance
background_sync_service = BackgroundSyncService()