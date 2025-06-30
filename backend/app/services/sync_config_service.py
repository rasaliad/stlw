from typing import List, Optional
from datetime import datetime, timedelta, timezone
import time
import logging
from app.schemas.sync_config import SyncConfigCreate, SyncConfigUpdate, SyncConfigResponse
from app.core.database import db

logger = logging.getLogger(__name__)

class SyncConfigService:
    def get_all_configs(self) -> List[SyncConfigResponse]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT ID, ENTITY_TYPE, SYNC_ENABLED, SYNC_INTERVAL_MINUTES, 
                       LAST_SYNC_AT, NEXT_SYNC_AT, BATCH_SIZE, MAX_RETRIES, 
                       API_ENDPOINT, CREATED_AT, UPDATED_AT 
                FROM STL_SYNC_CONFIG 
                ORDER BY ENTITY_TYPE
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            configs = []
            for row in results:
                configs.append(SyncConfigResponse(
                    id=row[0],
                    entity_type=row[1],
                    sync_enabled=row[2],
                    sync_interval_minutes=row[3],
                    last_sync_at=row[4],
                    next_sync_at=row[5],
                    batch_size=row[6],
                    max_retries=row[7],
                    api_endpoint=row[8],
                    created_at=row[9],
                    updated_at=row[10]
                ))
            return configs
    
    def get_config_by_entity(self, entity_type: str) -> Optional[SyncConfigResponse]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT ID, ENTITY_TYPE, SYNC_ENABLED, SYNC_INTERVAL_MINUTES, 
                       LAST_SYNC_AT, NEXT_SYNC_AT, BATCH_SIZE, MAX_RETRIES, 
                       API_ENDPOINT, CREATED_AT, UPDATED_AT 
                FROM STL_SYNC_CONFIG 
                WHERE ENTITY_TYPE = ?
            """
            cursor.execute(query, (entity_type,))
            result = cursor.fetchone()
            
            if result:
                return SyncConfigResponse(
                    id=result[0],
                    entity_type=result[1],
                    sync_enabled=result[2],
                    sync_interval_minutes=result[3],
                    last_sync_at=result[4],
                    next_sync_at=result[5],
                    batch_size=result[6],
                    max_retries=result[7],
                    api_endpoint=result[8],
                    created_at=result[9],
                    updated_at=result[10]
                )
            return None
    
    def update_config(self, entity_type: str, config_data: SyncConfigUpdate) -> Optional[SyncConfigResponse]:
        existing_config = self.get_config_by_entity(entity_type)
        if not existing_config:
            return None
        
        update_fields = []
        params = []
        
        if config_data.sync_enabled is not None:
            update_fields.append("SYNC_ENABLED = ?")
            params.append(config_data.sync_enabled)
        
        if config_data.sync_interval_minutes is not None:
            update_fields.append("SYNC_INTERVAL_MINUTES = ?")
            params.append(config_data.sync_interval_minutes)
            # Actualizar próxima sincronización (usar timezone local)
            now = datetime.now()
            next_sync = now + timedelta(minutes=config_data.sync_interval_minutes)
            update_fields.append("NEXT_SYNC_AT = ?")
            params.append(next_sync)
        
        if config_data.batch_size is not None:
            update_fields.append("BATCH_SIZE = ?")
            params.append(config_data.batch_size)
        
        if config_data.max_retries is not None:
            update_fields.append("MAX_RETRIES = ?")
            params.append(config_data.max_retries)
        
        if config_data.api_endpoint is not None:
            update_fields.append("API_ENDPOINT = ?")
            params.append(config_data.api_endpoint)
        
        if update_fields:
            update_fields.append("UPDATED_AT = ?")
            params.append(now if 'now' in locals() else datetime.now())
            params.append(entity_type)
            
            # Retry logic for deadlock handling
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        query = f"UPDATE STL_SYNC_CONFIG SET {', '.join(update_fields)} WHERE ENTITY_TYPE = ?"
                        cursor.execute(query, tuple(params))
                        conn.commit()
                        break
                except Exception as e:
                    if "deadlock" in str(e).lower() and attempt < max_retries - 1:
                        logger.warning(f"Deadlock detected on attempt {attempt + 1}, retrying in {0.1 * (attempt + 1)} seconds")
                        time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        logger.error(f"Failed to update config after {attempt + 1} attempts: {e}")
                        raise
        
        return self.get_config_by_entity(entity_type)
    
    def update_last_sync(self, entity_type: str) -> bool:
        """Actualiza la última sincronización y calcula la próxima"""
        config = self.get_config_by_entity(entity_type)
        if not config:
            return False
        
        now = datetime.now()
        next_sync = now + timedelta(minutes=config.sync_interval_minutes)
        
        # Retry logic for deadlock handling
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    query = """
                        UPDATE STL_SYNC_CONFIG 
                        SET LAST_SYNC_AT = ?, NEXT_SYNC_AT = ?, UPDATED_AT = ?
                        WHERE ENTITY_TYPE = ?
                    """
                    cursor.execute(query, (now, next_sync, now, entity_type))
                    conn.commit()
                    return True
            except Exception as e:
                if "deadlock" in str(e).lower() and attempt < max_retries - 1:
                    logger.warning(f"Deadlock detected in update_last_sync on attempt {attempt + 1}, retrying")
                    time.sleep(0.1 * (attempt + 1))
                    continue
                else:
                    logger.error(f"Failed to update last sync after {attempt + 1} attempts: {e}")
                    return False
        
        return False

sync_config_service = SyncConfigService()