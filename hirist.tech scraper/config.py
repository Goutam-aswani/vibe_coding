"""
Configuration settings for the scraper
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings
    """
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Request configuration
    request_timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # API configuration
    api_title: str = "Hirist.tech Job Scraper API"
    api_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
