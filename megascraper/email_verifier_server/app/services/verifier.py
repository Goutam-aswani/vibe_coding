"""
Email verification service using check.emailverifier.online API
"""

import httpx
import asyncio
import time
from urllib.parse import quote
from typing import Dict, List, Optional
import json
from datetime import datetime
import logging

try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailVerifierService:
    """Email verification service using HTTP API with automatic cookie refresh"""
    
    def __init__(self):
        """Initialize the email verifier service"""
        self.api_url = "https://check.emailverifier.online/bulk-verify-email/functions/quick_mail_verify.php"
        self.base_url = "https://check.emailverifier.online/bulk-verify-email/index.php"
        
        # Session cookies
        self.session_cookie = settings.EMAILVERIFIER_SESSION_COOKIE
        self.ga_cookie = settings.EMAILVERIFIER_GA_COOKIE or "_ga=GA1.1.908879861.1761510962"
        
        # Cookie manager (lazy initialization)
        self._cookie_manager = None
        self._cookie_refresh_task = None
        
        # Build cookie string
        self.cookies = f"{self.ga_cookie}; PHPSESSID={self.session_cookie}"
        
        # Initialize cookie manager if credentials are provided
        if settings.AUTO_REFRESH_COOKIE and settings.EMAILVERIFIER_EMAIL and settings.EMAILVERIFIER_PASSWORD:
            self._init_cookie_manager()
        
        # Headers that match browser request (without zstd encoding to avoid decompression issues)
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",  # Removed 'zstd' - httpx handles these automatically
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
    
    def _init_cookie_manager(self):
        """Initialize cookie manager for automatic refresh"""
        try:
            from app.services.cookie_fetcher import CookieManager
            
            self._cookie_manager = CookieManager(
                email=settings.EMAILVERIFIER_EMAIL,
                password=settings.EMAILVERIFIER_PASSWORD,
                refresh_interval_minutes=settings.COOKIE_REFRESH_INTERVAL,
                initial_cookie=self.session_cookie  # Pass existing cookie
            )
            logger.info("✅ Cookie auto-refresh enabled")
        except Exception as e:
            logger.warning(f"⚠️  Could not initialize cookie manager: {e}")
            self._cookie_manager = None
    
    async def _refresh_cookie_if_needed(self) -> bool:
        """
        Check and refresh cookie if needed
        
        Returns:
            bool: True if cookie is valid/refreshed, False if refresh failed
        """
        if not self._cookie_manager:
            return True  # No auto-refresh, assume current cookie is valid
        
        try:
            # Use get_cookie which handles expiry checking and refresh with proper locking
            # It will only refresh if the interval has passed
            new_cookie = await self._cookie_manager.get_cookie(force_refresh=False)
            
            if new_cookie and new_cookie != self.session_cookie:
                # Update cookies only if changed
                self.session_cookie = new_cookie
                self.cookies = f"{self.ga_cookie}; PHPSESSID={self.session_cookie}"
                self.headers["cookie"] = self.cookies
                
                # Update settings (optional - for persistence)
                settings.EMAILVERIFIER_SESSION_COOKIE = new_cookie
                
                logger.info("✅ Cookie refreshed successfully")
            
            return new_cookie is not None
            
        except Exception as e:
            logger.error(f"❌ Error during cookie refresh: {e}")
            return False
    
    async def _handle_session_expired(self) -> bool:
        """
        Handle expired session by attempting to refresh cookie
        
        Returns:
            bool: True if session was refreshed, False otherwise
        """
        logger.warning("⚠️  Session appears to be expired, attempting refresh...")
        
        if self._cookie_manager:
            new_cookie = await self._cookie_manager.get_cookie(force_refresh=True)
            
            if new_cookie:
                self.session_cookie = new_cookie
                self.cookies = f"{self.ga_cookie}; PHPSESSID={self.session_cookie}"
                self.headers["cookie"] = self.cookies
                settings.EMAILVERIFIER_SESSION_COOKIE = new_cookie
                logger.info("✅ Session refreshed after expiry detection")
                return True
        
        logger.error("❌ Could not refresh expired session")
        return False
    
    async def verify_email(self, email: str, index: int = 0, retry_on_auth_error: bool = True) -> Dict:
        """
        Verify a single email address asynchronously
        
        Args:
            email: Email address to verify
            index: Index number (for batch processing tracking)
            retry_on_auth_error: Retry if authentication error detected
        
        Returns:
            dict: Verification result with keys:
                - index: Request index
                - safetosend: "Yes" or "No"
                - status: "valid", "invalid", etc.
                - type: "Free Account", "Business", etc.
                - reasons: Success or failure reason
                - debug: List of SMTP debug messages
                - verified_at: Timestamp
                - processing_time_ms: Processing time
        """
        # Check if cookie needs refresh before verification
        await self._refresh_cookie_if_needed()
        
        start_time = time.time()
        
        # Build payload
        payload = {
            "email": email,
            "index": str(index),
            "token": "12345",
            "frommail": "root@earphone100.cf",
            "timeout": str(settings.REQUEST_TIMEOUT),
            "scan_port": "25"
        }
        
        # URL encode the payload
        payload_encoded = "&".join([f"{k}={quote(str(v))}" for k, v in payload.items()])
        
        try:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT + 10, follow_redirects=True) as client:
                response = await client.post(
                    self.api_url,
                    content=payload_encoded,
                    headers=self.headers
                )
                
                # Check for authentication/session errors
                if response.status_code in [401, 403]:
                    if retry_on_auth_error and await self._handle_session_expired():
                        # Retry with new cookie
                        return await self.verify_email(email, index, retry_on_auth_error=False)
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                    except Exception as json_error:
                        # Handle compressed responses manually if needed
                        content_encoding = response.headers.get('content-encoding', '').lower()
                        
                        if 'zstd' in content_encoding or response.content[:4] == b'\x28\xb5\x2f\xfd':
                            if HAS_ZSTD:
                                dctx = zstd.ZstdDecompressor()
                                decompressed = dctx.decompress(response.content)
                                result = json.loads(decompressed.decode('utf-8'))
                            else:
                                raise Exception("Response is zstd compressed but zstandard library not installed")
                        else:
                            raise json_error
                    
                    # Add metadata
                    result['verified_at'] = datetime.utcnow().isoformat()
                    result['processing_time_ms'] = int((time.time() - start_time) * 1000)
                    result['email'] = email
                    
                    return result
                else:
                    return {
                        "index": str(index),
                        "email": email,
                        "status": "error",
                        "safetosend": "Unknown",
                        "type": "Unknown",
                        "reasons": f"HTTP {response.status_code}",
                        "debug": [response.text[:200]],
                        "verified_at": datetime.utcnow().isoformat(),
                        "processing_time_ms": int((time.time() - start_time) * 1000)
                    }
                    
        except Exception as e:
            return {
                "index": str(index),
                "email": email,
                "status": "error",
                "safetosend": "Unknown",
                "type": "Unknown",
                "reasons": str(e),
                "debug": [],
                "verified_at": datetime.utcnow().isoformat(),
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
    
    async def verify_batch(self, emails: List[str], max_concurrent: int = 5) -> List[Dict]:
        """
        Verify multiple emails concurrently
        
        Args:
            emails: List of email addresses
            max_concurrent: Maximum concurrent requests
        
        Returns:
            List of verification results
        """
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def verify_with_limit(email: str, index: int):
            async with semaphore:
                # Add rate limit delay
                if settings.RATE_LIMIT_DELAY > 0 and index > 0:
                    await asyncio.sleep(settings.RATE_LIMIT_DELAY)
                return await self.verify_email(email, index)
        
        # Run all verifications concurrently
        tasks = [verify_with_limit(email, i) for i, email in enumerate(emails)]
        results = await asyncio.gather(*tasks)
        
        return results
    
    async def health_check(self) -> bool:
        """
        Check if the email verifier service is accessible
        
        Returns:
            bool: True if service is healthy
        """
        try:
            # Try to verify a test email
            result = await self.verify_email("test@example.com")
            # Service is healthy if we get any response (even invalid email)
            return result.get('status') in ['valid', 'invalid']
        except Exception:
            return False


# Global service instance
_verifier_service: Optional[EmailVerifierService] = None


def get_verifier_service() -> EmailVerifierService:
    """
    Get or create the global email verifier service instance
    
    Returns:
        EmailVerifierService: The verifier service
    """
    global _verifier_service
    if _verifier_service is None:
        _verifier_service = EmailVerifierService()
    return _verifier_service
