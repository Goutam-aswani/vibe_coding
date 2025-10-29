"""
Security utilities for API authentication and authorization
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Verify API key if authentication is enabled
    
    Args:
        api_key: API key from X-API-Key header
    
    Raises:
        HTTPException: If API key is invalid or missing
    
    Returns:
        str: The validated API key
    """
    # If no API_KEY is configured, allow all requests
    if not settings.API_KEY:
        return None
    
    # If API_KEY is configured, require and validate it
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Include X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )
    
    return api_key
