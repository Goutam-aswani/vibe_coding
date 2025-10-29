# 🎯 Static URLs - Quick Reference

## Verified Working URLs

These URLs have been tested and confirmed to work with the scraper:

### 1. Artificial Intelligence Jobs
```
https://www.hirist.tech/k/artificial-intelligence-jobs?ref=homepagetag&minexp=0&maxexp=1
```

### 2. Generative AI Jobs
```
https://www.hirist.tech/k/generative-ai-jobs?ref=homepagetag&minexp=0&maxexp=1
```

### 3. Machine Learning Jobs (Default)
```
https://www.hirist.tech/k/machine-learning-jobs?ref=homepagetag&minexp=0&maxexp=1
```

## API Usage Examples

### Option 1: Use Category Name (Recommended)

```bash
# Machine Learning jobs
curl http://localhost:8000/scrape-jobs?category=machine_learning

# Artificial Intelligence jobs
curl http://localhost:8000/scrape-jobs?category=artificial_intelligence

# Generative AI jobs
curl http://localhost:8000/scrape-jobs?category=generative_ai
```

### Option 2: Use Default URL

```bash
# Uses machine_learning by default
curl http://localhost:8000/scrape-jobs
```

### Option 3: Scrape All Categories at Once

```bash
# Scrapes all three categories and returns combined results
curl http://localhost:8000/scrape-all
```

### Option 4: Custom URL (Advanced)

```bash
# Use any Hirist.tech URL
curl "http://localhost:8000/scrape-jobs?url=https://www.hirist.tech/k/python-jobs"
```

## PowerShell Examples

```powershell
# Single category
Invoke-RestMethod -Uri "http://localhost:8000/scrape-jobs?category=machine_learning" | ConvertTo-Json -Depth 10

# All categories
Invoke-RestMethod -Uri "http://localhost:8000/scrape-all" | ConvertTo-Json -Depth 10

# Save to file
Invoke-RestMethod -Uri "http://localhost:8000/scrape-all" | ConvertTo-Json -Depth 10 | Out-File jobs.json
```

## Python Examples

```python
import httpx
import json

# Single category
response = httpx.get("http://localhost:8000/scrape-jobs?category=generative_ai")
data = response.json()
print(f"Found {data['jobs_count']} jobs")

# All categories
response = httpx.get("http://localhost:8000/scrape-all")
all_jobs = response.json()
print(f"Total unique jobs: {all_jobs['jobs_count']}")

# Save to file
with open('all_jobs.json', 'w', encoding='utf-8') as f:
    json.dump(all_jobs, f, indent=2, ensure_ascii=False)
```

## Available Categories

| Category Key | Description | URL |
|-------------|-------------|-----|
| `artificial_intelligence` | AI-related jobs | `/k/artificial-intelligence-jobs` |
| `generative_ai` | Generative AI jobs | `/k/generative-ai-jobs` |
| `machine_learning` | ML engineering jobs | `/k/machine-learning-jobs` |

## Response Format

```json
{
  "success": true,
  "jobs_count": 25,
  "jobs": [
    {
      "job_id": "1566140",
      "title": "Machine Learning Engineer",
      "company": "Tech Corp",
      "location": "Bangalore",
      "experience": "1 - 3 yrs",
      "posted_date": "1 day ago",
      "skills": ["Machine Learning", "Python", "TensorFlow"],
      "job_url": "https://www.hirist.tech/j/...",
      "company_rating": "4.5",
      "reviews_count": "10+",
      "is_premium": true
    }
  ],
  "message": "Successfully scraped 25 job postings"
}
```

## Tips

1. **Start with categories**: Use `category` parameter for faster, more reliable scraping
2. **Combine results**: Use `/scrape-all` to get comprehensive job listings
3. **Check logs**: Server console shows detailed scraping progress
4. **Save results**: Job postings change frequently, save important results

## Troubleshooting

### "No jobs found"
- Verify you're using one of the static URLs above
- Check your internet connection
- Website might be temporarily down

### Slow response
- Normal for scraping (5-15 seconds per URL)
- `/scrape-all` takes 15-45 seconds (scrapes 3 URLs)

### Duplicates in results
- `/scrape-all` automatically removes duplicates
- Single category scraping should have no duplicates
