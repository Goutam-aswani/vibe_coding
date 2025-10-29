"""
Quick Start Script for Email Verifier API
"""

import os
import sys
from pathlib import Path

print("="*70)
print("🚀 Email Verifier API - Quick Start")
print("="*70)

# Check if .env file exists
env_file = Path(".env")
env_example = Path(".env.example")

if not env_file.exists():
    print("\n⚠️  .env file not found!")
    print("\n📝 Creating .env file from template...")
    
    if env_example.exists():
        # Copy example to .env
        with open(env_example, 'r') as src:
            content = src.read()
        with open(env_file, 'w') as dst:
            dst.write(content)
        print("✅ Created .env file")
    else:
        print("❌ .env.example not found!")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("⚙️  CONFIGURATION REQUIRED")
    print("="*70)
    print("\nBefore starting the server, you need to:")
    print("\n1. Get your session cookie:")
    print("   • Visit: https://check.emailverifier.online/bulk-verify-email/index.php")
    print("   • Log in to your account")
    print("   • Press F12 → Application → Cookies")
    print("   • Copy the PHPSESSID value")
    print("\n2. Edit the .env file:")
    print("   • Open: .env")
    print("   • Find: EMAILVERIFIER_SESSION_COOKIE=")
    print("   • Paste your cookie value")
    print("\n3. Optional: Set an API key for security")
    print("   • Find: API_KEY=")
    print("   • Set a secret key (or leave empty for open access)")
    print("\n4. Run this script again to start the server")
    print("="*70)
    sys.exit(0)

# Load .env and check for session cookie
from dotenv import load_dotenv
load_dotenv()

session_cookie = os.getenv('EMAILVERIFIER_SESSION_COOKIE', '')

if not session_cookie or session_cookie == 'your_phpsessid_cookie_here':
    print("\n⚠️  Session cookie not configured!")
    print("\n📝 Please edit .env file and set EMAILVERIFIER_SESSION_COOKIE")
    print("\nInstructions:")
    print("1. Visit: https://check.emailverifier.online/bulk-verify-email/index.php")
    print("2. Log in to your account")
    print("3. Press F12 → Application → Cookies")
    print("4. Copy the PHPSESSID value")
    print("5. Paste it in .env file")
    print("\nThen run this script again!")
    print("="*70)
    sys.exit(1)

print("\n✅ Configuration loaded!")
print(f"   Session Cookie: {session_cookie[:20]}... (truncated)")

api_key = os.getenv('API_KEY', '')
if api_key:
    print(f"   API Key: {api_key[:10]}... (set)")
else:
    print("   API Key: Not set (open access)")

print("\n" + "="*70)
print("🚀 Starting Email Verifier API Server")
print("="*70)

if __name__ == "__main__":
    # Import and run the app
    import uvicorn
    from app.core.config import settings

    print(f"\n📍 Server will start at: http://{settings.HOST}:{settings.PORT}")
    print(f"📖 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔍 Health Check: http://{settings.HOST}:{settings.PORT}/health")
    print("\n💡 Press CTRL+C to stop the server")
    print("="*70 + "\n")

    try:
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=True,
            log_level=settings.LOG_LEVEL.lower()
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped!")
        print("="*70)

