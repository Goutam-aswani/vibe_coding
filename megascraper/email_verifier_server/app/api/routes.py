"""
API route handlers
"""

import time
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.models.requests import (
    EmailVerifyRequest,
    BatchVerifyRequest,
    JobCreateRequest
)
from app.models.responses import (
    EmailVerifyResponse,
    BatchVerifyResponse,
    JobCreateResponse,
    JobStatusResponse,
    JobResultsResponse,
    HealthCheckResponse,
    EmailStatus,
    JobStatus
)
from app.core.security import verify_api_key
from app.services.verifier import EmailVerifierService
from app.services.queue import JobQueue
from app.api.dependencies import get_verifier, get_queue
from app.core.config import settings

# Create router
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Health check endpoint"
)
async def health_check(verifier: EmailVerifierService = Depends(get_verifier)):
    """
    Check API health and service availability
    """
    session_valid = await verifier.health_check()
    
    return HealthCheckResponse(
        status="healthy" if session_valid else "degraded",
        version=settings.APP_VERSION,
        session_valid=session_valid
    )


@router.post(
    "/api/v1/verify",
    response_model=EmailVerifyResponse,
    tags=["Email Verification"],
    summary="Verify a single email address",
    dependencies=[Depends(verify_api_key)]
)
async def verify_single_email(
    request: EmailVerifyRequest,
    verifier: EmailVerifierService = Depends(get_verifier)
):
    """
    Verify a single email address
    
    - **email**: Email address to verify
    - **include_debug**: Include SMTP debug information
    
    Returns verification result with status, type, and safety information.
    """
    result = await verifier.verify_email(request.email)
    
    # Filter debug info if not requested
    if not request.include_debug:
        result['debug'] = None
    
    return EmailVerifyResponse(**result)


@router.post(
    "/api/v1/verify/batch",
    response_model=BatchVerifyResponse,
    tags=["Email Verification"],
    summary="Verify multiple emails concurrently",
    dependencies=[Depends(verify_api_key)]
)
async def verify_batch(
    request: BatchVerifyRequest,
    verifier: EmailVerifierService = Depends(get_verifier)
):
    """
    Verify multiple email addresses concurrently (up to 100 emails)
    
    - **emails**: List of email addresses to verify
    - **max_concurrent**: Maximum concurrent verifications (1-20)
    - **include_debug**: Include SMTP debug information
    
    Returns batch results with summary statistics.
    """
    start_time = time.time()
    
    # Verify all emails
    results = await verifier.verify_batch(request.emails, request.max_concurrent)
    
    # Filter debug info if not requested
    if not request.include_debug:
        for result in results:
            result['debug'] = None
    
    # Calculate statistics
    total = len(results)
    valid = sum(1 for r in results if r.get('status') == 'valid')
    invalid = sum(1 for r in results if r.get('status') == 'invalid')
    errors = sum(1 for r in results if r.get('status') == 'error')
    processing_time_ms = int((time.time() - start_time) * 1000)
    
    return BatchVerifyResponse(
        total=total,
        processed=total,
        valid=valid,
        invalid=invalid,
        errors=errors,
        processing_time_ms=processing_time_ms,
        results=[EmailVerifyResponse(**r) for r in results]
    )


@router.post(
    "/api/v1/jobs",
    response_model=JobCreateResponse,
    tags=["Background Jobs"],
    summary="Create a background verification job",
    dependencies=[Depends(verify_api_key)]
)
async def create_job(
    request: JobCreateRequest,
    queue: JobQueue = Depends(get_queue)
):
    """
    Create a background job for verifying large batches of emails
    
    - **emails**: List of email addresses to verify (up to 10,000)
    - **webhook_url**: Optional webhook URL to call when job completes
    - **max_concurrent**: Maximum concurrent verifications (1-20)
    
    Returns job ID for tracking progress.
    """
    # Validate job size
    if len(request.emails) > settings.MAX_JOB_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum job size is {settings.MAX_JOB_SIZE} emails"
        )
    
    # Create job
    job_id = queue.create_job(
        emails=request.emails,
        webhook_url=request.webhook_url,
        max_concurrent=request.max_concurrent
    )
    
    job = queue.get_job(job_id)
    
    return JobCreateResponse(
        job_id=job.job_id,
        status=job.status,
        total_emails=job.total,
        created_at=job.created_at
    )


@router.get(
    "/api/v1/jobs/{job_id}",
    response_model=JobStatusResponse,
    tags=["Background Jobs"],
    summary="Get job status",
    dependencies=[Depends(verify_api_key)]
)
async def get_job_status(
    job_id: str,
    queue: JobQueue = Depends(get_queue)
):
    """
    Get the status of a background job
    
    - **job_id**: Job identifier
    
    Returns current job status and progress.
    """
    job = queue.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    return JobStatusResponse(**job.to_dict())


@router.get(
    "/api/v1/jobs/{job_id}/results",
    response_model=JobResultsResponse,
    tags=["Background Jobs"],
    summary="Get job results",
    dependencies=[Depends(verify_api_key)]
)
async def get_job_results(
    job_id: str,
    queue: JobQueue = Depends(get_queue)
):
    """
    Get the results of a completed job
    
    - **job_id**: Job identifier
    
    Returns all verification results for the job.
    """
    job = queue.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    if job.status not in [JobStatus.COMPLETED, JobStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not completed yet. Status: {job.status.value}"
        )
    
    results = queue.get_job_results(job_id)
    
    return JobResultsResponse(
        job_id=job_id,
        results=[EmailVerifyResponse(**r) for r in results],
        total=len(results)
    )


@router.delete(
    "/api/v1/jobs/{job_id}",
    tags=["Background Jobs"],
    summary="Cancel a job",
    dependencies=[Depends(verify_api_key)]
)
async def cancel_job(
    job_id: str,
    queue: JobQueue = Depends(get_queue)
):
    """
    Cancel a running job
    
    - **job_id**: Job identifier
    
    Returns success message if job was cancelled.
    """
    success = queue.cancel_job(job_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    return {"message": f"Job {job_id} cancelled successfully"}
