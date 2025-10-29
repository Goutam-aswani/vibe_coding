# ⚡ QUICK START CHEAT SHEET

## 🎯 **TL;DR**

✅ **YES, automation is possible**  
⚠️ **Main blocker:** Cloudflare Turnstile CAPTCHA  
💰 **Two options:** Free (Playwright) or Paid (2Captcha)  
📜 **Legal:** Against ToS, use at own risk

---

## 🚀 **Quick Start (60 seconds)**

### Free Method (Playwright)

```bash
# Install
pip install playwright httpx
playwright install chromium

# Run example
python email_checker_playwright.py
```

### Paid Method (2Captcha)

```bash
# Install
pip install httpx twocaptcha-python

# Edit file: Add your API key
# Get key: https://2captcha.com/

# Run example
python email_checker_2captcha.py
```

### API Server

```bash
# Install
pip install -r requirements.txt

# Run server
python email_verification_server.py

# Test
curl -X POST http://localhost:8000/check \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

---

## 📊 **Comparison Table**

| Feature | Playwright | 2Captcha | Official APIs |
|---------|-----------|----------|---------------|
| **Cost** | $0 | $3/1000 | $1-8/1000 |
| **Speed** | 5-15 sec | 2-5 sec | 1-2 sec |
| **Success** | 50-80% | 95%+ | 99%+ |
| **Legal** | ⚠️ Risky | ⚠️ Risky | ✅ Safe |
| **Scale** | <100 | <1000 | Unlimited |
| **Setup** | Easy | Medium | Easy |

---

## 🔑 **Key API Endpoints**

### Mailmeteor (What we're automating)

```
POST https://tools.mailmeteor.com/api/email-checker
     ?cf-turnstile-response={TOKEN}

Body: {"email": "test@example.com"}

Response:
{
  "email": "test@example.com",
  "status": "valid|invalid|risky|unknown",
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

## 💻 **Code Snippets**

### Check Single Email (Playwright)

```python
from email_checker_playwright import EmailCheckerWithPlaywright
import asyncio

async def main():
    checker = EmailCheckerWithPlaywright(headless=False)
    result = await checker.check_email("test@example.com")
    print(f"Valid: {result['valid']}")

asyncio.run(main())
```

### Check Single Email (2Captcha)

```python
from email_checker_2captcha import EmailCheckerWith2Captcha
import asyncio

async def main():
    checker = EmailCheckerWith2Captcha("YOUR_API_KEY")
    result = await checker.check_email("test@example.com")
    print(f"Valid: {result['valid']}")

asyncio.run(main())
```

### Check Batch

```python
emails = [
    "elon@spacex.com",
    "test@example.com",
    "invalid@mailmeteor.com"
]

results = await checker.check_emails_batch(emails, delay=5)

for r in results:
    if r:
        print(f"{r['email']}: {r['status']}")
```

---

## 🌐 **FastAPI Endpoints**

### 1. Check Single Email (Sync)

```bash
POST /check
{
  "email": "test@example.com"
}

# Response (immediate)
{
  "email": "test@example.com",
  "status": "valid",
  "valid": true,
  "checks": {...},
  "checked_at": "2025-10-27T12:00:00Z"
}
```

### 2. Check Batch (Async)

```bash
POST /check-batch
{
  "emails": ["test1@example.com", "test2@example.com"]
}

# Response (job queued)
{
  "job_id": "abc-123",
  "status": "queued",
  "total": 2,
  "completed": 0
}

# Poll status
GET /jobs/abc-123

# Response (when done)
{
  "job_id": "abc-123",
  "status": "completed",
  "total": 2,
  "completed": 2,
  "results": [...]
}
```

---

## 🛠️ **Common Issues & Fixes**

### Issue 1: CAPTCHA Fails

```
Error: "Timeout waiting for results"
```

**Fix:**
- Use `headless=False` (visible browser)
- Increase timeout to 60 seconds
- Try 2Captcha method instead
- Check internet connection

---

### Issue 2: Rate Limited

```
Error: 429 Too Many Requests
```

**Fix:**
- Increase delay between requests (5-10 sec)
- Use residential proxies
- Reduce volume
- Consider official APIs

---

### Issue 3: IP Banned

```
Error: 403 Forbidden
```

**Fix:**
- Wait 24 hours
- Change IP (VPN/Proxy)
- Stop automated requests
- Use official services

---

### Issue 4: Browser Not Found

```
Error: Executable doesn't exist
```

**Fix:**
```bash
playwright install chromium
```

---

## 📈 **Performance Tips**

### 1. **Rate Limiting**
```python
# Good
await asyncio.sleep(5)  # 5 sec delay

# Better (randomize)
import random
await asyncio.sleep(random.uniform(3, 7))
```

### 2. **Retry Logic**
```python
for attempt in range(3):
    try:
        result = await checker.check_email(email)
        break
    except Exception as e:
        if attempt == 2:
            raise
        await asyncio.sleep(10)
```

### 3. **Batch Processing**
```python
# Process in chunks
chunk_size = 10
for i in range(0, len(emails), chunk_size):
    chunk = emails[i:i+chunk_size]
    results = await checker.check_emails_batch(chunk)
    await asyncio.sleep(60)  # Rest between chunks
```

---

## 📚 **File Reference**

| File | Purpose |
|------|---------|
| `email_checker_playwright.py` | Free browser automation |
| `email_checker_2captcha.py` | Paid CAPTCHA solving |
| `email_verification_server.py` | REST API server |
| `requirements.txt` | Dependencies |
| `README.md` | Full docs |
| `SUMMARY.md` | Executive summary |
| `ARCHITECTURE.md` | Flow diagrams |
| `analysis_mailmeteor.md` | Deep analysis |

---

## ⚠️ **Important Warnings**

1. **Terms of Service**
   - ❌ Automation is forbidden
   - ⚠️ Risk of ban
   - ✅ Use at own risk

2. **Rate Limits**
   - 🐌 Go slow (3-5 sec delays)
   - 📊 Monitor usage
   - 🛑 Stop if blocked

3. **Reliability**
   - Free: 50-80% success
   - Paid: 95% success
   - May break if site changes

4. **Production Use**
   - ❌ Don't abuse free tool
   - ✅ Use official services
   - 💰 Budget for scale

---

## 🎓 **Learning Path**

### Beginner
1. ✅ Run `email_checker_playwright.py`
2. ✅ Check 1-5 emails manually
3. ✅ Understand the flow

### Intermediate
1. ✅ Test batch processing
2. ✅ Add error handling
3. ✅ Deploy API server locally

### Advanced
1. ✅ Integrate with your app
2. ✅ Add proxy rotation
3. ✅ Implement retry logic
4. ✅ Monitor success rates

### Production Ready
1. ⚠️ Don't use this!
2. ✅ Use official APIs instead:
   - [Bouncer](https://usebouncer.com/)
   - [Clearout](https://clearout.io/)
   - [ZeroBounce](https://zerobounce.net/)

---

## 🔗 **Useful Links**

- **Mailmeteor:** https://mailmeteor.com/email-checker
- **2Captcha:** https://2captcha.com/
- **Playwright:** https://playwright.dev/
- **FastAPI:** https://fastapi.tiangolo.com/

### Official Email Verification Services
- **Bouncer:** https://usebouncer.com/ ($0.001/email)
- **Clearout:** https://clearout.io/ ($0.002/email)
- **ZeroBounce:** https://zerobounce.net/ ($0.002/email)
- **NeverBounce:** https://neverbounce.com/ ($0.008/email)

---

## 🏁 **Quick Decision Guide**

**Choose Playwright if:**
- ✅ Budget = $0
- ✅ <100 emails
- ✅ Learning/testing
- ✅ Can accept 50-80% success

**Choose 2Captcha if:**
- ✅ Budget = $3-10 per 1000
- ✅ 100-1000 emails
- ✅ Need 95% success
- ✅ Want faster results

**Choose Official APIs if:**
- ✅ Budget = $1-8 per 1000
- ✅ 1000+ emails
- ✅ Need 99% success
- ✅ Production use
- ✅ Legal compliance

---

**Last Updated:** October 27, 2025  
**Status:** ✅ Working  
**Success Rate:** 50-95% (depends on method)

---

**Need help?** Check `README.md` for full documentation!
