from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    hashed_password: str = ""
    is_active: bool = True
    role: str = "OPERADOR"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None