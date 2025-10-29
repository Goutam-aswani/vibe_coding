"""
FastAPI Server for Email Verification
Provides REST API endpoints for email verification using Mailmeteor
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
import asyncio
from datetime import datetime
import uuid

# You can use either implementation
# from email_checker_2captcha import EmailCheckerWith2Captcha as EmailChecker
from email_checker_playwright import EmailCheckerWithPlaywright as EmailChecker


app = FastAPI(
    title="Email Verification API",
    description="Email verification service using Mailmeteor",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Models ====================

class EmailCheckRequest(BaseModel):
    email: EmailStr
    
class BatchEmailCheckRequest(BaseModel):
    emails: List[EmailStr]

class EmailCheckResponse(BaseModel):
    email: str
    status: str
    valid: bool
    checks: Optional[Dict] = None
    checked_at: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # 'queued', 'processing', 'completed', 'failed'
    total: int
    completed: int
    results: List[Optional[EmailCheckResponse]]


# ==================== Storage ====================

# In-memory storage (replace with Redis/DB for production)
jobs: Dict[str, JobStatusResponse] = {}
email_queue = asyncio.Queue()


# ==================== Background Worker ====================

async def process_email_queue():
    """Background worker to process emails from queue"""
    # Initialize checker (choose one)
    
    # Option 1: Using Playwright (free but slower)
    checker = EmailChecker(headless=False)
    
    # Option 2: Using 2Captcha (paid but faster and more reliable)
    # checker = EmailChecker(captcha_api_key="YOUR_API_KEY")
    
    while True:
        try:
            # Get job from queue
            job_id, emails = await email_queue.get()
            
            if job_id not in jobs:
                continue
            
            jobs[job_id].status = 'processing'
            
            # Process each email
            for i, email in enumerate(emails):
                try:
                    # Check email
                    result = await checker.check_email(email)
                    
                    if result:
                        jobs[job_id].results[i] = EmailCheckResponse(
                            email=result['email'],
                            status=result['status'],
                            valid=result['valid'],
                            checks=result.get('checks'),
                            checked_at=datetime.utcnow().isoformat()
                        )
                    else:
                        jobs[job_id].results[i] = EmailCheckResponse(
                            email=email,
                            status='error',
                            valid=False,
                            checked_at=datetime.utcnow().isoformat()
                        )
                    
                    jobs[job_id].completed += 1
                    
                    # Delay between requests to respect rate limits
                    if i < len(emails) - 1:
                        await asyncio.sleep(3)
                        
                except Exception as e:
                    print(f"Error processing {email}: {str(e)}")
                    jobs[job_id].results[i] = EmailCheckResponse(
                        email=email,
                        status='error',
                        valid=False,
                        checked_at=datetime.utcnow().isoformat()
                    )
                    jobs[job_id].completed += 1
            
            # Mark job as completed
            jobs[job_id].status = 'completed'
            
        except Exception as e:
            print(f"Queue processing error: {str(e)}")
            if job_id in jobs:
                jobs[job_id].status = 'failed'


# ==================== API Endpoints ====================

@app.on_event("startup")
async def startup_event():
    """Start background worker on startup"""
    asyncio.create_task(process_email_queue())


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "Email Verification API",
        "version": "1.0.0",
        "endpoints": {
            "check_single": "/check",
            "check_batch": "/check-batch",
            "job_status": "/jobs/{job_id}"
        }
    }


@app.post("/check", response_model=EmailCheckResponse)
async def check_single_email(request: EmailCheckRequest):
    """
    Check a single email address immediately
    
    This endpoint processes the email synchronously and returns result
    May take 10-30 seconds to complete
    """
    # Initialize checker
    checker = EmailChecker(headless=False)
    
    # Check email
    result = await checker.check_email(request.email)
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to verify email")
    
    return EmailCheckResponse(
        email=result['email'],
        status=result['status'],
        valid=result['valid'],
        checks=result.get('checks'),
        checked_at=datetime.utcnow().isoformat()
    )


@app.post("/check-batch", response_model=JobStatusResponse)
async def check_batch_emails(request: BatchEmailCheckRequest):
    """
    Queue multiple emails for verification
    
    Returns a job_id that can be used to check status
    Emails are processed in background with rate limiting
    """
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Create job
    jobs[job_id] = JobStatusResponse(
        job_id=job_id,
        status='queued',
        total=len(request.emails),
        completed=0,
        results=[None] * len(request.emails)
    )
    
    # Add to queue
    await email_queue.put((job_id, request.emails))
    
    return jobs[job_id]


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get status of a batch verification job
    
    Returns current progress and results for completed emails
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "queue_size": email_queue.qsize(),
        "active_jobs": len([j for j in jobs.values() if j.status in ['queued', 'processing']])
    }


# ==================== Example Usage ====================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         Email Verification API Server                      ║
    ╚════════════════════════════════════════════════════════════╝
    
    Starting server...
    
    API Documentation: http://localhost:8000/docs
    Health Check: http://localhost:8000/health
    
    Example requests:
    
    1. Check single email:
       POST http://localhost:8000/check
       Body: {"email": "test@example.com"}
    
    2. Check batch:
       POST http://localhost:8000/check-batch
       Body: {"emails": ["test1@example.com", "test2@example.com"]}
    
    3. Get job status:
       GET http://localhost:8000/jobs/{job_id}
    
    ⚠️  Make sure to configure your email checker in the code:
       - For free: EmailCheckerWithPlaywright
       - For paid: EmailCheckerWith2Captcha (requires API key)
    """)
    
    uvicorn.run(
        "email_verification_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
