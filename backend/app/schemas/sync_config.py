from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SyncConfigBase(BaseModel):
    entity_type: str
    sync_enabled: str = 'Y'
    sync_interval_minutes: int = 60
    batch_size: int = 100
    max_retries: int = 3
    api_endpoint: str

class SyncConfigCreate(SyncConfigBase):
    pass

class SyncConfigUpdate(BaseModel):
    sync_enabled: Optional[str] = None
    sync_interval_minutes: Optional[int] = None
    batch_size: Optional[int] = None
    max_retries: Optional[int] = None
    api_endpoint: Optional[str] = None

class SyncConfigResponse(SyncConfigBase):
    id: int
    last_sync_at: Optional[datetime] = None
    next_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True