import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://frontend:3000"]
    
    # Firebird Database
    FIREBIRD_HOST: str = os.getenv("FIREBIRD_HOST", "host.docker.internal")
    FIREBIRD_PORT: int = int(os.getenv("FIREBIRD_PORT", "3050"))
    FIREBIRD_DATABASE: str = os.getenv("FIREBIRD_DATABASE", "C:\\App\\STL\\Datos\\DATOS_STL.FDB")
    FIREBIRD_USER: str = os.getenv("FIREBIRD_USER", "sysdba")
    FIREBIRD_PASSWORD: str = os.getenv("FIREBIRD_PASSWORD", "masterkey")
    
    # SAP-STL API Configuration
    SAP_STL_URL: str = os.getenv("SAP_STL_URL", "http://192.168.160.254:49568")
    SAP_STL_USERNAME: str = os.getenv("SAP_STL_USERNAME", "STLUser")
    SAP_STL_PASSWORD: str = os.getenv("SAP_STL_PASSWORD", "7a6T9IVeUdf5bvRIv")
    
    @property
    def firebird_url(self) -> str:
        return f"firebird://{self.FIREBIRD_USER}:{self.FIREBIRD_PASSWORD}@{self.FIREBIRD_HOST}:{self.FIREBIRD_PORT}/{self.FIREBIRD_DATABASE}"
    
    class Config:
        env_file = ".env"

settings = Settings()