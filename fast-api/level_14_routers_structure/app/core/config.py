"""
Application Configuration
=========================
Centralized settings for the application.

In production, use environment variables or .env file.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings using Pydantic BaseSettings
    
    Values can be overridden by environment variables:
    - APP_NAME=MyApp
    - DEBUG=true
    - API_KEY=secret-key
    """
    
    # Application
    APP_NAME: str = "Task Manager API"
    VERSION: str = "14.0.0"
    DEBUG: bool = True
    
    # API Settings
    API_PREFIX: str = "/api/v1"
    
    # Security
    API_KEY: str = "dev-api-key-12345"
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080"
    ]
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
