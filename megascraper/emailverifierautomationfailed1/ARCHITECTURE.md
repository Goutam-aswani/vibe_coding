# Mailmeteor Email Checker - Architecture & Flow

## 🔄 Complete Verification Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER / APPLICATION                          │
│                   (FastAPI Server / Direct Script)                  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ email to verify
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AUTOMATION LAYER                               │
│  ┌─────────────────────┐         ┌──────────────────────────────┐  │
│  │  Option 1: FREE     │   OR    │  Option 2: PAID              │  │
│  │  Playwright Browser │         │  2Captcha Service            │  │
│  │  - Opens browser    │         │  - API call to 2Captcha      │  │
│  │  - Auto-solves      │         │  - 95% success rate          │  │
│  │  - 50-80% success   │         │  - $0.003-0.01/solve         │  │
│  └──────────┬──────────┘         └──────────────┬───────────────┘  │
│             │                                   │                   │
└─────────────┼───────────────────────────────────┼───────────────────┘
              │                                   │
              │ CAPTCHA solve                     │ CAPTCHA token
              ▼                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  CLOUDFLARE TURNSTILE CAPTCHA                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Site Key: 0x4AAAAAAAe7i7oicz-TnMTr                         │    │
│  │  Action: emailchecker                                       │    │
│  │  Type: Managed Challenge                                    │    │
│  │  ─────────────────────────────────────────────────────────  │    │
│  │  ✅ Verified human (or solved by service)                  │    │
│  │  Returns: cf-turnstile-response token                       │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  │ token
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    MAILMETEOR API ENDPOINT                          │
│  POST https://tools.mailmeteor.com/api/email-checker                │
│       ?cf-turnstile-response={TOKEN}                                │
│  ─────────────────────────────────────────────────────────────────  │
│  Body: { "email": "test@example.com" }                              │
│  Headers: Content-Type: application/json                            │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  │ verification request
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     VERIFICATION CHECKS                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  1. FORMAT CHECK                                             │  │
│  │     ✓ Valid email format (user@domain.com)                   │  │
│  │     ✗ Gibberish or malformed                                 │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │  2. DISPOSABLE CHECK                                         │  │
│  │     ✓ Professional domain                                    │  │
│  │     ✗ Temporary/disposable service                           │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │  3. DNS CHECK                                                │  │
│  │     ✓ Domain exists                                          │  │
│  │     ✗ Domain not found                                       │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │  4. MX RECORDS CHECK                                         │  │
│  │     ✓ Mail server configured                                 │  │
│  │     ✗ No MX records                                          │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │  5. SMTP CHECK                                               │  │
│  │     ✓ Mailbox exists                                         │  │
│  │     ? Unknown (catch-all domain)                             │  │
│  │     ✗ Mailbox doesn't exist                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  │ verification result
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          RESPONSE                                   │
│  {                                                                  │
│    "email": "test@example.com",                                     │
│    "status": "valid|invalid|risky|unknown",                         │
│    "checks": {                                                      │
│      "format": { "status": "valid" },                               │
│      "disposable": { "status": "valid" },                           │
│      "dns": { "status": "valid" },                                  │
│      "mx": { "status": "valid" },                                   │
│      "smtp": { "status": "valid" }                                  │
│    }                                                                │
│  }                                                                  │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  │ parsed result
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FINAL RESULT TO USER                             │
│  ✅ test@example.com is VALID                                       │
│     - Format: ✓                                                     │
│     - Professional: ✓                                               │
│     - DNS: ✓                                                        │
│     - MX Records: ✓                                                 │
│     - Mailbox: ✓                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ System Architecture Options

### Option A: Direct Script Execution

```
┌─────────────┐
│   Script    │──> Check email(s) ──> Results printed to console
└─────────────┘
```

**Use Case:** One-off checks, testing, development  
**Files:** `email_checker_playwright.py` or `email_checker_2captcha.py`

---

### Option B: FastAPI Server

```
┌──────────┐     HTTP     ┌──────────────┐     Queue    ┌──────────────┐
│  Client  │─────────────>│  FastAPI     │─────────────>│  Background  │
│ (cURL,   │   Request    │  Server      │   Add Job    │  Worker      │
│ Browser, │              │              │              │              │
│ App)     │<─────────────│  - Endpoints │<─────────────│  - Process   │
└──────────┘  Response    │  - Validation│   Results    │  - Rate      │
                          │  - Queue Mgmt│              │    Limit     │
                          └──────────────┘              │  - Retry     │
                                                        └──────────────┘
                                                               │
                                                               ▼
                                                        ┌──────────────┐
                                                        │  Mailmeteor  │
                                                        │  API         │
                                                        └──────────────┘
```

**Use Case:** Production service, multiple clients, batch processing  
**File:** `email_verification_server.py`

---

## 🔐 CAPTCHA Solving Methods Comparison

### Method 1: Playwright (Browser Automation)

```
┌─────────────────┐
│  Your Script    │
└────────┬────────┘
         │ Launch browser
         ▼
┌─────────────────┐
│  Chromium       │──> Navigate to site
│  Browser        │──> Fill form
│  (Real Window)  │──> Submit
└────────┬────────┘
         │ Turnstile auto-detects "human"
         ▼
┌─────────────────┐
│  Cloudflare     │──> Validates browser fingerprint
│  Turnstile      │──> Issues token (if successful)
└────────┬────────┘
         │ Token
         ▼
┌─────────────────┐
│  API Request    │──> With token
└─────────────────┘
```

**Pros:**
- ✅ Free
- ✅ No external service
- ✅ Works if Turnstile is lenient

**Cons:**
- ❌ 50-80% success rate
- ❌ Slower (5-15 sec)
- ❌ Needs visible browser
- ❌ High resource usage

---

### Method 2: 2Captcha (Solving Service)

```
┌─────────────────┐
│  Your Script    │
└────────┬────────┘
         │ API call to 2Captcha
         ▼
┌─────────────────┐
│  2Captcha       │──> Workers solve CAPTCHA
│  Service        │──> (Human or AI)
└────────┬────────┘
         │ Token (2-30 sec)
         ▼
┌─────────────────┐
│  Your Script    │──> Direct API call with token
└────────┬────────┘
         │ With token
         ▼
┌─────────────────┐
│  Mailmeteor API │
└─────────────────┘
```

**Pros:**
- ✅ 95%+ success rate
- ✅ Faster (2-5 sec)
- ✅ No browser needed
- ✅ Low resource usage
- ✅ Scalable

**Cons:**
- ❌ Costs money ($0.003-0.01/solve)
- ❌ External dependency
- ❌ Need account setup

---

## 📊 Performance Comparison

| Aspect | Playwright | 2Captcha |
|--------|-----------|----------|
| **Setup Time** | 5 min | 10 min + account |
| **First Request** | 10-20 sec | 5-10 sec |
| **Subsequent Requests** | 5-15 sec | 2-5 sec |
| **100 Emails** | 8-25 min | 3-8 min |
| **1000 Emails** | 83-250 min | 33-83 min |
| **Success Rate** | 50-80% | 95%+ |
| **Cost (1000 emails)** | $0 | $3-10 |
| **CPU Usage** | High | Low |
| **RAM Usage** | 300-500 MB/browser | <50 MB |

---

## 🎯 Decision Tree: Which Method to Use?

```
Start Here
    │
    ▼
┌──────────────────────────────┐
│ Do you have budget?          │
└─┬────────────────────────┬───┘
  │ NO                     │ YES
  │                        │
  ▼                        ▼
┌──────────────────┐    ┌──────────────────┐
│ < 100 emails?    │    │ Need reliability?│
└─┬──────────┬─────┘    └─┬──────────┬─────┘
  │ YES      │ NO         │ YES      │ NO
  │          │            │          │
  ▼          ▼            ▼          ▼
Use        Consider    Use        Try
Playwright  Official   2Captcha   Playwright
(Free)      APIs                  first
            
            
If Playwright fails often (< 50% success):
    └──> Switch to 2Captcha or Official APIs
    
If need > 1000 emails/day:
    └──> Use Official APIs (Bouncer, Clearout, etc.)
```

---

## 🚨 Rate Limiting Strategy

```
Request 1  ────>  Wait 3-5 sec  ────>  Request 2  ────>  Wait 3-5 sec  ────> ...

Benefits:
✓ Avoids rate limits
✓ Appears more human-like
✓ Reduces server load
✓ Better success rate

Recommended delays:
- Testing: 5-10 seconds
- Production: 3-5 seconds
- Aggressive: 2-3 seconds (higher ban risk)
```

---

## 🛡️ Error Handling Flow

```
Check Email
    │
    ▼
┌──────────────────┐
│ Try CAPTCHA      │
│ (max 3 attempts) │
└─┬────────────────┘
  │
  ├─ Success ───────> Continue to verification
  │
  └─ Failure ───────> Log error + Return null
                          │
                          ▼
                     ┌─────────────────┐
                     │ Retry Queue?    │
                     └─┬───────────┬───┘
                       │ YES       │ NO
                       │           │
                       ▼           ▼
                   Re-queue    Mark as failed
                   
                   
Verification Result
    │
    ├─ 200 OK ────────> Parse response + Return result
    │
    ├─ 429 Too Many ──> Wait 60 sec + Retry
    │
    ├─ 403 Forbidden ─> IP banned + Stop/Switch proxy
    │
    └─ 5xx Error ─────> Retry 3x + Then fail
```

---

## 📁 Project File Structure

```
megascraper/
│
├── email_checker_playwright.py    # Free method (browser)
├── email_checker_2captcha.py      # Paid method (CAPTCHA service)
├── email_verification_server.py   # FastAPI REST API
│
├── requirements.txt               # Python dependencies
├── README.md                      # Full documentation
├── SUMMARY.md                     # Quick overview
├── analysis_mailmeteor.md         # Deep technical analysis
└── ARCHITECTURE.md                # This file (flow diagrams)
```

---

## 🔄 Workflow Example: Batch Processing

```
User Request: Verify 100 emails
         │
         ▼
┌─────────────────────┐
│ FastAPI Endpoint    │
│ POST /check-batch   │
└──────────┬──────────┘
           │
           │ Create job
           │ Generate job_id
           │
           ▼
┌─────────────────────┐
│ Job Queue           │
│ {                   │
│   id: "abc-123",    │
│   status: "queued", │
│   emails: [100],    │
│   results: []       │
│ }                   │
└──────────┬──────────┘
           │
           │ Return job_id to user
           │
           ▼
┌─────────────────────┐
│ Background Worker   │
│ (async loop)        │
└──────────┬──────────┘
           │
           │ Process emails 1 by 1
           │ with 3-5 sec delay
           │
           ├──> Email 1: Check ──> Update job.results[0]
           │         ▼
           │      Wait 3 sec
           │         ▼
           ├──> Email 2: Check ──> Update job.results[1]
           │         ▼
           │      Wait 3 sec
           │         ▼
           ├──> Email 3: Check ──> Update job.results[2]
           │         ▼
           │       ...
           │         ▼
           └──> Email 100: Check ──> Update job.results[99]
                     ▼
           ┌─────────────────────┐
           │ Job Complete        │
           │ status: "completed" │
           └─────────────────────┘
                     │
                     │ User polls GET /jobs/{id}
                     │
                     ▼
           ┌─────────────────────┐
           │ Return full results │
           └─────────────────────┘
```

**Total Time for 100 emails:**
- With 3 sec delay: ~5-8 minutes
- With 5 sec delay: ~8-13 minutes

---

This architecture document shows all the flows and decision points! 🚀
