# 🚨 TROUBLESHOOTING: "No job postings found"

## ❌ Common Mistake in /docs Interface

### The Problem You're Seeing:
```json
{
  "success": true,
  "jobs_count": 0,
  "jobs": [],
  "message": "No job postings found. The page structure might have changed or no jobs match the criteria."
}
```

## ✅ THE SOLUTION (Follow These Exact Steps!)

### Step-by-Step Fix:

1. **Go to:** http://localhost:8005/docs
2. **Click on:** `GET /scrape-jobs`
3. **Click:** "Try it out" button
4. **IMPORTANT:** Look at the form fields:

   **DO THIS:**
   ```
   category: machine_learning    ← Type this
   url: [LEAVE COMPLETELY EMPTY] ← DELETE everything here!
   ```

   **NOT THIS (Wrong!):**
   ```
   category: machine_learning
   url: https://www.hirist.tech/k/machine-learning-jobs  ← DELETE THIS!
   ```

5. **Click:** "Execute"

## 🎯 Why This Happens

**The Swagger UI auto-fills the URL field** with example text. You MUST delete it!

When both `category` and `url` are filled:
- ❌ The URL takes priority
- ❌ Your category is ignored
- ❌ The URL gets encoded and fails

## ✅ Correct Usage Patterns

### Pattern 1: Use Category (RECOMMENDED)
```
category: machine_learning
url: [empty - DELETE ANY TEXT HERE]
```
**Result:** Uses our verified working URL ✅

### Pattern 2: Use Custom URL
```
category: [empty]
url: https://www.hirist.tech/k/python-jobs?ref=homepagetag&minexp=0&maxexp=1
```
**Result:** Uses your custom URL ✅

### Pattern 3: Use Default
```
category: [empty]
url: [empty]
```
**Result:** Uses default (machine_learning) ✅

### ❌ WRONG - Don't Do This
```
category: machine_learning
url: https://www.hirist.tech/k/machine-learning-jobs  ← Don't fill both!
```
**Result:** URL overrides category, might fail ❌

## 🔍 How to Check What's Being Sent

Look at the **"Request URL"** section in the response:

**GOOD (Category only):**
```
http://localhost:8005/scrape-jobs?category=machine_learning
```

**GOOD (URL only):**
```
http://localhost:8005/scrape-jobs?url=https%3A%2F%2Fwww.hirist.tech%2Fk%2Fpython-jobs
```

**BAD (Both filled):**
```
http://localhost:8005/scrape-jobs?category=machine_learning&url=https%3A%2F%2F...
                                                           ↑ This is the problem!
```

## 🎉 Better Alternative: Use /scrape-all

**No parameters needed!**

1. Go to: http://localhost:8005/docs
2. Click on: `GET /scrape-all`
3. Click: "Try it out"
4. Click: "Execute"
5. Done! ✅

This scrapes all three categories automatically with no configuration needed.

## 📝 Testing Checklist

- [ ] I cleared the URL field completely (not just selected the text, but deleted it)
- [ ] I only filled ONE field (either category OR url, not both)
- [ ] I checked the "Request URL" to confirm only one parameter is sent
- [ ] I checked the server console logs for errors

## 🔧 Advanced: Check Server Logs

In your PowerShell terminal where the server is running, you should see:

**Good logs:**
```
INFO:__main__:Using category 'machine_learning': https://www.hirist.tech/k/machine-learning-jobs?ref=homepagetag&minexp=0&maxexp=1
INFO:scraper:Fetching URL: https://www.hirist.tech/k/machine-learning-jobs...
INFO:scraper:Found 25 potential job links
INFO:scraper:Successfully parsed 25 unique job postings
```

**Bad logs:**
```
INFO:__main__:Using custom URL: https%3A%2F%2F...
ERROR: HTTP error occurred: 404
```

## 🆘 Still Not Working?

### Try the Simple Test:

**Option A: Use curl (bypasses Swagger UI issues)**
```powershell
curl http://localhost:8005/scrape-jobs?category=machine_learning
```

**Option B: Use Python**
```python
import httpx
response = httpx.get("http://localhost:8005/scrape-jobs?category=machine_learning")
print(response.json())
```

**Option C: Use /scrape-all endpoint**
```powershell
curl http://localhost:8005/scrape-all
```

If these work but the `/docs` interface doesn't, it's a Swagger UI form issue - make sure you're clearing the fields properly!

## 💡 Pro Tip

**Bookmark this URL in your browser:**
```
http://localhost:8005/scrape-all
```

Just visit it directly to get all jobs without any form-filling!

---

## Quick Reference

| Method | category field | url field | Result |
|--------|---------------|-----------|---------|
| ✅ Best | `machine_learning` | **EMPTY** | Works perfectly |
| ✅ Good | **EMPTY** | Custom URL | Works with custom URL |
| ✅ Good | **EMPTY** | **EMPTY** | Uses default |
| ❌ Bad | `machine_learning` | Example text | URL overrides, might fail |

**Remember:** In Swagger UI, DELETE the example text from the url field if you're using category!
