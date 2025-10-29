"""
Request models for API endpoints
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional


class EmailVerifyRequest(BaseModel):
    """Single email verification request"""
    
    email: EmailStr = Field(
        ...,
        description="Email address to verify",
        example="test@example.com"
    )
    
    include_debug: bool = Field(
        default=False,
        description="Include SMTP debug information in response"
    )


class BatchVerifyRequest(BaseModel):
    """Batch email verification request"""
    
    emails: List[EmailStr] = Field(
        ...,
        description="List of email addresses to verify",
        min_items=1,
        max_items=100,
        example=["user1@example.com", "user2@example.com"]
    )
    
    max_concurrent: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum concurrent verifications (1-20)"
    )
    
    include_debug: bool = Field(
        default=False,
        description="Include SMTP debug information in responses"
    )
    
    @validator('emails')
    def validate_emails_unique(cls, v):
        """Ensure emails are unique"""
        if len(v) != len(set(v)):
            raise ValueError("Duplicate emails found in batch")
        return v


class JobCreateRequest(BaseModel):
    """Background job creation request"""
    
    emails: List[EmailStr] = Field(
        ...,
        description="List of email addresses to verify",
        min_items=1,
        max_items=10000,
        example=["user1@example.com", "user2@example.com"]
    )
    
    webhook_url: Optional[str] = Field(
        default=None,
        description="Webhook URL to call when job completes",
        example="https://yourapp.com/webhook/email-verification"
    )
    
    max_concurrent: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum concurrent verifications (1-20)"
    )
    
    @validator('emails')
    def validate_emails_unique(cls, v):
        """Ensure emails are unique"""
        if len(v) != len(set(v)):
            raise ValueError("Duplicate emails found")
        return v
    
    @validator('webhook_url')
    def validate_webhook_url(cls, v):
        """Validate webhook URL format"""
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError("Webhook URL must start with http:// or https://")
        return v


class HealthCheckRequest(BaseModel):
    """Health check request (no body needed)"""
    pass
