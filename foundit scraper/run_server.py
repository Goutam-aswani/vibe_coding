"""
Start server without auto-reload for stable testing
"""
import uvicorn

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 Starting Foundit Job Scraper API (Stable Mode)")
    print("="*80)
    print("\n📋 Available endpoints:")
    print("  • http://localhost:8080/docs - Interactive API documentation")
    print("  • http://localhost:8080/health - Health check")
    print("  • http://localhost:8080/scrape - Scrape jobs (POST)")
    print("  • http://localhost:8080/example-request - Example request")
    print("\n" + "="*80 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,  # No auto-reload for stable testing
        log_level="info"
    )
