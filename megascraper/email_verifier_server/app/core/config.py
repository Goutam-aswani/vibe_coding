"""
Core configuration settings for the Email Verifier API
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    APP_NAME: str = "Email Verifier API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "REST API for email verification using check.emailverifier.online"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    WORKERS: int = 4
    DEBUG: bool = False
    
    # Email Verifier Settings (REQUIRED)
    EMAILVERIFIER_SESSION_COOKIE: str = ""
    EMAILVERIFIER_GA_COOKIE: Optional[str] = None
    
    # Automatic Cookie Refresh (Optional - for auto-login)
    EMAILVERIFIER_EMAIL: Optional[str] = None
    EMAILVERIFIER_PASSWORD: Optional[str] = None
    COOKIE_REFRESH_INTERVAL: int = 50  # Minutes before refresh (default: 50, expires at 60)
    AUTO_REFRESH_COOKIE: bool = True  # Enable automatic cookie refresh
    
    # Rate Limiting
    RATE_LIMIT_DELAY: float = 1.0  # Seconds between requests
    MAX_CONCURRENT: int = 5  # Max concurrent verifications
    REQUEST_TIMEOUT: int = 30  # Request timeout in seconds
    
    # Security
    API_KEY: Optional[str] = None  # If set, requires X-API-Key header
    CORS_ORIGINS: list = ["*"]  # CORS allowed origins
    
    # Redis (optional - for caching and job queue)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # Cache TTL in seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" or "text"
    
    # Job Queue
    MAX_JOB_SIZE: int = 10000  # Max emails per job
    JOB_CLEANUP_HOURS: int = 24  # Remove completed jobs after N hours
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def validate_settings():
    """Validate required settings"""
    if not settings.EMAILVERIFIER_SESSION_COOKIE:
        raise ValueError(
            "EMAILVERIFIER_SESSION_COOKIE is required! "
            "Get it from check.emailverifier.online after logging in."
        )


# Validate on import
validate_settings()
