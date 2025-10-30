import asyncio
import sys
import logging
import uuid
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Fix for Python 3.13+ on Windows with Playwright
# MUST be set before any async operations or imports
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except AttributeError:
        pass

from src.models import (
    JobApplicationRequest, 
    SubmitApplicationRequest, 
    ApplicationResponse,
    ApplicationStatus,
    ApplicationStep,
    HealthResponse
)
from src.browser_manager import BrowserManager
from src.question_extractor import QuestionExtractor
from src.form_filler import FormFiller

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global browser manager
browser_manager: Optional[BrowserManager] = None

# Store active sessions
active_sessions: Dict[str, Dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global browser_manager
    
    # Startup
    logger.info("Starting LinkedIn Automation Service...")
    browser_manager = BrowserManager()
    
    initialized = await browser_manager.initialize()
    if initialized:
        logger.info("Browser initialized successfully")
        # Check if user is logged in
        logged_in = await browser_manager.ensure_logged_in()
        if logged_in:
            logger.info("User is logged in to LinkedIn")
        else:
            logger.warning("User needs to log in to LinkedIn manually")
    else:
        logger.error("Failed to initialize browser")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    if browser_manager:
        await browser_manager.close()


app = FastAPI(
    title="LinkedIn Easy Apply Automation",
    description="Automate LinkedIn Easy Apply applications with AI-powered form filling",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check service health"""
    return HealthResponse(
        status="healthy" if browser_manager else "unhealthy",
        browser_ready=browser_manager is not None,
        active_sessions=len(active_sessions)
    )


@app.post("/start-application", response_model=ApplicationResponse)
async def start_application(request: JobApplicationRequest):
    """
    Start a job application process
    - Navigates to the job URL
    - Clicks Easy Apply
    - Extracts all form fields from the first step
    - Returns fields as JSON for AI processing
    """
    global browser_manager, active_sessions
    
    if not browser_manager:
        raise HTTPException(status_code=503, message="Browser not initialized")
    
    # Generate session ID
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        logger.info(f"Starting application for session {session_id}: {request.job_url}")
        
        # Navigate to job
        success = await browser_manager.navigate_to_job(request.job_url)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to navigate to job URL")
        
        # Take screenshot of job page
        await browser_manager.take_screenshot(f"{session_id}_job_page")
        
        # Extract job title and company
        page = browser_manager.get_page()
        job_title = None
        company_name = None
        
        try:
            job_title_elem = await page.locator('h1.job-title, h1.jobs-unified-top-card__job-title').first.text_content(timeout=3000)
            if job_title_elem:
                job_title = job_title_elem.strip()
        except:
            pass
        
        try:
            company_elem = await page.locator('.job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name a').first.text_content(timeout=3000)
            if company_elem:
                company_name = company_elem.strip()
        except:
            pass
        
        # Click Easy Apply
        clicked = await browser_manager.click_easy_apply()
        if not clicked:
            return ApplicationResponse(
                session_id=session_id,
                status=ApplicationStatus.FAILED,
                job_title=job_title,
                company_name=company_name,
                message="Easy Apply button not found or job not available for Easy Apply",
                error="Easy Apply not available"
            )
        
        # Wait for modal to load
        await asyncio.sleep(2)
        
        # Take screenshot of modal
        await browser_manager.take_screenshot(f"{session_id}_step_1")
        
        # Extract form fields
        extractor = QuestionExtractor(page)
        
        step_info = await extractor.get_current_step_info()
        fields = await extractor.extract_all_fields()
        has_next = await extractor.check_has_next_step()
        
        # Create application step
        current_step = ApplicationStep(
            step_number=step_info['step_number'],
            step_title=step_info['step_title'],
            fields=fields,
            screenshot_path=f"screenshots/{session_id}_step_1.png",
            has_next_step=has_next
        )
        
        # Store session data
        active_sessions[session_id] = {
            'job_url': request.job_url,
            'job_title': job_title,
            'company_name': company_name,
            'current_step': 1,
            'fields': {field.field_id: {'type': field.field_type, 'label': field.label} for field in fields}
        }
        
        return ApplicationResponse(
            session_id=session_id,
            status=ApplicationStatus.WAITING_FOR_INPUT,
            job_title=job_title,
            company_name=company_name,
            current_step=current_step,
            message=f"Extracted {len(fields)} fields from step {step_info['step_number']}. Waiting for answers.",
            total_steps=step_info.get('total_steps')
        )
        
    except Exception as e:
        logger.error(f"Error starting application: {e}", exc_info=True)
        
        # Cleanup session
        if session_id in active_sessions:
            del active_sessions[session_id]
        
        raise HTTPException(status_code=500, detail=f"Application start failed: {str(e)}")


@app.post("/submit-application", response_model=ApplicationResponse)
async def submit_application(request: SubmitApplicationRequest):
    """
    Submit answers for the current step
    - Fills in the provided answers
    - Clicks Next/Review/Submit as appropriate
    - If more steps exist, extracts fields from next step
    - Returns next step fields or completion status
    """
    global browser_manager, active_sessions
    
    if not browser_manager:
        raise HTTPException(status_code=503, detail="Browser not initialized")
    
    session_id = request.session_id
    
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    session_data = active_sessions[session_id]
    
    try:
        logger.info(f"Submitting answers for session {session_id}")
        
        page = browser_manager.get_page()
        filler = FormFiller(page)
        
        # Fill all provided answers
        for answer in request.answers:
            field_info = session_data['fields'].get(answer.field_id, {})
            success = await filler.fill_field(answer, field_info)
            if not success:
                logger.warning(f"Failed to fill field {answer.field_id}")
        
        await asyncio.sleep(1)
        
        # Take screenshot after filling
        step_num = session_data['current_step']
        await browser_manager.take_screenshot(f"{session_id}_step_{step_num}_filled")
        
        if not request.continue_to_next:
            # Just fill fields, don't proceed
            return ApplicationResponse(
                session_id=session_id,
                status=ApplicationStatus.IN_PROGRESS,
                job_title=session_data['job_title'],
                company_name=session_data['company_name'],
                message="Fields filled. Waiting for continue command."
            )
        
        # Check what button to click
        extractor = QuestionExtractor(page)
        has_next = await extractor.check_has_next_step()
        has_review = await extractor.check_has_review_button()
        
        if has_review:
            # Click Review button
            await filler.click_review()
            await asyncio.sleep(2)
            
            # Check if there's a submit button now
            await browser_manager.take_screenshot(f"{session_id}_review")
            
            # Try to submit
            submitted = await filler.submit_application()
            
            if submitted:
                # Check for success
                await asyncio.sleep(2)
                success = await filler.check_success()
                
                if success:
                    # Close modal
                    await filler.close_modal()
                    
                    # Cleanup session
                    del active_sessions[session_id]
                    
                    return ApplicationResponse(
                        session_id=session_id,
                        status=ApplicationStatus.COMPLETED,
                        job_title=session_data['job_title'],
                        company_name=session_data['company_name'],
                        message="Application submitted successfully!"
                    )
                else:
                    return ApplicationResponse(
                        session_id=session_id,
                        status=ApplicationStatus.FAILED,
                        job_title=session_data['job_title'],
                        company_name=session_data['company_name'],
                        message="Application submission uncertain. Please check manually.",
                        error="Could not confirm success"
                    )
        
        elif has_next:
            # Click Next button
            await filler.click_next()
            await asyncio.sleep(2)
            
            # Extract fields from next step
            step_num = session_data['current_step'] + 1
            session_data['current_step'] = step_num
            
            await browser_manager.take_screenshot(f"{session_id}_step_{step_num}")
            
            step_info = await extractor.get_current_step_info()
            fields = await extractor.extract_all_fields()
            has_next_step = await extractor.check_has_next_step()
            
            # Update session fields
            session_data['fields'] = {field.field_id: {'type': field.field_type, 'label': field.label} for field in fields}
            
            current_step = ApplicationStep(
                step_number=step_num,
                step_title=step_info['step_title'],
                fields=fields,
                screenshot_path=f"screenshots/{session_id}_step_{step_num}.png",
                has_next_step=has_next_step
            )
            
            return ApplicationResponse(
                session_id=session_id,
                status=ApplicationStatus.WAITING_FOR_INPUT,
                job_title=session_data['job_title'],
                company_name=session_data['company_name'],
                current_step=current_step,
                message=f"Moved to step {step_num}. Extracted {len(fields)} fields."
            )
        
        else:
            # No next or review button found - try to submit directly
            submitted = await filler.submit_application()
            
            if submitted:
                await asyncio.sleep(2)
                success = await filler.check_success()
                
                if success:
                    await filler.close_modal()
                    del active_sessions[session_id]
                    
                    return ApplicationResponse(
                        session_id=session_id,
                        status=ApplicationStatus.COMPLETED,
                        job_title=session_data['job_title'],
                        company_name=session_data['company_name'],
                        message="Application submitted successfully!"
                    )
            
            return ApplicationResponse(
                session_id=session_id,
                status=ApplicationStatus.FAILED,
                job_title=session_data['job_title'],
                company_name=session_data['company_name'],
                message="Could not find Next, Review, or Submit button",
                error="Navigation buttons not found"
            )
        
    except Exception as e:
        logger.error(f"Error submitting application: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Application submission failed: {str(e)}")


@app.delete("/session/{session_id}")
async def cancel_session(session_id: str):
    """Cancel an active session"""
    global active_sessions
    
    if session_id in active_sessions:
        del active_sessions[session_id]
        
        # Try to close modal if open
        try:
            page = browser_manager.get_page()
            filler = FormFiller(page)
            await filler.close_modal()
        except:
            pass
        
        return {"message": f"Session {session_id} cancelled"}
    else:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")


@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    return {
        "active_sessions": len(active_sessions),
        "sessions": [
            {
                "session_id": sid,
                "job_title": data.get('job_title'),
                "company_name": data.get('company_name'),
                "current_step": data.get('current_step')
            }
            for sid, data in active_sessions.items()
        ]
    }


if __name__ == "__main__":
    import os
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8008"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
