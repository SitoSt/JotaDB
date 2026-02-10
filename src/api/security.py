"""
Security utilities for API authentication.

Provides Bearer token validation for protecting API endpoints.
"""
from fastapi import Header, HTTPException, status
from typing import Optional
import os


async def verify_api_key(
    authorization: Optional[str] = Header(None, description="Bearer API Key")
) -> bool:
    """
    Validates Bearer API Key from Authorization header.
    
    Expected format: "Authorization: Bearer <API_SECRET_KEY>"
    
    Args:
        authorization: Authorization header value
        
    Returns:
        True if authentication is successful
        
    Raises:
        HTTPException: 401 if header is missing or invalid format
        HTTPException: 403 if API key is invalid
        HTTPException: 500 if API_SECRET_KEY is not configured
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Parse "Bearer <token>" format
    parts = authorization.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = parts[1]
    
    # Get expected key from environment
    expected_key = os.getenv("API_SECRET_KEY")
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API_SECRET_KEY not configured on server"
        )
    
    # Validate token
    if token != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return True
