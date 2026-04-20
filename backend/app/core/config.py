"""Application configuration settings."""
import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"]
    )
    ALLOWED_HOSTS: List[str] = Field(default=["localhost", "127.0.0.1"])
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://grineos:grineos@localhost/grineos_db"
    )
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # OpenAI for AI Agent
    OPENAI_API_KEY: Optional[str] = None
    
    # Grine Engine Settings
    REGIME_CACHE_TTL: int = Field(default=300)  # 5 minutes
    ALLOCATION_CACHE_TTL: int = Field(default=60)  # 1 minute
    DEFAULT_TURNOVER_CAP: float = Field(default=0.15)
    DEFAULT_OPTIMIZER_OBJECTIVE: str = Field(default="min_variance")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
