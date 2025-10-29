"""
Mailmeteor Email Checker Automation - Using 2Captcha Service
Best for: Production use, reliable results, scale
Cost: ~$3-10 per 1000 emails
"""

import httpx
import asyncio
from typing import Dict, Optional
from twocaptcha import TwoCaptcha


class EmailCheckerWith2Captcha:
    def __init__(self, captcha_api_key: str):
        """
        Initialize email checker with 2Captcha service
        
        Args:
            captcha_api_key: Your 2Captcha API key from https://2captcha.com/
        """
        self.captcha_solver = TwoCaptcha(captcha_api_key)
        self.base_url = "https://tools.mailmeteor.com"
        self.site_url = "https://mailmeteor.com/email-checker"
        self.sitekey = "0x4AAAAAAAe7i7oicz-TnMTr"
        
    def solve_captcha(self) -> str:
        """Solve Cloudflare Turnstile CAPTCHA using 2Captcha"""
        print("🔐 Solving CAPTCHA...")
        
        result = self.captcha_solver.turnstile(
            sitekey=self.sitekey,
            url=self.site_url,
            action='emailchecker'
        )
        
        print(f"✅ CAPTCHA solved! Token: {result['code'][:20]}...")
        return result['code']
    
    async def check_email(self, email: str) -> Optional[Dict]:
        """
        Check if an email is valid
        
        Args:
            email: Email address to verify
            
        Returns:
            Dict with verification results or None if failed
        """
        print(f"\n📧 Checking email: {email}")
        
        try:
            # Step 1: Solve CAPTCHA
            captcha_token = self.solve_captcha()
            
            # Step 2: Make API request
            url = f"{self.base_url}/api/email-checker?cf-turnstile-response={captcha_token}"
            
            headers = {
                'Content-Type': 'application/json',
                'Origin': 'https://mailmeteor.com',
                'Referer': 'https://mailmeteor.com/email-checker',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            payload = {"email": email}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    result = {
                        'email': data['email'],
                        'status': data['status'],
                        'valid': data['status'] == 'valid',
                        'checks': {
                            'format': data['checks']['format']['status'],
                            'disposable': data['checks']['disposable']['status'],
                            'dns': data['checks']['dns']['status'],
                            'mx': data['checks']['mx']['status'],
                            'smtp': data['checks']['smtp']['status'],
                        }
                    }
                    
                    # Print result
                    status_emoji = "✅" if result['valid'] else "❌"
                    print(f"{status_emoji} Status: {result['status'].upper()}")
                    print(f"   Format: {result['checks']['format']}")
                    print(f"   Disposable: {result['checks']['disposable']}")
                    print(f"   DNS: {result['checks']['dns']}")
                    print(f"   MX: {result['checks']['mx']}")
                    print(f"   SMTP: {result['checks']['smtp']}")
                    
                    return result
                else:
                    print(f"❌ API Error: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    async def check_emails_batch(self, emails: list, delay: int = 3) -> list:
        """
        Check multiple emails with delay between requests
        
        Args:
            emails: List of email addresses
            delay: Seconds to wait between requests (default 3)
            
        Returns:
            List of verification results
        """
        results = []
        
        print(f"🚀 Checking {len(emails)} emails with {delay}s delay...")
        
        for i, email in enumerate(emails, 1):
            print(f"\n--- Progress: {i}/{len(emails)} ---")
            
            result = await self.check_email(email)
            results.append(result)
            
            # Delay between requests (except last one)
            if i < len(emails):
                print(f"⏳ Waiting {delay} seconds...")
                await asyncio.sleep(delay)
        
        return results


async def main():
    """Example usage"""
    
    # Replace with your actual 2Captcha API key
    API_KEY = "YOUR_2CAPTCHA_API_KEY_HERE"
    
    if API_KEY == "YOUR_2CAPTCHA_API_KEY_HERE":
        print("❌ Please set your 2Captcha API key first!")
        print("   Get one at: https://2captcha.com/")
        return
    
    # Initialize checker
    checker = EmailCheckerWith2Captcha(API_KEY)
    
    # Example 1: Check single email
    print("=" * 60)
    print("EXAMPLE 1: Single Email Check")
    print("=" * 60)
    result = await checker.check_email("elon@spacex.com")
    
    # Example 2: Check multiple emails
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Batch Email Check")
    print("=" * 60)
    
    emails_to_check = [
        "corentin@mailmeteor.com",
        "invalid@example.com",
        "test@gmail.com",
    ]
    
    results = await checker.check_emails_batch(emails_to_check, delay=3)
    
    # Summary
    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    valid_count = sum(1 for r in results if r and r.get('valid'))
    print(f"✅ Valid emails: {valid_count}/{len(results)}")
    print(f"❌ Invalid emails: {len(results) - valid_count}/{len(results)}")


if __name__ == "__main__":
    # Install dependencies first:
    # pip install httpx twocaptcha-python
    
    asyncio.run(main())
