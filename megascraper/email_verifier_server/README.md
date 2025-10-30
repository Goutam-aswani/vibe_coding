# 🚀 Email Verifier REST API Server

A production-ready FastAPI server for email verification using check.emailverifier.online backend.

## ✨ Features

- ✅ **Single Email Verification** - Verify one email at a time
- ✅ **Batch Processing** - Verify multiple emails concurrently
- ✅ **Job Queue System** - Background processing for large batches
- ✅ **🔄 Automatic Cookie Refresh** - No more manual cookie updates every hour! ⭐ **NEW**
- ✅ **Rate Limiting** - Configurable delays between requests
- ✅ **Caching** - Redis-based caching (optional)
- ✅ **API Documentation** - Auto-generated Swagger/ReDoc UI
- ✅ **Health Checks** - Monitor server status
- ✅ **CORS Support** - Enable cross-origin requests
- ✅ **Environment Config** - Secure configuration management

## 📁 Project Structure

```
email_verifier_server/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API endpoints
│   │   └── dependencies.py     # Dependency injection
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration settings
│   │   └── security.py         # API key validation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py         # Request models
│   │   └── responses.py        # Response models
│   └── services/
│       ├── __init__.py
│       ├── verifier.py         # Email verification logic
│       └── queue.py            # Job queue manager
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_verifier.py
├── .env.example                # Example environment variables
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### 1. Installation

**Windows (One-Click Setup):**
```bash
setup.bat
```

**Or Manual Installation:**
```bash
cd email_verifier_server
pip install -r requirements.txt
playwright install chromium
```

### 2. Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```ini
# ⭐ NEW: Automatic Cookie Refresh (Recommended!)
# Set these to enable auto-refresh - no more manual cookie updates!
EMAILVERIFIER_EMAIL=your_email@example.com
EMAILVERIFIER_PASSWORD=your_password
COOKIE_REFRESH_INTERVAL=50  # Refresh every 50 minutes (before 60-min expiry)

# OR: Manual cookie management (old method)
EMAILVERIFIER_SESSION_COOKIE=your_phpsessid_here

# Optional: API security
API_KEY=your-secret-api-key-here

# Optional: Server settings
HOST=0.0.0.0
PORT=8001
WORKERS=4
RATE_LIMIT_DELAY=1.0
MAX_CONCURRENT=5
```

> **💡 Tip:** Use automatic cookie refresh to avoid manual updates every hour!
> See [COOKIE_AUTOREFRESH.md](COOKIE_AUTOREFRESH.md) for complete guide.

### 3. Run the Server

**Development mode:**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Production mode:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

**Using Docker:**
```bash
docker-compose up -d
```

### 4. Access the API

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

## 📚 API Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-27T12:00:00Z"
}
```

### Verify Single Email

```http
POST /api/v1/verify
Content-Type: application/json
X-API-Key: your-api-key

{
  "email": "test@example.com"
}
```

**Response:**
```json
{
  "email": "test@example.com",
  "status": "valid",
  "safetosend": "Yes",
  "type": "Free Account",
  "reasons": "success",
  "debug": ["Valid Email Domain DNS Found...", "..."],
  "verified_at": "2025-10-27T12:00:00Z",
  "processing_time_ms": 1234
}
```

### Verify Batch (Concurrent)

```http
POST /api/v1/verify/batch
Content-Type: application/json
X-API-Key: your-api-key

{
  "emails": [
    "user1@example.com",
    "user2@example.com",
    "user3@example.com"
  ],
  "max_concurrent": 5
}
```

**Response:**
```json
{
  "total": 3,
  "processed": 3,
  "valid": 2,
  "invalid": 1,
  "errors": 0,
  "processing_time_ms": 2456,
  "results": [
    {
      "email": "user1@example.com",
      "status": "valid",
      "safetosend": "Yes",
      "type": "Business",
      "reasons": "success"
    },
    ...
  ]
}
```

### Create Background Job

```http
POST /api/v1/jobs
Content-Type: application/json
X-API-Key: your-api-key

{
  "emails": ["email1@test.com", "email2@test.com", ...],
  "webhook_url": "https://yourapp.com/webhook" // optional
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "total_emails": 1000,
  "created_at": "2025-10-27T12:00:00Z"
}
```

### Get Job Status

```http
GET /api/v1/jobs/{job_id}
X-API-Key: your-api-key
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "total": 1000,
  "processed": 1000,
  "valid": 850,
  "invalid": 145,
  "errors": 5,
  "progress": 100,
  "created_at": "2025-10-27T12:00:00Z",
  "completed_at": "2025-10-27T12:30:00Z"
}
```

### Get Job Results

```http
GET /api/v1/jobs/{job_id}/results
X-API-Key: your-api-key
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "results": [
    {
      "email": "test@example.com",
      "status": "valid",
      "safetosend": "Yes",
      "type": "Free Account"
    },
    ...
  ]
}
```

## � Automatic Cookie Refresh ⭐ **NEW**

**Problem:** Session cookies expire every hour, requiring manual updates.

**Solution:** Automated browser-based login and cookie refresh!

### Quick Setup

1. **Add credentials to `.env`:**
```ini
EMAILVERIFIER_EMAIL=your_email@example.com
EMAILVERIFIER_PASSWORD=your_password
```

2. **Start the server** - cookies refresh automatically every 50 minutes!

### Manual Refresh (Optional)

```bash
python refresh_cookie.py
```

### Features
- ✅ **Zero Manual Intervention** - Runs 24/7 unattended
- ✅ **Self-Healing** - Auto-recovers from expired sessions
- ✅ **Transparent** - Works silently in background
- ✅ **Debug-Friendly** - Screenshots on errors

📚 **Complete Guide:** [COOKIE_AUTOREFRESH.md](COOKIE_AUTOREFRESH.md)

## �🔐 Security

### API Key Authentication

Set `API_KEY` in your `.env` file. All requests must include the header:

```http
X-API-Key: your-secret-api-key-here
```

### Rate Limiting

Configure rate limiting in `.env`:

```ini
RATE_LIMIT_DELAY=1.0  # Seconds between requests
MAX_CONCURRENT=5      # Max concurrent verifications
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t email-verifier-api .

# Run container
docker run -d \
  -p 8001:8001 \
  -e EMAILVERIFIER_SESSION_COOKIE=your_cookie \
  -e API_KEY=your_api_key \
  --name email-verifier \
  email-verifier-api
```

Or use docker-compose:

```bash
docker-compose up -d
```

## 📊 Performance

| Emails | Sequential | Concurrent (5x) | Concurrent (10x) |
|--------|-----------|----------------|-----------------|
| 10 | 20s | 4s | 2s |
| 100 | 3m | 40s | 20s |
| 1,000 | 30m | 6m | 3m |
| 10,000 | 5h | **1h** | **30m** |

## 🧪 Testing

Run tests:

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ --cov=app --cov-report=html
```

## 📝 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAILVERIFIER_SESSION_COOKIE` | Yes | - | PHPSESSID from check.emailverifier.online |
| `API_KEY` | No | - | API key for authentication |
| `HOST` | No | `0.0.0.0` | Server host |
| `PORT` | No | `8001` | Server port |
| `WORKERS` | No | `4` | Number of worker processes |
| `RATE_LIMIT_DELAY` | No | `1.0` | Delay between requests (seconds) |
| `MAX_CONCURRENT` | No | `5` | Max concurrent verifications |
| `REDIS_URL` | No | - | Redis URL for caching |
| `LOG_LEVEL` | No | `INFO` | Logging level |

## 🔄 Updates

To get a fresh session cookie:

1. Visit: https://check.emailverifier.online/bulk-verify-email/index.php
2. Log in to your account
3. Open DevTools (F12) → Application → Cookies
4. Copy `PHPSESSID` value
5. Update `.env` file

## 📞 Support

- **API Docs**: http://localhost:8001/docs
- **Health**: http://localhost:8001/health
- **Metrics**: http://localhost:8001/metrics

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ using FastAPI and check.emailverifier.online**
