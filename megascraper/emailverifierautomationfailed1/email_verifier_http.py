"""
Email Verifier using check.emailverifier.online HTTP API
========================================================

This script directly calls the email verification API without browser automation.
Much faster, 100% reliable, no CAPTCHA challenges!

API Endpoint: https://check.emailverifier.online/bulk-verify-email/functions/quick_mail_verify.php

Requirements:
- httpx library for HTTP requests
- Valid session (cookies from logged-in account)

Usage:
    # Single email
    python email_verifier_http.py test@example.com
    
    # Multiple emails
    python email_verifier_http.py email1@test.com email2@test.com
    
    # From code
    from email_verifier_http import EmailVerifierHTTP
    verifier = EmailVerifierHTTP(session_cookie="your_phpsessid_cookie")
    result = verifier.check_email("test@example.com")
    print(f"Status: {result['status']}, Safe to send: {result['safetosend']}")

Author: GitHub Copilot
Date: October 27, 2025
"""

import httpx
import asyncio
import time
from urllib.parse import quote
from typing import Dict, List, Optional
import json

try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False


class EmailVerifierHTTP:
    """Direct HTTP client for check.emailverifier.online API"""
    
    def __init__(
        self,
        session_cookie: Optional[str] = None,
        ga_cookie: Optional[str] = None,
        timeout: int = 10,
        rate_limit_delay: float = 1.0
    ):
        """
        Initialize the HTTP email verifier
        
        Args:
            session_cookie: PHPSESSID cookie value (required for authenticated access)
            ga_cookie: Google Analytics cookie (optional, but helps look more realistic)
            timeout: Request timeout in seconds (default: 10)
            rate_limit_delay: Delay between requests in seconds (default: 1.0)
        """
        self.api_url = "https://check.emailverifier.online/bulk-verify-email/functions/quick_mail_verify.php"
        self.base_url = "https://check.emailverifier.online/bulk-verify-email/index.php"
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        
        # Session cookies - you can get these from your browser after logging in
        self.session_cookie = session_cookie or "YOUR_PHPSESSID_HERE"
        self.ga_cookie = ga_cookie or "_ga=GA1.1.908879861.1761510962"
        
        # Build cookie string
        self.cookies = f"{self.ga_cookie}; PHPSESSID={self.session_cookie}"
        
        # Headers that match the browser request exactly
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",  # Removed 'zstd' - not supported by httpx
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://check.emailverifier.online",
            "referer": self.base_url,
            "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "cookie": self.cookies
        }
    
    def check_email(self, email: str, index: int = 0) -> Dict:
        """
        Verify a single email address
        
        Args:
            email: Email address to verify
            index: Index number (for batch processing tracking)
        
        Returns:
            dict: Verification result with keys:
                - index: Request index
                - safetosend: "Yes" or "No"
                - status: "valid", "invalid", etc.
                - type: "Free Account", "Business", etc.
                - reasons: Success or failure reason
                - debug: List of SMTP debug messages
        
        Example response:
            {
                "index": "0",
                "safetosend": "Yes",
                "status": "valid",
                "type": "Free Account",
                "reasons": "success",
                "debug": [
                    "Valid Email Domain DNS Found...",
                    "Valid Email Domain MX Records Found...",
                    "220 mx.google.com ESMTP...",
                    "250 2.1.5 OK..."
                ]
            }
        """
        # Build payload exactly as the browser sends it
        payload = {
            "email": email,
            "index": str(index),
            "token": "12345",  # Static token used by the site
            "frommail": "root@earphone100.cf",  # Source email for SMTP check
            "timeout": str(self.timeout),
            "scan_port": "25"  # SMTP port
        }
        
        # URL encode the payload
        payload_encoded = "&".join([f"{k}={quote(str(v))}" for k, v in payload.items()])
        
        print(f"\n{'='*60}")
        print(f"🔍 Verifying: {email}")
        print(f"{'='*60}")
        
        try:
            # Make the POST request
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                response = client.post(
                    self.api_url,
                    content=payload_encoded,
                    headers=self.headers
                )
                
                print(f"📡 Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    # Handle compressed responses (zstd, gzip, etc.)
                    try:
                        result = response.json()
                    except Exception as json_error:
                        # Check if response is zstd compressed but httpx didn't decompress
                        content_encoding = response.headers.get('content-encoding', '').lower()
                        
                        if 'zstd' in content_encoding or response.content[:4] == b'\x28\xb5\x2f\xfd':
                            # Manual zstd decompression
                            if HAS_ZSTD:
                                print("⚙️  Manually decompressing zstd data...")
                                dctx = zstd.ZstdDecompressor()
                                decompressed = dctx.decompress(response.content)
                                result = json.loads(decompressed.decode('utf-8'))
                            else:
                                print("❌ Response is zstd compressed but zstandard library not installed!")
                                print("   Run: pip install zstandard")
                                raise
                        else:
                            # Some other error
                            print(f"⚠️  JSON decode error: {json_error}")
                            print(f"📝 Response encoding: {response.encoding}")
                            print(f"📝 Content-Type: {response.headers.get('content-type', 'unknown')}")
                            print(f"📝 Content-Encoding: {content_encoding}")
                            print(f"📝 First 100 bytes: {response.content[:100]}")
                            raise
                    
                    # Pretty print the result
                    print(f"\n✅ Verification Complete!")
                    print(f"   Status: {result.get('status', 'unknown')}")
                    print(f"   Safe to Send: {result.get('safetosend', 'unknown')}")
                    print(f"   Account Type: {result.get('type', 'unknown')}")
                    print(f"   Reason: {result.get('reasons', 'unknown')}")
                    
                    if 'debug' in result and result['debug']:
                        print(f"\n📋 Debug Info:")
                        for debug_msg in result['debug'][:5]:  # Show first 5 debug messages
                            print(f"   • {debug_msg}")
                        if len(result['debug']) > 5:
                            print(f"   ... and {len(result['debug']) - 5} more messages")
                    
                    return result
                else:
                    print(f"❌ Error: HTTP {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    return {
                        "index": str(index),
                        "status": "error",
                        "safetosend": "Unknown",
                        "type": "Unknown",
                        "reasons": f"HTTP {response.status_code}",
                        "debug": [response.text[:200]]
                    }
                    
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return {
                "index": str(index),
                "status": "error",
                "safetosend": "Unknown",
                "type": "Unknown",
                "reasons": str(e),
                "debug": []
            }
    
    def check_emails_batch(self, emails: List[str]) -> List[Dict]:
        """
        Verify multiple email addresses with rate limiting
        
        Args:
            emails: List of email addresses to verify
        
        Returns:
            List of verification results (one per email)
        """
        results = []
        total = len(emails)
        
        print(f"\n🚀 Starting batch verification of {total} emails")
        print(f"⏱️  Rate limit: {self.rate_limit_delay}s between requests")
        print(f"{'='*60}\n")
        
        for index, email in enumerate(emails):
            start_time = time.time()
            
            # Verify the email
            result = self.check_email(email, index)
            results.append(result)
            
            # Calculate time taken
            elapsed = time.time() - start_time
            
            # Show progress
            print(f"\n📊 Progress: {index + 1}/{total} complete ({(index + 1)/total*100:.1f}%)")
            print(f"⏱️  Time taken: {elapsed:.2f}s")
            
            # Rate limiting (except for last email)
            if index < total - 1:
                print(f"💤 Waiting {self.rate_limit_delay}s before next request...")
                time.sleep(self.rate_limit_delay)
        
        # Summary
        print(f"\n{'='*60}")
        print(f"✅ Batch Complete!")
        print(f"{'='*60}")
        
        valid_count = sum(1 for r in results if r.get('status') == 'valid')
        invalid_count = sum(1 for r in results if r.get('status') == 'invalid')
        error_count = sum(1 for r in results if r.get('status') == 'error')
        
        print(f"\n📈 Summary:")
        print(f"   Total: {total}")
        print(f"   ✅ Valid: {valid_count} ({valid_count/total*100:.1f}%)")
        print(f"   ❌ Invalid: {invalid_count} ({invalid_count/total*100:.1f}%)")
        print(f"   ⚠️  Errors: {error_count} ({error_count/total*100:.1f}%)")
        
        return results
    
    async def check_email_async(self, email: str, index: int = 0) -> Dict:
        """Async version of check_email for concurrent processing"""
        payload = {
            "email": email,
            "index": str(index),
            "token": "12345",
            "frommail": "root@earphone100.cf",
            "timeout": str(self.timeout),
            "scan_port": "25"
        }
        
        payload_encoded = "&".join([f"{k}={quote(str(v))}" for k, v in payload.items()])
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.post(
                    self.api_url,
                    content=payload_encoded,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "index": str(index),
                        "status": "error",
                        "safetosend": "Unknown",
                        "type": "Unknown",
                        "reasons": f"HTTP {response.status_code}",
                        "debug": []
                    }
        except Exception as e:
            return {
                "index": str(index),
                "status": "error",
                "safetosend": "Unknown",
                "type": "Unknown",
                "reasons": str(e),
                "debug": []
            }
    
    async def check_emails_concurrent(self, emails: List[str], max_concurrent: int = 5) -> List[Dict]:
        """
        Verify multiple emails concurrently (faster than batch)
        
        Args:
            emails: List of email addresses
            max_concurrent: Maximum concurrent requests (default: 5)
        
        Returns:
            List of verification results
        """
        print(f"\n🚀 Starting concurrent verification of {len(emails)} emails")
        print(f"⚡ Max concurrent requests: {max_concurrent}")
        print(f"{'='*60}\n")
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def verify_with_limit(email: str, index: int):
            async with semaphore:
                return await self.check_email_async(email, index)
        
        # Run all verifications concurrently
        tasks = [verify_with_limit(email, i) for i, email in enumerate(emails)]
        results = await asyncio.gather(*tasks)
        
        # Summary
        valid_count = sum(1 for r in results if r.get('status') == 'valid')
        invalid_count = sum(1 for r in results if r.get('status') == 'invalid')
        
        print(f"\n✅ Concurrent verification complete!")
        print(f"   Valid: {valid_count}/{len(emails)}")
        print(f"   Invalid: {invalid_count}/{len(emails)}")
        
        return results


def main():
    """Command-line interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("❌ Usage: python email_verifier_http.py <email1> [email2] [email3] ...")
        print("\nExample:")
        print("  python email_verifier_http.py test@gmail.com")
        print("  python email_verifier_http.py user1@test.com user2@test.com")
        sys.exit(1)
    
    emails = sys.argv[1:]
    
    # TODO: Replace with your actual session cookie!
    # Get this from browser DevTools → Application → Cookies → PHPSESSID
    print("⚠️  WARNING: You need to set your PHPSESSID cookie!")
    print("   1. Open https://check.emailverifier.online/bulk-verify-email/index.php")
    print("   2. Log in to your account")
    print("   3. Open DevTools (F12) → Application → Cookies")
    print("   4. Copy the PHPSESSID value")
    print("   5. Replace 'YOUR_PHPSESSID_HERE' in the code\n")
    
    verifier = EmailVerifierHTTP(
        session_cookie="YOUR_PHPSESSID_HERE",  # ← REPLACE THIS!
        rate_limit_delay=1.0  # 1 second between requests
    )
    
    if len(emails) == 1:
        # Single email
        result = verifier.check_email(emails[0])
    else:
        # Multiple emails
        results = verifier.check_emails_batch(emails)
        
        # Save to JSON
        output_file = f"verification_results_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
