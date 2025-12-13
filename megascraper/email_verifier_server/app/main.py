"""
FastAPI application for Email Verifier API
"""

# Fix for Python 3.13+ on Windows with asyncio subprocess
import sys
if sys.platform == 'win32' and sys.version_info >= (3, 13):
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging
import os
from pathlib import Path
from dotenv import set_key

from app.core.config import settings
from app.api.routes import router
from app.services.cookie_fetcher import fetch_cookie_cli

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


async def refresh_cookie_on_startup():
    """Refresh the session cookie on server startup"""
    try:
        logger.info("🔄 Refreshing session cookie on startup...")
        
        email = settings.EMAILVERIFIER_EMAIL
        password = settings.EMAILVERIFIER_PASSWORD
        
        if not email or not password:
            logger.warning("⚠️  Cookie auto-refresh skipped: EMAILVERIFIER_EMAIL or EMAILVERIFIER_PASSWORD not set in .env")
            logger.warning("💡 Set these credentials to enable automatic cookie refresh on startup")
            return
        
        # Fetch new cookie (headless mode for server startup)
        cookie = await fetch_cookie_cli(email, password, headless=True)
        
        if not cookie:
            logger.error("❌ Failed to refresh cookie on startup")
            logger.warning("⚠️  Server will continue with existing cookie from .env")
            return
        
        # Update .env file with new cookie
        env_path = Path(__file__).parent.parent / ".env"
        
        if not env_path.exists():
            logger.error("❌ .env file not found, cannot update cookie")
            return
        
        set_key(env_path, "EMAILVERIFIER_SESSION_COOKIE", cookie)
        
        # Update the settings in memory
        settings.EMAILVERIFIER_SESSION_COOKIE = cookie
        
        logger.info("✅ Cookie refreshed and updated successfully!")
        logger.info(f"   New Cookie: {cookie[:30]}... (truncated)")
        
    except Exception as e:
        logger.error(f"❌ Error refreshing cookie on startup: {e}")
        logger.warning("⚠️  Server will continue with existing cookie from .env")


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📝 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"🔐 API Key Required: {'Yes' if settings.API_KEY else 'No (Open Access)'}")
    logger.info(f"⚙️  Rate Limit: {settings.RATE_LIMIT_DELAY}s between requests")
    logger.info(f"⚡ Max Concurrent: {settings.MAX_CONCURRENT} verifications")
    
    # Refresh cookie on startup
    await refresh_cookie_on_startup()


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
