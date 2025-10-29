# 🎯 QUICK START: Get Your Cookie & Run (2 Minutes!)

## Step 1: Get Your Session Cookie (1 minute)

### A. Open the Website
1. Open Chrome/Edge browser
2. Go to: `https://check.emailverifier.online/bulk-verify-email/index.php`
3. **Log in** to your account (where you have 10,000 credits)

### B. Open DevTools
- Press `F12` on your keyboard
- OR right-click anywhere → "Inspect"

### C. Find the Cookie
1. Click the **"Application"** tab at the top
2. In left sidebar: expand **"Cookies"**
3. Click: `https://check.emailverifier.online`
4. Find row: `PHPSESSID`
5. Click the **Value** column
6. Press `Ctrl+C` to copy

Example cookie value: `5dc7jcltfl2gvuoo9h59u973mf`

---

## Step 2: Configure the Script (30 seconds)

1. Open: `emailverifierautomationfailed1/demo_http_verifier.py`
2. Find line 18:
   ```python
   YOUR_SESSION_COOKIE = "YOUR_SESSION_COOKIE_HERE"
   ```
3. Replace with your cookie:
   ```python
   YOUR_SESSION_COOKIE = "5dc7jcltfl2gvuoo9h59u973mf"
   ```
4. Save the file (`Ctrl+S`)

---

## Step 3: Run It! (30 seconds)

Open PowerShell and run:

```powershell
cd Z:\scraper\megascraper
python emailverifierautomationfailed1\demo_http_verifier.py
```

That's it! 🎉

---

## What You'll See

### Demo 1: Single Email
```
🔍 Verifying: goutamaswani43@gmail.com
📡 Response Status: 200

✅ Verification Complete!
   Status: valid
   Safe to Send: Yes
   Account Type: Free Account
   Reason: success

📋 Debug Info:
   • Valid Email Domain DNS Found...
   • Valid Email Domain MX Records Found...
   • 220 mx.google.com ESMTP...
   • 250 2.1.5 OK...
```

### Demo 2: Batch Processing
```
🚀 Starting batch verification of 3 emails
⏱️  Rate limit: 2.0s between requests

📊 Progress: 3/3 complete (100.0%)

📈 Summary:
   Total: 3
   ✅ Valid: 2 (66.7%)
   ❌ Invalid: 1 (33.3%)

💾 Results saved to: demo_verification_results.json
```

### Demo 3: Concurrent (FAST!)
```
⚡ Max concurrent requests: 5

✅ Concurrent verification complete!
   Valid: 12/15
   Invalid: 3/15

💾 Results saved to: demo_concurrent_results.json
```

---

## Customizing for Your Emails

Edit `demo_http_verifier.py`, find line 25:

```python
test_emails = [
    "goutamaswani43@gmail.com",  # ← Change these!
    "test@gmail.com",
    "invalid.email@nonexistent-domain-12345.com",
]
```

Replace with your actual emails:

```python
test_emails = [
    "customer1@company.com",
    "customer2@company.com",
    "customer3@company.com",
    # ... add up to 10,000!
]
```

---

## Performance Tips

### For Maximum Speed:
```python
# In demo_http_verifier.py, line 106:
max_concurrent=10  # ← Increase from 5 to 10
```

**Warning**: Start with 5, test it, then increase gradually. Don't overload the server!

### Processing Large Lists:
```python
# Read from file
with open('my_emails.txt', 'r') as f:
    test_emails = [line.strip() for line in f]

# Verify them all
verifier = EmailVerifierHTTP(session_cookie=YOUR_SESSION_COOKIE)
results = asyncio.run(verifier.check_emails_concurrent(test_emails, max_concurrent=5))
```

---

## Troubleshooting

### "HTTP 401" or "HTTP 403"
→ Your cookie expired. Get a fresh one (repeat Step 1)

### "Connection timeout"
→ Server is slow. Increase timeout:
```python
verifier = EmailVerifierHTTP(
    session_cookie=YOUR_SESSION_COOKIE,
    timeout=30  # ← Increase from 10 to 30
)
```

### Need Help?
Read the full guide: `HTTP_SETUP_GUIDE.md`

---

## Time Estimates

| Emails | Sequential | Concurrent (5x) | Concurrent (10x) |
|--------|-----------|----------------|-----------------|
| 10 | 20 seconds | 4 seconds | 2 seconds |
| 100 | 3 minutes | 40 seconds | 20 seconds |
| 1,000 | 30 minutes | 6 minutes | 3 minutes |
| 10,000 | 5 hours | **1 hour** | **30 minutes** |

**Your 10,000 credits** = All emails verified in under 1 hour! ⚡

---

**Ready? Let's go!** 🚀

1. ✅ Get cookie (1 min)
2. ✅ Edit script (30 sec)
3. ✅ Run demo (30 sec)
4. 🎉 Verify 10,000 emails!
