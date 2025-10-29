"""
Response models for API endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EmailStatus(str, Enum):
    """Email verification status"""
    VALID = "valid"
    INVALID = "invalid"
    ERROR = "error"
    UNKNOWN = "unknown"


class JobStatus(str, Enum):
    """Background job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EmailVerifyResponse(BaseModel):
    """Single email verification response"""
    
    email: str = Field(..., description="Email address that was verified")
    status: EmailStatus = Field(..., description="Verification status")
    safetosend: str = Field(..., description="Safe to send email? Yes/No/Unknown")
    type: str = Field(..., description="Email account type (Free Account, Business, etc.)")
    reasons: str = Field(..., description="Success or failure reason")
    debug: Optional[List[str]] = Field(default=None, description="SMTP debug messages")
    verified_at: datetime = Field(default_factory=datetime.utcnow, description="Verification timestamp")
    processing_time_ms: Optional[int] = Field(default=None, description="Processing time in milliseconds")


class BatchVerifyResponse(BaseModel):
    """Batch verification response"""
    
    total: int = Field(..., description="Total emails in batch")
    processed: int = Field(..., description="Number of emails processed")
    valid: int = Field(..., description="Number of valid emails")
    invalid: int = Field(..., description="Number of invalid emails")
    errors: int = Field(..., description="Number of errors")
    processing_time_ms: int = Field(..., description="Total processing time in milliseconds")
    results: List[EmailVerifyResponse] = Field(..., description="Individual verification results")


class JobCreateResponse(BaseModel):
    """Job creation response"""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    total_emails: int = Field(..., description="Total emails to process")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation timestamp")


class JobStatusResponse(BaseModel):
    """Job status response"""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    total: int = Field(..., description="Total emails in job")
    processed: int = Field(..., description="Number of emails processed")
    valid: int = Field(..., description="Number of valid emails")
    invalid: int = Field(..., description="Number of invalid emails")
    errors: int = Field(..., description="Number of errors")
    progress: float = Field(..., description="Progress percentage (0-100)")
    created_at: datetime = Field(..., description="Job creation timestamp")
    started_at: Optional[datetime] = Field(default=None, description="Job start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Job completion timestamp")
    error_message: Optional[str] = Field(default=None, description="Error message if job failed")


class JobResultsResponse(BaseModel):
    """Job results response"""
    
    job_id: str = Field(..., description="Unique job identifier")
    results: List[EmailVerifyResponse] = Field(..., description="Verification results")
    total: int = Field(..., description="Total results")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    
    status: str = Field(..., description="Health status (healthy/unhealthy)")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current server time")
    session_valid: bool = Field(..., description="Email verifier session is valid")
    uptime_seconds: Optional[float] = Field(default=None, description="Server uptime in seconds")


class ErrorResponse(BaseModel):
    """Error response"""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[Any] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
