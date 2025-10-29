# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT (Browser/curl/Python)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP Requests
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI APPLICATION                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  main.py - API Endpoints                             │   │
│  │  - GET /                  (Root)                     │   │
│  │  - GET /health            (Health Check)             │   │
│  │  - GET /scrape-jobs       (Main Scraper)             │   │
│  │  - GET /jobs/{job_id}     (Individual Job)           │   │
│  └───────────────────┬──────────────────────────────────┘   │
│                      │                                       │
│  ┌──────────────────▼──────────────────────────────────┐   │
│  │  models.py - Data Models (Pydantic)                 │   │
│  │  - JobPosting                                        │   │
│  │  - ScrapeResponse                                    │   │
│  │  - ErrorResponse                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │ Calls
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   SCRAPER MODULE                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  scraper.py - HiristScraper Class                    │   │
│  │                                                       │   │
│  │  Methods:                                            │   │
│  │  - fetch_page()      : Get HTML from URL            │   │
│  │  - parse_job_postings() : Extract job data          │   │
│  │  - extract_job_id()     : Parse job IDs             │   │
│  └───────────────────┬──────────────────────────────────┘   │
└────────────────────┬─┴──────────────────────────────────────┘
                     │        │
         ┌───────────▼────┐   └───────────────┐
         │                │                    │
    ┌────▼─────┐    ┌────▼────────┐    ┌──────▼──────┐
    │  httpx   │    │ BeautifulSoup│    │   lxml     │
    │  (HTTP)  │    │  (Parsing)   │    │  (Parser)  │
    └────┬─────┘    └──────────────┘    └────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                   HIRIST.TECH WEBSITE                        │
│  https://www.hirist.tech/c/ai-ml-jobs                       │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
1. CLIENT REQUEST
   └─→ GET /scrape-jobs?min_exp=0&max_exp=1

2. FASTAPI (main.py)
   └─→ Validates parameters
   └─→ Calls HiristScraper.scrape_jobs()

3. SCRAPER (scraper.py)
   └─→ fetch_page() - Downloads HTML using httpx
   └─→ parse_job_postings() - Parses with BeautifulSoup
       └─→ Finds all <a> tags with job links
       └─→ Extracts data for each job:
           - Job ID from URL
           - Title from URL pattern
           - Company name
           - Location
           - Experience
           - Skills
           - Posted date
           - Rating & reviews
           - Premium status

4. DATA VALIDATION (models.py)
   └─→ Each job validated with JobPosting model
   └─→ Response wrapped in ScrapeResponse model

5. API RESPONSE
   └─→ JSON returned to client
       {
         "success": true,
         "jobs_count": 20,
         "jobs": [...],
         "message": "..."
       }
```

## File Structure & Responsibilities

```
hirist.tech scraper/
│
├── main.py                 # 🚀 FastAPI app & endpoints
│   ├── Route definitions
│   ├── Error handling
│   └── CORS configuration
│
├── scraper.py             # 🕷️ Web scraping logic
│   ├── HiristScraper class
│   ├── HTML fetching
│   └── Data extraction
│
├── models.py              # 📊 Data models
│   ├── JobPosting
│   ├── ScrapeResponse
│   └── ErrorResponse
│
├── config.py              # ⚙️ Configuration
│   └── Settings class
│
├── test_api.py            # 🧪 Test script
│   └── API testing functions
│
├── requirements.txt       # 📦 Dependencies
├── .env                   # 🔐 Environment variables
├── .gitignore            # 🚫 Git ignore rules
├── start.ps1             # 🎬 Quick start script
├── README.md             # 📖 Full documentation
└── QUICKSTART.md         # ⚡ Quick start guide
```

## Technology Stack

```
┌─────────────────────────────────────────────────┐
│                  PYTHON 3.8+                     │
└─────────────────────────────────────────────────┘
            │           │           │
    ┌───────▼──┐   ┌────▼────┐   ┌─▼─────────┐
    │ FastAPI  │   │  httpx  │   │BeautifulSoup│
    │  0.115   │   │  0.27   │   │    4.12     │
    └──────────┘   └─────────┘   └─────────────┘
         │              │               │
    ┌────▼─────┐  ┌────▼────┐    ┌─────▼─────┐
    │Pydantic  │  │Uvicorn  │    │   lxml    │
    │   2.9    │  │  0.31   │    │   5.3     │
    └──────────┘  └─────────┘    └───────────┘
```

## Request/Response Flow Example

```
┌─────────────────────────────────────────────────────────────┐
│ 1. HTTP Request                                              │
│    GET /scrape-jobs?min_exp=1&max_exp=3                     │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. FastAPI validates & processes                             │
│    - Check parameters (1 <= min_exp <= max_exp)             │
│    - Build target URL                                        │
│    - Call scraper                                            │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Scraper fetches page                                      │
│    - httpx GET request to Hirist.tech                       │
│    - Returns HTML content                                    │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. BeautifulSoup parses HTML                                 │
│    - Find all job links: <a href="/j/job-title-123456">    │
│    - Extract text content                                    │
│    - Parse each field with regex                             │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Create JobPosting objects                                 │
│    - Validate with Pydantic                                  │
│    - Deduplicate jobs                                        │
│    - Build list                                              │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Return ScrapeResponse                                     │
│    - Wrap in response model                                  │
│    - Add metadata (count, message)                           │
│    - Serialize to JSON                                       │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. HTTP Response                                             │
│    Status: 200 OK                                            │
│    Content-Type: application/json                            │
│    Body: {success: true, jobs_count: 15, jobs: [...]}      │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 🎯 Async/Await Architecture
- Non-blocking I/O operations
- Handles multiple requests efficiently
- Uses httpx async client

### 🛡️ Error Handling
- Try-catch blocks at every level
- Custom HTTP exception handlers
- Detailed error logging
- Graceful degradation

### ✅ Data Validation
- Pydantic models ensure type safety
- Automatic validation of all inputs/outputs
- Schema generation for API docs

### 📝 Logging
- Comprehensive logging throughout
- Different levels (INFO, WARNING, ERROR)
- Helps with debugging and monitoring

### 🔄 Extensibility
- Modular design
- Easy to add new features
- Database-ready architecture
- Can add caching, rate limiting, etc.

## Performance Considerations

```
Typical Request Timeline:
┌──────────────────────────────────────────┐
│ HTTP Request           │ ~1ms             │
├──────────────────────────────────────────┤
│ Parameter Validation   │ <1ms             │
├──────────────────────────────────────────┤
│ HTTP Fetch (httpx)     │ 5-15s (network)  │
├──────────────────────────────────────────┤
│ HTML Parsing           │ 100-500ms        │
├──────────────────────────────────────────┤
│ Data Extraction        │ 200-1000ms       │
├──────────────────────────────────────────┤
│ Validation & Response  │ ~10ms            │
├──────────────────────────────────────────┤
│ TOTAL                  │ 6-17 seconds     │
└──────────────────────────────────────────┘
```

Most time spent on network I/O (fetching HTML).

## Security Considerations

1. **Rate Limiting**: Not implemented - add for production
2. **User Agent**: Spoofs browser to avoid blocking
3. **CORS**: Currently allows all origins - restrict in production
4. **Input Validation**: All inputs validated with Pydantic
5. **No Secrets**: No API keys or passwords required

---

This architecture is designed to be:
- ✅ Simple to understand
- ✅ Easy to extend
- ✅ Production-ready (with additional features)
- ✅ Well-documented
- ✅ Type-safe
- ✅ Testable
