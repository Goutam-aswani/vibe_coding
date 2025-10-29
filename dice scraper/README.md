# Dice.com Job Scraper API

A FastAPI-based web scraper that extracts job posting information from Dice.com.

## Features

- 🔍 Search for jobs by keywords
- 🏠 Filter by workplace type (Remote, Hybrid, On-Site)
- 📄 Pagination support
- 📊 Extract comprehensive job details:
  - Job title
  - Company name
  - Location
  - Salary information
  - Job type (Full-time, Contract, etc.)
  - Job description snippet
  - Direct links to job postings
  - Company profile links
- 📚 Interactive API documentation (Swagger UI)
- ⚡ Fast and efficient scraping

## Installation

1. **Clone or navigate to the project directory:**
   ```powershell
   cd "z:\scraper\dice scraper"
   ```

2. **Create a virtual environment (recommended):**
   ```powershell
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

### Running the API

Start the FastAPI server:

```powershell
python main.py
```

Or using uvicorn directly:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base URL:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

### API Endpoints

#### 1. Root Endpoint
```
GET /
```
Returns basic API information.

#### 2. Health Check
```
GET /health
```
Check if the API is running.

#### 3. Search Jobs
```
GET /jobs?q=AI+engineer&workplace_type=Remote&page=1
```

**Query Parameters:**
- `q` (string): Search query for job title or keywords (default: "AI engineer")
- `workplace_type` (string): Workplace type filter - "Remote", "Hybrid", or "On-Site" (default: "Remote")
- `page` (integer): Page number, starting from 1 (default: 1)

**Example Response:**
```json
{
  "total_jobs": 20,
  "search_query": "AI engineer",
  "filters": {
    "workplace_type": "Remote",
    "page": 1
  },
  "jobs": [
    {
      "title": "AI Engineer",
      "company": "AaraTechnologies Inc",
      "location": "Remote or Hybrid in Sherborn, Massachusetts",
      "posted_date": "Today",
      "salary": "$60,000 - $80,000",
      "job_type": "Contract",
      "description": "Job Title: AI Engineer Company: Aaratech Inc Job Summary...",
      "job_url": "https://www.dice.com/job-detail/...",
      "company_url": "https://www.dice.com/company-profile/..."
    }
  ]
}
```

## Example Usage

### Using cURL

```powershell
# Search for AI engineer jobs (Remote)
curl "http://localhost:8000/jobs?q=AI+engineer&workplace_type=Remote&page=1"

# Search for Python developer jobs (Hybrid)
curl "http://localhost:8000/jobs?q=Python+developer&workplace_type=Hybrid&page=1"
```

### Using Python

```python
import requests

# Make a request to the API
response = requests.get(
    "http://localhost:8000/jobs",
    params={
        "q": "AI engineer",
        "workplace_type": "Remote",
        "page": 1
    }
)

# Parse the JSON response
data = response.json()

# Print job titles
for job in data["jobs"]:
    print(f"{job['title']} at {job['company']}")
```

### Using JavaScript (Browser/Node.js)

```javascript
fetch('http://localhost:8000/jobs?q=AI+engineer&workplace_type=Remote&page=1')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.total_jobs} jobs`);
    data.jobs.forEach(job => {
      console.log(`${job.title} at ${job.company}`);
    });
  });
```

## Interactive Documentation

Once the server is running, visit http://localhost:8000/docs to access the interactive Swagger UI documentation where you can:
- View all available endpoints
- See request/response schemas
- Test the API directly from your browser
- Download OpenAPI specification

## Project Structure

```
dice scraper/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **BeautifulSoup4**: HTML parsing library
- **Requests**: HTTP library for making requests
- **lxml**: Fast XML/HTML parser
- **Pydantic**: Data validation using Python type hints

## Notes

- The scraper uses appropriate headers to mimic browser requests
- Results may vary based on Dice.com's current page structure
- Be respectful of the website's resources and implement rate limiting if making frequent requests
- Some job details may be incomplete if they're not available in the search results page

## Troubleshooting

### Import Errors
If you get import errors, make sure all dependencies are installed:
```powershell
pip install -r requirements.txt
```

### Connection Errors
If the scraper can't connect to Dice.com:
- Check your internet connection
- Verify that Dice.com is accessible from your location
- The website structure may have changed (scraper may need updates)

### No Jobs Found
If the API returns no jobs:
- Try different search queries
- Check if the workplace type filter is too restrictive
- The website structure may have changed

## License

This project is for educational purposes only. Please respect Dice.com's Terms of Service and robots.txt when using this scraper.
