# 🔍 Naukri Job Scraper - FastAPI Server

A powerful FastAPI-based web application for scraping job listings from Naukri.com. Search multiple job roles simultaneously and get structured job data instantly!

## ✨ Features

- 🎯 **Multiple Job Role Search** - Search for one or many job roles at once
- ⚡ **Fast API Integration** - Direct API calls (no browser automation needed)
- 🎨 **Beautiful Web Interface** - Clean, responsive UI for easy scraping
- 📊 **Structured Data** - Get detailed job information in JSON format
- 🔄 **Pagination Support** - Scrape multiple pages per job role
- 🛡️ **Rate Limiting** - Built-in delays to respect server limits
- 📝 **RESTful API** - Use programmatically via REST endpoints

## 📋 What Data Gets Scraped?

For each job listing, you'll get:
- Job ID & Title
- Company Name & Logo
- Job Description
- Experience Range (min/max)
- Salary Range (min/max)
- Location(s)
- Skills/Tags
- Posted Date
- Direct Job URL
- And more...

## 🚀 Quick Start

### 1. Setup Virtual Environment

```powershell
# Create venv (already done)
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Server

```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Start the server
python main.py
```

The server will start on `http://localhost:8000`

### 3. Use the Application

**Web Interface:**
- Open browser: http://localhost:8000
- Enter job roles (comma-separated): `Python Developer, Data Scientist, Gen AI Engineer`
- Set max pages (1-20)
- Click "Start Scraping"

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔌 API Usage

### Scrape Jobs (POST)

**Endpoint:** `POST /api/scrape`

**Request Body:**
```json
{
  "keywords": ["Python Developer", "Data Scientist"],
  "max_pages": 3,
  "results_per_page": 20
}
```

**Example with cURL:**
```bash
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["Gen AI Engineer", "Machine Learning Engineer"],
    "max_pages": 2,
    "results_per_page": 20
  }'
```

**Example with Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/scrape",
    json={
        "keywords": ["Python Developer", "Data Scientist"],
        "max_pages": 3,
        "results_per_page": 20
    }
)

data = response.json()
print(f"Total jobs scraped: {data['results'][0]['jobs_scraped']}")
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully scraped 120 jobs for 2 keyword(s)",
  "total_keywords": 2,
  "results": [
    {
      "keyword": "Python Developer",
      "total_jobs_found": 5000,
      "jobs_scraped": 60,
      "pages_scraped": 3,
      "timestamp": "2025-10-30T12:00:00",
      "jobs": [
        {
          "job_id": "123456789",
          "title": "Senior Python Developer",
          "company_name": "Tech Corp",
          "job_description": "...",
          "experience": "3-5 Yrs",
          "salary": "10-15 Lacs PA",
          "locations": ["Bangalore", "Remote"],
          "skills": ["Python", "Django", "REST API"],
          "job_url": "https://www.naukri.com/job-listings-...",
          ...
        }
      ]
    }
  ]
}
```

## 📁 Project Structure

```
naukri scraper/
├── main.py                 # FastAPI application & routes
├── scraper.py              # Naukri API scraper logic
├── requirements.txt        # Python dependencies
├── templates/
│   ├── index.html         # Home page with search form
│   └── results.html       # Results display page
├── venv/                  # Virtual environment
└── README.md              # This file
```

## ⚙️ Configuration

### Scraper Settings (in `scraper.py`)

```python
BASE_URL = "https://www.naukri.com/jobapi/v3/search"
```

### Rate Limiting

- 1 second delay between pages
- 2 seconds delay between different keywords

### Default Values

- `max_pages`: 3 (can be 1-20)
- `results_per_page`: 20 (can be 10-50)

## 🎯 Use Cases

1. **Job Market Research** - Analyze job trends and requirements
2. **Skill Analysis** - See what skills are in demand
3. **Salary Benchmarking** - Compare salary ranges across roles
4. **Job Alerts** - Build custom job alert systems
5. **Portfolio Projects** - Integrate into your projects

## 🛠️ Technologies Used

- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **httpx** - Async HTTP client
- **Pydantic** - Data validation
- **Jinja2** - HTML templating

## 📝 Notes

- **Rate Limiting**: Built-in delays respect Naukri's servers
- **API Discovery**: Uses Naukri's internal API endpoint (discovered via network analysis)
- **No Browser Required**: Direct API calls make it fast and efficient
- **Legal**: For educational/personal use. Review Naukri's terms before heavy usage

## 🐛 Troubleshooting

**Server won't start:**
```powershell
# Ensure venv is activated
.\venv\Scripts\Activate.ps1

# Check if port 8000 is free
netstat -ano | findstr :8000

# Try a different port
uvicorn main:app --port 8001
```

**No jobs returned:**
- Check if Naukri.com is accessible
- Try different keywords
- Reduce max_pages to 1 for testing
- Check console for error messages

**Import errors:**
```powershell
pip install -r requirements.txt --force-reinstall
```

## 🚀 Future Enhancements

- [ ] Export to CSV/Excel
- [ ] Job filtering by experience/salary/location
- [ ] Email notifications for new jobs
- [ ] Database storage (SQLite/PostgreSQL)
- [ ] Job deduplication
- [ ] Company research integration
- [ ] Scheduled scraping (cron jobs)

## 📄 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

---

**Happy Job Hunting! 🎉**
