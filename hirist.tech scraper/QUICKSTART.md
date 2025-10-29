# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies

Open PowerShell in the project directory and run:

```powershell
# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

**OR** use the automated script:

```powershell
.\start.ps1
```

### Step 2: Start the Server

```powershell
python main.py
```

The server will start at: **http://localhost:8000**

### Step 3: Test the API

**Option A: Using your browser**
1. Open http://localhost:8000/docs
2. Try the `/scrape-jobs` endpoint
3. Click "Execute" to see results

**Option B: Using the test script**
```powershell
# In a new PowerShell window (keep server running in the first)
python test_api.py
```

**Option C: Using curl**
```powershell
curl http://localhost:8000/scrape-jobs
```

## 📖 API Endpoints

### 1. Scrape Jobs (Main Endpoint)

```
GET /scrape-jobs
```

**Parameters:**
- `url` (optional): Custom URL to scrape
- `min_exp` (optional): Minimum years of experience (default: 0)
- `max_exp` (optional): Maximum years of experience (default: 1)

**Examples:**

Default (AI/ML jobs, 0-1 years exp):
```powershell
curl http://localhost:8000/scrape-jobs
```

Custom experience range:
```powershell
curl "http://localhost:8000/scrape-jobs?min_exp=2&max_exp=5"
```

Custom URL:
```powershell
curl "http://localhost:8000/scrape-jobs?url=https://www.hirist.tech/c/python-jobs"
```

### 2. Interactive Documentation

Visit http://localhost:8000/docs for:
- Full API documentation
- Interactive testing
- Request/response examples
- Schema definitions

## 📊 Understanding the Response

Each job posting includes:

```json
{
  "job_id": "1566140",              // Unique identifier
  "title": "Machine Learning Engineer",
  "company": "Tech Corp",           // Company name (if available)
  "location": "Bangalore",          // Job location
  "experience": "1 - 3 yrs",        // Experience requirement
  "posted_date": "1 day ago",       // When posted
  "skills": [                       // Required skills
    "Machine Learning",
    "Python",
    "Deep Learning"
  ],
  "job_url": "https://...",         // Direct link to job
  "company_rating": "4.7",          // Company rating (if available)
  "reviews_count": "5+",            // Number of reviews
  "is_premium": true                // Premium listing flag
}
```

## 🔧 Common Tasks

### Save Results to File

**Using PowerShell:**
```powershell
curl http://localhost:8000/scrape-jobs | Out-File -Encoding utf8 jobs.json
```

**Using Python:**
```python
import httpx
import json

response = httpx.get("http://localhost:8000/scrape-jobs")
with open("jobs.json", "w", encoding="utf-8") as f:
    json.dump(response.json(), f, indent=2)
```

### Filter Jobs by Skills

After scraping, filter in Python:

```python
import httpx

response = httpx.get("http://localhost:8000/scrape-jobs")
jobs = response.json()["jobs"]

# Filter jobs requiring Python
python_jobs = [j for j in jobs if "Python" in j["skills"]]
print(f"Found {len(python_jobs)} Python jobs")
```

### Change Server Port

Edit `main.py` or use command line:

```powershell
uvicorn main:app --host 0.0.0.0 --port 8080
```

## 🐛 Troubleshooting

### "Module not found" Error
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Server Won't Start
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Use different port
uvicorn main:app --port 8080
```

### No Jobs Found
- Verify the URL is accessible
- Check your internet connection
- Website structure may have changed
- Review server logs for errors

### Timeout Errors
Increase timeout in `scraper.py`:
```python
scraper = HiristScraper(timeout=60)  # 60 seconds
```

## 💡 Pro Tips

1. **View Logs**: The server console shows detailed logs of what's happening

2. **Multiple Tabs**: Open http://localhost:8000/docs in your browser while the server runs

3. **Save Regularly**: Job postings change frequently, save results periodically

4. **Respect Limits**: Don't overwhelm the website with too many requests

5. **Check Structure**: If scraping fails, the website HTML structure may have changed

## 🔄 Next Steps

1. **Database Integration**: Store jobs in PostgreSQL/MongoDB for persistence
2. **Scheduled Scraping**: Use cron/task scheduler to scrape automatically
3. **Notifications**: Get alerts for new relevant jobs
4. **Advanced Filtering**: Add more search parameters
5. **Job Details**: Scrape individual job pages for full descriptions

## 📚 Learn More

- FastAPI Documentation: https://fastapi.tiangolo.com/
- BeautifulSoup Docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- API Best Practices: https://restfulapi.net/

## 🆘 Need Help?

1. Check the console logs when running the server
2. Visit http://localhost:8000/docs for API documentation
3. Review README.md for detailed information
4. Check the code comments in main.py and scraper.py

---

Happy Scraping! 🎉
