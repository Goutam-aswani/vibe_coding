"""
Background job queue manager for processing large batches
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

from app.models.responses import JobStatus
from app.services.verifier import get_verifier_service


class Job:
    """Background job for email verification"""
    
    def __init__(self, job_id: str, emails: List[str], webhook_url: Optional[str] = None, max_concurrent: int = 5):
        self.job_id = job_id
        self.emails = emails
        self.webhook_url = webhook_url
        self.max_concurrent = max_concurrent
        
        self.status = JobStatus.PENDING
        self.total = len(emails)
        self.processed = 0
        self.valid = 0
        self.invalid = 0
        self.errors = 0
        self.results: List[Dict] = []
        
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
    
    @property
    def progress(self) -> float:
        """Calculate progress percentage"""
        if self.total == 0:
            return 100.0
        return (self.processed / self.total) * 100
    
    def to_dict(self) -> Dict:
        """Convert job to dictionary"""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "total": self.total,
            "processed": self.processed,
            "valid": self.valid,
            "invalid": self.invalid,
            "errors": self.errors,
            "progress": round(self.progress, 2),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message
        }


class JobQueue:
    """In-memory job queue manager"""
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}
    
    def create_job(self, emails: List[str], webhook_url: Optional[str] = None, max_concurrent: int = 5) -> str:
        """
        Create a new background job
        
        Args:
            emails: List of emails to verify
            webhook_url: Optional webhook URL to call when complete
            max_concurrent: Max concurrent verifications
        
        Returns:
            str: Job ID
        """
        job_id = str(uuid.uuid4())
        job = Job(job_id, emails, webhook_url, max_concurrent)
        self.jobs[job_id] = job
        
        # Start processing in background
        task = asyncio.create_task(self._process_job(job))
        self.processing_tasks[job_id] = task
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get job status"""
        job = self.get_job(job_id)
        return job.to_dict() if job else None
    
    def get_job_results(self, job_id: str) -> Optional[List[Dict]]:
        """Get job results"""
        job = self.get_job(job_id)
        return job.results if job else None
    
    async def _process_job(self, job: Job):
        """
        Process a job in the background
        
        Args:
            job: Job to process
        """
        try:
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.utcnow()
            
            # Get verifier service
            verifier = get_verifier_service()
            
            # Verify all emails
            results = await verifier.verify_batch(job.emails, job.max_concurrent)
            
            # Update job with results
            job.results = results
            job.processed = len(results)
            
            # Count statuses
            for result in results:
                status = result.get('status', 'error')
                if status == 'valid':
                    job.valid += 1
                elif status == 'invalid':
                    job.invalid += 1
                else:
                    job.errors += 1
            
            # Mark as completed
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            # Call webhook if provided
            if job.webhook_url:
                await self._call_webhook(job)
                
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
        finally:
            # Remove from processing tasks
            if job.job_id in self.processing_tasks:
                del self.processing_tasks[job.job_id]
    
    async def _call_webhook(self, job: Job):
        """Call webhook with job results"""
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                await client.post(
                    job.webhook_url,
                    json={
                        "job_id": job.job_id,
                        "status": job.status.value,
                        "total": job.total,
                        "valid": job.valid,
                        "invalid": job.invalid,
                        "errors": job.errors,
                        "completed_at": job.completed_at.isoformat() if job.completed_at else None
                    }
                )
        except Exception as e:
            # Log webhook error but don't fail the job
            print(f"Webhook error for job {job.job_id}: {e}")
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running job
        
        Args:
            job_id: Job ID to cancel
        
        Returns:
            bool: True if cancelled successfully
        """
        job = self.get_job(job_id)
        if not job:
            return False
        
        # Cancel the task if it's running
        if job_id in self.processing_tasks:
            task = self.processing_tasks[job_id]
            task.cancel()
            del self.processing_tasks[job_id]
        
        # Update job status
        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.utcnow()
        
        return True
    
    def cleanup_old_jobs(self, hours: int = 24):
        """Remove completed jobs older than N hours"""
        now = datetime.utcnow()
        to_remove = []
        
        for job_id, job in self.jobs.items():
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                if job.completed_at:
                    age_hours = (now - job.completed_at).total_seconds() / 3600
                    if age_hours > hours:
                        to_remove.append(job_id)
        
        for job_id in to_remove:
            del self.jobs[job_id]
        
        return len(to_remove)


# Global job queue instance
_job_queue: Optional[JobQueue] = None


def get_job_queue() -> JobQueue:
    """
    Get or create the global job queue instance
    
    Returns:
        JobQueue: The job queue
    """
    global _job_queue
    if _job_queue is None:
        _job_queue = JobQueue()
    return _job_queue
