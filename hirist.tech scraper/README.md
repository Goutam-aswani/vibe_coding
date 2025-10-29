# Hirist.tech Job Scraper API

A FastAPI-based web scraper that extracts job posting information from Hirist.tech, specifically targeting AI/ML job listings. This API provides clean, structured data about job postings including titles, companies, locations, skills, and more.

## Features

- 🚀 **Fast & Async**: Built with FastAPI and async/await for high performance
- 📊 **Structured Data**: Returns well-formatted JSON with Pydantic validation
- 🎯 **Targeted Scraping**: Extracts comprehensive job details including:
  - Job ID and title
  - Company name and rating
  - Location and experience requirements
  - Required skills and technologies
  - Posted date
  - Direct job URL
  - Premium job indicator
- 📝 **Auto-generated Documentation**: Interactive API docs at `/docs`
- 🔒 **Error Handling**: Robust error handling and logging
- 🌐 **CORS Enabled**: Ready for frontend integration

## Project Structure

```
hirist.tech scraper/
├── main.py              # FastAPI application and endpoints
├── scraper.py           # Web scraping logic with BeautifulSoup
├── models.py            # Pydantic data models
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Create environment file** (optional):
   ```powershell
   Copy-Item .env.example .env
   ```

## Usage

### Starting the Server

Run the FastAPI server:

```powershell
python main.py
```

Or using uvicorn directly:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

### API Endpoints

#### 1. Root Endpoint
```
GET /
```
Returns API information and available endpoints.

**Example Response:**
```json
{
  "message": "Welcome to Hirist.tech Job Scraper API",
  "version": "1.0.0",
  "endpoints": {
    "scrape_jobs": "/scrape-jobs",
    "health": "/health",
    "docs": "/docs"
  }
}
```

#### 2. Health Check
```
GET /health
```
Check if the API is running.

#### 3. Scrape Jobs (Main Endpoint)
```
GET /scrape-jobs
```

**Query Parameters:**
- `url` (optional): Custom Hirist.tech URL to scrape
- `min_exp` (optional): Minimum years of experience (0-20)
- `max_exp` (optional): Maximum years of experience (0-20)

**Example Requests:**

Using default URL (AI/ML jobs, 0-1 years experience):
```powershell
curl http://localhost:8000/scrape-jobs
```

With custom experience range:
```powershell
curl "http://localhost:8000/scrape-jobs?min_exp=2&max_exp=5"
```

With custom URL:
```powershell
curl "http://localhost:8000/scrape-jobs?url=https://www.hirist.tech/c/python-jobs"
```

**Example Response:**
```json
{
  "success": true,
  "jobs_count": 20,
  "jobs": [
    {
      "job_id": "1566140",
      "title": "Machine Learning Engineer",
      "company": "Tech Solutions Inc",
      "location": "Bangalore",
      "experience": "1 - 3 yrs",
      "posted_date": "1 day ago",
      "skills": ["Machine Learning", "Deep Learning", "Python"],
      "job_url": "https://www.hirist.tech/j/machine-learning-engineer-1566140",
      "company_rating": "4.7",
      "reviews_count": "5+",
      "is_premium": true
    }
  ],
  "message": "Successfully scraped 20 job postings"
}
```

### Interactive API Documentation

FastAPI automatically generates interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints
- See request/response schemas
- Try out API calls directly from the browser

## API Response Models

### JobPosting

```python
{
  "job_id": str,           # Unique job identifier
  "title": str,            # Job title
  "company": str | None,   # Company name
  "location": str | None,  # Job location
  "experience": str | None,# Required experience (e.g., "1 - 3 yrs")
  "posted_date": str | None,# When job was posted (e.g., "1 day ago")
  "skills": [str],         # List of required skills
  "job_url": str | None,   # Direct URL to job posting
  "company_rating": str | None,    # Company rating
  "reviews_count": str | None,     # Number of reviews
  "is_premium": bool       # Whether job is premium listing
}
```

### ScrapeResponse

```python
{
  "success": bool,         # Whether scraping succeeded
  "jobs_count": int,       # Number of jobs found
  "jobs": [JobPosting],    # List of job postings
  "message": str | None    # Additional information
}
```

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **BeautifulSoup4**: HTML parsing and web scraping
- **httpx**: Async HTTP client for fetching web pages
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running FastAPI
- **lxml**: Fast HTML/XML parser

## Development

### Code Quality

The code follows best practices:
- Type hints for better IDE support and type checking
- Comprehensive logging for debugging
- Pydantic models for data validation
- Async/await for efficient I/O operations
- Modular structure for maintainability

### Error Handling

The API includes robust error handling:
- HTTP exceptions for client errors (4xx)
- Server error handling (5xx)
- Detailed error messages in responses
- Request timeout handling
- Logging of all errors

### Logging

All significant operations are logged:
- Request URLs
- Number of jobs found
- Parsing errors
- HTTP errors
- Server errors

View logs in the console where the server is running.

## Limitations & Notes

1. **Website Structure**: The scraper parses the HTML structure of Hirist.tech. If the website changes its structure, the scraper may need updates.

2. **Rate Limiting**: Be respectful of the website's resources. Consider implementing rate limiting for production use.

3. **Dynamic Content**: If Hirist.tech loads jobs dynamically with JavaScript, this scraper may not capture all content (as it only parses the initial HTML).

4. **Database**: Currently, jobs are not persisted. For production use, integrate a database (PostgreSQL, MongoDB, etc.) to store scraped jobs.

5. **Legal**: Ensure compliance with Hirist.tech's Terms of Service and robots.txt before deploying in production.

## Future Enhancements

- [ ] Database integration for persistent storage
- [ ] Pagination support for multiple pages
- [ ] Job detail page scraping
- [ ] Filter by skills, location, etc.
- [ ] Rate limiting and caching
- [ ] Background job scheduling
- [ ] Email notifications for new jobs
- [ ] Search and filter scraped jobs
- [ ] Export to CSV/Excel

## Troubleshooting

### Import Errors
If you get import errors, ensure all dependencies are installed:
```powershell
pip install -r requirements.txt
```

### Connection Timeouts
If scraping times out, increase the timeout in `scraper.py`:
```python
scraper = HiristScraper(timeout=60)  # 60 seconds
```

### No Jobs Found
- Verify the URL is correct
- Check if the website structure has changed
- Review logs for parsing errors
- Try accessing the URL in a browser

### Port Already in Use
If port 8000 is busy, use a different port:
```powershell
uvicorn main:app --port 8080
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Ensure you have permission to scrape the target website and comply with their Terms of Service.

## Support

For issues, questions, or contributions, please open an issue on the project repository.

---

**Built with ❤️ using FastAPI and Python**
