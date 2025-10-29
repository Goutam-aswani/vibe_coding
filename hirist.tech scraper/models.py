"""
Data models for job postings from Hirist.tech
"""
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class JobPosting(BaseModel):
    """
    Represents a single job posting from Hirist.tech
    """
    job_id: str = Field(..., description="Unique identifier for the job posting")
    title: str = Field(..., description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    experience: Optional[str] = Field(None, description="Required experience (e.g., '1 - 3 yrs')")
    posted_date: Optional[str] = Field(None, description="When the job was posted")
    skills: List[str] = Field(default_factory=list, description="Required skills/technologies")
    job_url: Optional[str] = Field(None, description="Direct URL to the job posting")
    company_rating: Optional[str] = Field(None, description="Company rating if available")
    reviews_count: Optional[str] = Field(None, description="Number of reviews")
    is_premium: bool = Field(default=False, description="Whether job is marked as premium")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "1566140",
                "title": "Machine Learning Engineer",
                "company": "Tech Solutions Inc",
                "location": "Bangalore",
                "experience": "1 - 3 yrs",
                "posted_date": "1 day ago",
                "skills": ["Machine Learning", "Deep Learning", "Python"],
                "job_url": "https://www.hirist.tech/j/machine-learning-engineer-1566140",
                "company_rating": "4.7",
                "reviews_count": "5+",
                "is_premium": True
            }
        }


class ScrapeResponse(BaseModel):
    """
    Response model for scraping operation
    """
    success: bool = Field(..., description="Whether scraping was successful")
    jobs_count: int = Field(..., description="Number of jobs scraped")
    jobs: List[JobPosting] = Field(default_factory=list, description="List of job postings")
    message: Optional[str] = Field(None, description="Additional message or error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "jobs_count": 20,
                "jobs": [
                    {
                        "job_id": "1566140",
                        "title": "Machine Learning Engineer",
                        "company": "Tech Solutions Inc",
                        "location": "Bangalore",
                        "experience": "1 - 3 yrs",
                        "posted_date": "1 day ago",
                        "skills": ["Machine Learning", "Deep Learning"],
                        "job_url": "https://www.hirist.tech/j/machine-learning-engineer-1566140",
                        "company_rating": "4.7",
                        "reviews_count": "5+",
                        "is_premium": True
                    }
                ],
                "message": "Successfully scraped 20 job postings"
            }
        }


class ErrorResponse(BaseModel):
    """
    Error response model
    """
    success: bool = Field(default=False, description="Always False for errors")
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Failed to fetch webpage",
                "details": "Connection timeout after 30 seconds"
            }
        }
