"""
Startup script for LinkedIn Automation
Fixes Python 3.13+ asyncio issues on Windows
"""
import sys
import asyncio

# CRITICAL: Fix event loop policy BEFORE importing anything else
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Now import and run the main application
if __name__ == "__main__":
    from main import app
    import uvicorn
    import os
    
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8080"))
    
    print(f"Starting LinkedIn Automation Service on {host}:{port}")
    print("Event loop policy set to WindowsSelectorEventLoopPolicy")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
