# 🚀 Foundit Job Scraper API

A FastAPI-based web scraper for **foundit.in** (formerly Monster India) that extracts job listings using their official API. No browser automation needed - pure API scraping!

## ✨ Features

- 🎯 **Multiple Job Roles**: Search for multiple job roles in a single request
- 🚀 **Fast & Reliable**: Direct API access (10-50x faster than browser automation)
- 📊 **Comprehensive Data**: Extract all important job details
- 🔄 **Automatic Deduplication**: Removes duplicate jobs across different role searches
- 📝 **Interactive Docs**: Built-in Swagger UI for easy testing
- 🛡️ **Type Safe**: Full Pydantic validation

## 📦 Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

1. **Start the server:**
```bash
python main.py
```

2. **Open your browser:**
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

3. **Make a request:**

### Using cURL:
```bash
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "job_roles": ["gen ai engineer", "machine learning engineer"],
    "experience_range": "0~2",
    "country": "India",
    "limit_per_role": 50
  }'
```

### Using Python:
```python
import requests

response = requests.post(
    "http://localhost:8000/scrape",
    json={
        "job_roles": ["gen ai engineer", "data scientist"],
        "experience_range": "0~0",
        "country": "India",
        "limit_per_role": 100
    }
)

data = response.json()
print(f"Found {data['stats']['total_jobs_found']} jobs!")
```

### Using JavaScript/Fetch:
```javascript
fetch('http://localhost:8000/scrape', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    job_roles: ['gen ai engineer', 'python developer'],
    experience_range: '0~0',
    country: 'India',
    limit_per_role: 50
  })
})
.then(res => res.json())
.then(data => console.log(`Found ${data.stats.total_jobs_found} jobs!`));
```

## 📋 API Endpoints

### `POST /scrape`
Scrape jobs for multiple job roles.

**Request Body:**
```json
{
  "job_roles": ["gen ai engineer", "machine learning engineer"],
  "experience_range": "0~0",
  "country": "India",
  "limit_per_role": 100
}
```

**Parameters:**
- `job_roles` (required): List of job role queries
- `experience_range` (optional): Experience range in format "min~max" (default: "0~0")
  - Examples: "0~0" (freshers), "2~5" (2-5 years), "5~10" (5-10 years)
- `country` (optional): Country to search in (default: "India")
- `limit_per_role` (optional): Maximum jobs per role, 1-100 (default: 100)

**Response:**
```json
{
  "success": true,
  "message": "Successfully scraped 150 jobs for 2 role(s)",
  "stats": {
    "total_jobs_found": 150,
    "jobs_per_role": {
      "gen ai engineer": 80,
      "machine learning engineer": 70
    },
    "total_roles_searched": 2,
    "execution_time_seconds": 3.45,
    "timestamp": "2025-10-30T12:30:00"
  },
  "jobs": [
    {
      "job_id": "37214112",
      "title": "Gen AI Engineer",
      "company": {
        "name": "EXL",
        "company_id": 506824,
        "logo_url": "https://..."
      },
      "locations": [
        {
          "city": "Pune",
          "state": "Maharashtra",
          "country": "India",
          "lat_lon": "18.520430,73.856744"
        }
      ],
      "description": "Full job description here...",
      "experience": {
        "minimum_years": 0,
        "maximum_years": 2
      },
      "salary": {
        "currency": "INR",
        "minimum": 0,
        "maximum": 0,
        "is_disclosed": false
      },
      "skills": [
        {"name": "Python", "skill_id": "..."},
        {"name": "Machine Learning", "skill_id": "..."}
      ],
      "it_skills": [
        {"name": "TensorFlow", "skill_id": "..."}
      ],
      "apply_url": "https://www.linkedin.com/jobs/view/...",
      "posted_date": "2025-10-28T10:30:00",
      "job_types": ["Permanent Job"],
      "employment_types": ["Full time"],
      "industries": ["IT"],
      "functions": ["Ai/Ml Development"]
    }
  ]
}
```

### `GET /health`
Check API health status.

### `GET /`
Root endpoint with API information.

### `GET /example-request`
Get an example request body.

## 📊 Extracted Data Fields

For each job, the API extracts:

| Field | Description |
|-------|-------------|
| **job_id** | Unique job identifier |
| **title** | Job title |
| **company** | Company name, ID, and logo |
| **locations** | List of job locations (city, state, country) |
| **description** | Full job description (HTML format) |
| **experience** | Minimum and maximum years required |
| **salary** | Salary range (if disclosed) |
| **skills** | List of required skills |
| **it_skills** | List of IT/technical skills |
| **apply_url** | Direct application link |
| **posted_date** | When the job was posted |
| **job_types** | Type of job (Permanent, Contract, etc.) |
| **employment_types** | Full time, Part time, etc. |
| **industries** | Industry categories |
| **functions** | Job function categories |

## 🏗️ Project Structure

```
foundit scraper/
├── main.py              # FastAPI application
├── scraper.py           # Scraper logic
├── models.py            # Pydantic models
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## 🔧 Configuration

### Experience Ranges
- `"0~0"` - Freshers/Entry level
- `"0~2"` - 0-2 years
- `"2~5"` - 2-5 years
- `"5~10"` - 5-10 years
- `"10~15"` - 10-15 years

### Rate Limiting
The API implements automatic rate limiting to avoid overwhelming the source. Each role is scraped sequentially.

## 🐛 Error Handling

The API includes comprehensive error handling:
- Invalid requests return 400 with validation errors
- Scraping failures return 500 with error details
- All errors are logged for debugging

## 📝 Notes

- **Company Website**: Not available in API response (limitation of source API)
- **Salary**: Often not disclosed (value will be 0)
- **Duplicates**: Automatically removed across different role searches
- **Pagination**: Automatic - fetches up to specified limit

## 🎯 Example Use Cases

### 1. Search for Multiple Related Roles
```json
{
  "job_roles": [
    "python developer",
    "backend developer",
    "django developer"
  ],
  "limit_per_role": 50
}
```

### 2. Search for Experienced Positions
```json
{
  "job_roles": ["senior data scientist"],
  "experience_range": "5~10",
  "limit_per_role": 100
}
```

### 3. Quick Search for Few Results
```json
{
  "job_roles": ["gen ai engineer"],
  "experience_range": "0~0",
  "limit_per_role": 20
}
```

## 🤝 Contributing

Feel free to open issues or submit pull requests!

## 📄 License

MIT License

## ⚠️ Disclaimer

This tool is for educational purposes. Please respect foundit.in's terms of service and use responsibly. Do not overwhelm their servers with excessive requests.

---

**Built with ❤️ using FastAPI and Python**
