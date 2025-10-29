"""
CLI Tool to Manually Refresh Email Verifier Session Cookie
Usage: python refresh_cookie.py
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv, set_key

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.cookie_fetcher import fetch_cookie_cli


def update_env_file(cookie_value: str) -> bool:
    """
    Update .env file with new cookie
    
    Args:
        cookie_value: New PHPSESSID value
        
    Returns:
        True if successful, False otherwise
    """
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("❌ .env file not found!")
        return False
    
    try:
        # Update the .env file
        set_key(env_path, "EMAILVERIFIER_SESSION_COOKIE", cookie_value)
        print(f"✅ Updated .env file with new cookie")
        return True
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False


async def main():
    """Main CLI function"""
    print("="*70)
    print("🔄 Email Verifier Cookie Refresher")
    print("="*70)
    
    # Load environment variables
    load_dotenv()
    
    email = os.getenv('EMAILVERIFIER_EMAIL')
    password = os.getenv('EMAILVERIFIER_PASSWORD')
    
    if not email or not password:
        print("\n❌ Missing credentials!")
        print("\n📝 Please set the following in your .env file:")
        print("   EMAILVERIFIER_EMAIL=your_email@example.com")
        print("   EMAILVERIFIER_PASSWORD=your_password")
        print("\n💡 These are your login credentials for check.emailverifier.online")
        print("="*70)
        return 1
    
    print(f"\n📧 Email: {email}")
    print("🔐 Password: ********")
    
    # Ask for headless mode
    print("\n🌐 Browser Mode:")
    print("   1. Headless (background, faster)")
    print("   2. Visible (see the login process)")
    
    choice = input("\nSelect mode (1 or 2) [default: 1]: ").strip() or "1"
    headless = choice == "1"
    
    print("\n" + "="*70)
    print("🚀 Starting cookie refresh process...")
    print("="*70)
    
    # Fetch cookie
    cookie = await fetch_cookie_cli(email, password, headless=headless)
    
    if not cookie:
        print("\n❌ Failed to fetch cookie!")
        print("\n🔍 Troubleshooting:")
        print("   • Check your credentials in .env")
        print("   • Verify your account is active at check.emailverifier.online")
        print("   • Check login_page_debug.png for clues (if generated)")
        print("   • Try running in visible mode (option 2) to see what's happening")
        print("="*70)
        return 1
    
    print("\n✅ Successfully fetched cookie!")
    print(f"   Cookie: {cookie[:30]}... (truncated)")
    
    # Ask to update .env
    update = input("\n💾 Update .env file with new cookie? (y/n) [default: y]: ").strip().lower()
    
    if update in ['', 'y', 'yes']:
        if update_env_file(cookie):
            print("\n🎉 Cookie refresh complete!")
            print("\n📋 Next steps:")
            print("   • Your .env file has been updated")
            print("   • Restart your API server to use the new cookie")
            print("   • The cookie will expire in ~1 hour")
        else:
            print("\n⚠️  Couldn't update .env automatically")
            print(f"\n📝 Please manually update .env with this cookie:")
            print(f"   EMAILVERIFIER_SESSION_COOKIE={cookie}")
    else:
        print(f"\n📝 New cookie value:")
        print(f"   {cookie}")
        print("\n💡 Copy this to your .env file manually")
    
    print("="*70)
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("="*70)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("="*70)
        sys.exit(1)
