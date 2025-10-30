"""
Pydantic models for job scraper API
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime


class Location(BaseModel):
    """Job location information"""
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    lat_lon: Optional[str] = Field(None, description="Latitude and longitude")


class Salary(BaseModel):
    """Salary information"""
    currency: str = "INR"
    minimum: float = Field(0, description="Minimum salary")
    maximum: float = Field(0, description="Maximum salary")
    is_disclosed: bool = Field(False, description="Whether salary is disclosed")


class Experience(BaseModel):
    """Experience requirements"""
    minimum_years: int = Field(0, description="Minimum years of experience")
    maximum_years: int = Field(0, description="Maximum years of experience")


class Company(BaseModel):
    """Company information"""
    name: str
    company_id: int
    logo_url: Optional[str] = None


class Skill(BaseModel):
    """Skill information"""
    name: str
    skill_id: Optional[str] = None


class Job(BaseModel):
    """Complete job listing information"""
    job_id: str
    title: str
    company: Company
    locations: List[Location]
    description: str = Field(..., description="Full job description (HTML)")
    experience: Experience
    salary: Salary
    skills: List[Skill] = Field(default_factory=list)
    it_skills: List[Skill] = Field(default_factory=list)
    apply_url: str = Field(..., description="Direct application link")
    posted_date: datetime
    job_types: List[str] = Field(default_factory=list, description="e.g., Permanent Job")
    employment_types: List[str] = Field(default_factory=list, description="e.g., Full time")
    industries: List[str] = Field(default_factory=list)
    functions: List[str] = Field(default_factory=list)


class ScrapeRequest(BaseModel):
    """Request model for scraping jobs"""
    job_roles: List[str] = Field(
        ..., 
        min_length=1,
        description="List of job roles to search (e.g., ['gen ai engineer', 'data scientist'])",
        example=["gen ai engineer", "machine learning engineer"]
    )
    experience_range: Optional[str] = Field(
        "0~0",
        description="Experience range in format 'min~max' (e.g., '0~0', '2~5')",
        example="0~0"
    )
    country: str = Field(
        "India",
        description="Country to search jobs in"
    )
    limit_per_role: int = Field(
        100,
        ge=1,
        le=100,
        description="Maximum number of jobs to fetch per role (1-100)"
    )


class ScrapeStats(BaseModel):
    """Statistics about the scraping operation"""
    total_jobs_found: int
    jobs_per_role: dict[str, int]
    total_roles_searched: int
    execution_time_seconds: float
    timestamp: datetime


class ScrapeResponse(BaseModel):
    """Response model for scraping jobs"""
    success: bool
    message: str
    stats: ScrapeStats
    jobs: List[Job]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str = "1.0.0"
