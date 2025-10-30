from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


class FieldType(str, Enum):
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    NUMBER = "number"
    TEXTAREA = "textarea"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    FILE = "file"
    DATE = "date"


class FormField(BaseModel):
    """Represents a single form field"""
    field_id: str = Field(..., description="Unique identifier for the field")
    field_type: FieldType = Field(..., description="Type of the form field")
    label: str = Field(..., description="Label or question text")
    placeholder: Optional[str] = Field(None, description="Placeholder text if available")
    required: bool = Field(False, description="Whether the field is required")
    options: Optional[List[str]] = Field(None, description="Available options for select/radio")
    current_value: Optional[str] = Field(None, description="Pre-filled value if any")
    hint: Optional[str] = Field(None, description="Helper text or hint")


class ApplicationStep(BaseModel):
    """Represents one step in the Easy Apply process"""
    step_number: int = Field(..., description="Step number in the application flow")
    step_title: Optional[str] = Field(None, description="Title of the current step")
    fields: List[FormField] = Field(..., description="Form fields in this step")
    screenshot_path: Optional[str] = Field(None, description="Path to screenshot of this step")
    has_next_step: bool = Field(True, description="Whether there are more steps")


class JobApplicationRequest(BaseModel):
    """Request to start a job application"""
    job_url: str = Field(..., description="LinkedIn job posting URL")
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")


class FieldAnswer(BaseModel):
    """Answer to a form field"""
    field_id: str = Field(..., description="ID of the field to fill")
    value: Any = Field(..., description="Value to fill in the field")


class SubmitApplicationRequest(BaseModel):
    """Request to submit answers for a step"""
    session_id: str = Field(..., description="Session ID from start application")
    answers: List[FieldAnswer] = Field(..., description="Answers to form fields")
    continue_to_next: bool = Field(True, description="Whether to continue to next step after filling")


class ApplicationStatus(str, Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_FOR_INPUT = "waiting_for_input"


class ApplicationResponse(BaseModel):
    """Response after starting or continuing an application"""
    session_id: str = Field(..., description="Unique session identifier")
    status: ApplicationStatus = Field(..., description="Current status of the application")
    job_title: Optional[str] = Field(None, description="Title of the job")
    company_name: Optional[str] = Field(None, description="Name of the company")
    current_step: Optional[ApplicationStep] = Field(None, description="Current step data if waiting for input")
    message: str = Field(..., description="Human-readable status message")
    error: Optional[str] = Field(None, description="Error message if failed")
    total_steps: Optional[int] = Field(None, description="Total number of steps if known")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    browser_ready: bool = Field(..., description="Whether browser is initialized")
    active_sessions: int = Field(0, description="Number of active application sessions")
