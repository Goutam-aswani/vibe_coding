# Mailmeteor Email Checker Automation

**Automated email verification using Mailmeteor's free email checker service**

> ⚠️ **IMPORTANT:** This is for educational purposes only. Mailmeteor's Terms of Service explicitly forbid automated requests. For production use, consider their paid services or official API partners.

---

## 📋 Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [API Server](#api-server)
- [Cost Analysis](#cost-analysis)
- [Limitations](#limitations)
- [Alternatives](#alternatives)
- [Legal Notice](#legal-notice)

---

## 🎯 Overview

This project provides automation scripts for verifying email addresses using Mailmeteor's free email checker tool at https://mailmeteor.com/email-checker

**Features:**
- ✅ Single email verification
- ✅ Batch email verification with rate limiting
- ✅ Two approaches: Free (Playwright) and Paid (2Captcha)
- ✅ FastAPI REST API server
- ✅ Detailed verification results (format, DNS, MX, SMTP checks)

**Main Challenge:**
The service uses **Cloudflare Turnstile CAPTCHA** which must be solved for each verification.

---

## 🔍 How It Works

### Verification Flow

1. **User submits email** → Form on Mailmeteor website
2. **Cloudflare Turnstile** → CAPTCHA must be solved
3. **API Request** → POST to `https://tools.mailmeteor.com/api/email-checker`
4. **Verification checks:**
   - ✉️ **Format:** Valid email format
   - 🏢 **Professional:** Not disposable/temporary
   - 🌐 **DNS:** Domain exists
   - 📬 **MX Records:** Mail server configured
   - 📨 **SMTP:** Mailbox exists

### Response Example

```json
{
  "email": "test@example.com",
  "status": "valid",
  "checks": {
    "format": {"status": "valid"},
    "disposable": {"status": "valid"},
    "dns": {"status": "valid"},
    "mx": {"status": "valid"},
    "smtp": {"status": "valid"}
  }
}
```

---

## 📦 Installation

### Prerequisites

- Python 3.8+
- Windows/Linux/Mac

### Option 1: Using Playwright (Free)

```bash
# Install dependencies
pip install playwright httpx

# Install browser
playwright install chromium
```

### Option 2: Using 2Captcha (Paid)

```bash
# Install dependencies
pip install httpx twocaptcha-python

# Get API key from https://2captcha.com/
```

### For FastAPI Server

```bash
pip install fastapi uvicorn pydantic
```

---

## 🚀 Usage

### 1. Single Email Check (Playwright - Free)

```python
from email_checker_playwright import EmailCheckerWithPlaywright
import asyncio

async def main():
    checker = EmailCheckerWithPlaywright(headless=False)
    result = await checker.check_email("test@example.com")
    
    if result:
        print(f"Email: {result['email']}")
        print(f"Valid: {result['valid']}")
        print(f"Status: {result['status']}")

asyncio.run(main())
```

**Run:**
```bash
python email_checker_playwright.py
```

**Expected output:**
```
📧 Checking email: test@example.com
🌐 Loading page...
✍️  Filling email...
🔘 Clicking verify button...
⏳ Waiting for CAPTCHA to solve and results to load...
📊 Extracting results...
✅ Status: VALID
   format: valid
   disposable: valid
   domain_status: valid
   smtp: valid
```

---

### 2. Single Email Check (2Captcha - Paid)

```python
from email_checker_2captcha import EmailCheckerWith2Captcha
import asyncio

async def main():
    # Get API key from https://2captcha.com/
    checker = EmailCheckerWith2Captcha(captcha_api_key="YOUR_API_KEY")
    result = await checker.check_email("test@example.com")
    
    if result:
        print(f"Valid: {result['valid']}")

asyncio.run(main())
```

**Run:**
```bash
python email_checker_2captcha.py
```

**Expected output:**
```
📧 Checking email: test@example.com
🔐 Solving CAPTCHA...
✅ CAPTCHA solved! Token: cf-chl-widget-abc...
✅ Status: VALID
   Format: valid
   Disposable: valid
   DNS: valid
   MX: valid
   SMTP: valid
```

---

### 3. Batch Email Verification

```python
from email_checker_playwright import EmailCheckerWithPlaywright
import asyncio

async def main():
    checker = EmailCheckerWithPlaywright(headless=False)
    
    emails = [
        "elon@spacex.com",
        "invalid@mailmeteor.com",
        "test@example.com"
    ]
    
    results = await checker.check_emails_batch(emails, delay=5)
    
    # Print summary
    valid = sum(1 for r in results if r and r['valid'])
    print(f"\n✅ Valid: {valid}/{len(results)}")

asyncio.run(main())
```

---

## 🖥️ API Server

### Start the Server

```bash
python email_verification_server.py
```

Server will start at `http://localhost:8000`

**API Documentation:** http://localhost:8000/docs

---

### API Endpoints

#### 1. **Check Single Email** (Synchronous)

```bash
POST http://localhost:8000/check
Content-Type: application/json

{
  "email": "test@example.com"
}
```

**Response:**
```json
{
  "email": "test@example.com",
  "status": "valid",
  "valid": true,
  "checks": {
    "format": "valid",
    "disposable": "valid",
    "domain_status": "valid",
    "smtp": "valid"
  },
  "checked_at": "2025-10-27T12:00:00Z"
}
```

---

#### 2. **Check Batch Emails** (Asynchronous)

```bash
POST http://localhost:8000/check-batch
Content-Type: application/json

{
  "emails": [
    "test1@example.com",
    "test2@example.com",
    "test3@example.com"
  ]
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "total": 3,
  "completed": 0,
  "results": [null, null, null]
}
```

---

#### 3. **Get Job Status**

```bash
GET http://localhost:8000/jobs/{job_id}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "total": 3,
  "completed": 3,
  "results": [
    {
      "email": "test1@example.com",
      "status": "valid",
      "valid": true,
      "checks": {...},
      "checked_at": "2025-10-27T12:00:00Z"
    },
    ...
  ]
}
```

---

### Example with cURL

```bash
# Check single email
curl -X POST http://localhost:8000/check \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Check batch
curl -X POST http://localhost:8000/check-batch \
  -H "Content-Type: application/json" \
  -d '{"emails": ["test1@example.com", "test2@example.com"]}'

# Get job status
curl http://localhost:8000/jobs/{job_id}
```

---

### Example with Python Requests

```python
import requests

# Check single email
response = requests.post(
    "http://localhost:8000/check",
    json={"email": "test@example.com"}
)
print(response.json())

# Check batch
response = requests.post(
    "http://localhost:8000/check-batch",
    json={"emails": ["test1@example.com", "test2@example.com"]}
)
job = response.json()
print(f"Job ID: {job['job_id']}")

# Check status
import time
time.sleep(30)  # Wait for processing
response = requests.get(f"http://localhost:8000/jobs/{job['job_id']}")
print(response.json())
```

---

## 💰 Cost Analysis

### Option 1: Playwright (Free)

| Metric | Value |
|--------|-------|
| **Cost** | $0 (Free) |
| **Speed** | 5-15 seconds per email |
| **Success Rate** | 50-80% (depends on CAPTCHA) |
| **Resource Usage** | High (browser instance) |
| **Best For** | Testing, small scale (<100 emails) |

**Pros:**
- ✅ Completely free
- ✅ No external dependencies
- ✅ Good for learning/testing

**Cons:**
- ❌ Slower
- ❌ Lower success rate
- ❌ Requires visible browser window
- ❌ Higher CPU/RAM usage

---

### Option 2: 2Captcha (Paid)

| Metric | Value |
|--------|-------|
| **Cost** | $0.003-0.01 per verification |
| **Speed** | 2-5 seconds per email |
| **Success Rate** | 95%+ |
| **Resource Usage** | Low (API calls only) |
| **Best For** | Production, scale (100-1000 emails) |

**Pricing:**
- 100 emails = $0.30 - $1.00
- 1,000 emails = $3.00 - $10.00
- 10,000 emails = $30.00 - $100.00

**Pros:**
- ✅ Faster
- ✅ More reliable
- ✅ Lower resource usage
- ✅ Scalable

**Cons:**
- ❌ Costs money
- ❌ Requires 2Captcha account
- ❌ External dependency

---

## ⚠️ Limitations

### Technical Limitations

1. **CAPTCHA Requirement**
   - Every request requires solving Cloudflare Turnstile
   - Free method (Playwright) may fail if CAPTCHA is strict
   - Paid method (2Captcha) adds cost and delay

2. **Rate Limiting**
   - Unknown exact limits (fair-use policy)
   - Likely IP-based throttling
   - Recommended delay: 3-5 seconds between requests

3. **Browser Fingerprinting**
   - Playwright can be detected as automation
   - Success rate varies based on Cloudflare's detection

4. **No Official API**
   - This is reverse-engineered from web interface
   - May break if Mailmeteor changes implementation
   - Not officially supported

---

### Legal & Ethical Limitations

**From Mailmeteor's Terms:**
> "Any abuse includes, but is not limited to, making automatic requests to our service."

**Implications:**
- ❌ Automation is explicitly forbidden
- ❌ Risk of IP ban or blocking
- ❌ Against Terms of Service

**Recommended Use:**
- ✅ Educational purposes only
- ✅ Testing/learning automation
- ✅ Personal spot-checks
- ❌ NOT for production/commercial use

---

## 🔄 Alternatives

### For Production Email Verification

Instead of automating the free tool, use these professional services:

| Service | Cost per Email | Free Tier | API | Bulk |
|---------|---------------|-----------|-----|------|
| [Bouncer](https://usebouncer.com/) | $0.001 | 100 free | ✅ | ✅ |
| [Clearout](https://clearout.io/) | $0.002 | 100 free | ✅ | ✅ |
| [ZeroBounce](https://www.zerobounce.net/) | $0.002 | 100 free | ✅ | ✅ |
| [NeverBounce](https://neverbounce.com/) | $0.008 | - | ✅ | ✅ |
| [Hunter.io](https://hunter.io/) | $0.005 | 25/month free | ✅ | ✅ |
| [EmailListVerify](https://www.emaillistverify.com/) | $0.004 | 100 free | ✅ | ✅ |

**Mailmeteor Partners:**
- Get exclusive discounts at https://dashboard.mailmeteor.com/account/partners

---

### DIY Email Verification

Build your own basic verification:

```python
import dns.resolver
import smtplib
import re

def verify_email_basic(email: str) -> dict:
    """Basic email verification without external services"""
    
    # 1. Format check
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return {'email': email, 'status': 'invalid', 'reason': 'format'}
    
    # 2. Domain check
    domain = email.split('@')[1]
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_host = str(mx_records[0].exchange)
    except:
        return {'email': email, 'status': 'invalid', 'reason': 'no_mx'}
    
    # 3. SMTP check (be careful - can trigger spam filters)
    try:
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_host)
        server.helo('example.com')
        server.mail('verify@example.com')
        code, message = server.rcpt(email)
        server.quit()
        
        if code == 250:
            return {'email': email, 'status': 'valid'}
        else:
            return {'email': email, 'status': 'invalid', 'reason': 'smtp_reject'}
    except:
        return {'email': email, 'status': 'unknown', 'reason': 'smtp_error'}

# Test
result = verify_email_basic('test@gmail.com')
print(result)
```

**Pros:**
- Free
- Fast
- No external dependencies
- Full control

**Cons:**
- Less accurate than Mailmeteor
- Can trigger spam filters
- No disposable email detection
- May get blocked by mail servers

---

## 📚 Legal Notice

### Disclaimer

This project is provided **for educational purposes only**. 

**You should NOT:**
- ❌ Use this for commercial purposes
- ❌ Abuse Mailmeteor's free service
- ❌ Violate their Terms of Service
- ❌ Send high volumes of requests

**You should:**
- ✅ Use for learning automation
- ✅ Test with your own emails
- ✅ Respect rate limits
- ✅ Consider using official services for production

### Terms of Service

Mailmeteor's Terms explicitly forbid automated requests:
- https://mailmeteor.com/legal/terms

**For legitimate email verification needs:**
- Use Mailmeteor's official Google Sheets add-on
- Use their partner services with discounts
- Contact them for commercial API access

---

## 🤝 Contributing

This is an educational project. Feel free to:
- Report issues
- Suggest improvements
- Share knowledge

But please:
- Don't encourage abuse
- Respect the service
- Follow ethical guidelines

---

## 📄 License

MIT License - See LICENSE file

**Disclaimer:** The authors are not responsible for any misuse of this code. Use at your own risk and always respect the terms of service of the websites you interact with.

---

## 🙏 Credits

- **Mailmeteor** - For providing the free email checker tool
- **Cloudflare** - For Turnstile CAPTCHA
- **Playwright** - Browser automation framework
- **2Captcha** - CAPTCHA solving service

---

## 📞 Support

For issues with:
- **This code:** Open an issue on GitHub
- **Mailmeteor service:** Contact https://mailmeteor.com/contact
- **Email verification needs:** Use official services mentioned above

---

**Remember:** This is a proof of concept. For production use, always use official, properly licensed services! 🚀
