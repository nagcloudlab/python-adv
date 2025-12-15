"""
Application Configuration
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Task Manager API"
    VERSION: str = "15.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./tasks.db"
    
    # For PostgreSQL (example):
    # DATABASE_URL: str = "postgresql://user:password@localhost/dbname"
    
    # For MySQL (example):
    # DATABASE_URL: str = "mysql+pymysql://user:password@localhost/dbname"
    
    class Config:
        env_file = ".env"


settings = Settings()
