"""
FastAPI application for Email Verifier API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging

from app.core.config import settings
from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📝 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"🔐 API Key Required: {'Yes' if settings.API_KEY else 'No (Open Access)'}")
    logger.info(f"⚙️  Rate Limit: {settings.RATE_LIMIT_DELAY}s between requests")
    logger.info(f"⚡ Max Concurrent: {settings.MAX_CONCURRENT} verifications")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"👋 Shutting down {settings.APP_NAME}")


@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Basic metrics endpoint (can be extended with prometheus_client)"""
    from app.services.queue import get_job_queue
    
    queue = get_job_queue()
    
    total_jobs = len(queue.jobs)
    pending = sum(1 for j in queue.jobs.values() if j.status.value == "pending")
    processing = sum(1 for j in queue.jobs.values() if j.status.value == "processing")
    completed = sum(1 for j in queue.jobs.values() if j.status.value == "completed")
    failed = sum(1 for j in queue.jobs.values() if j.status.value == "failed")
    
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "jobs": {
            "total": total_jobs,
            "pending": pending,
            "processing": processing,
            "completed": completed,
            "failed": failed
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS
    )
