"""
API route dependencies
"""

from app.services.verifier import get_verifier_service
from app.services.queue import get_job_queue


def get_verifier():
    """Dependency for getting verifier service"""
    return get_verifier_service()


def get_queue():
    """Dependency for getting job queue"""
    return get_job_queue()
