# 🚀 Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your session cookie
notepad .env  # Windows
nano .env     # Linux/Mac
```

### Get Your Session Cookie:

1. Visit: https://check.emailverifier.online/bulk-verify-email/index.php
2. Log in to your account
3. Press **F12** → **Application** → **Cookies**
4. Copy the **PHPSESSID** value
5. Paste it in `.env` file:
   ```
   EMAILVERIFIER_SESSION_COOKIE=your_cookie_here
   ```

## 3. Start the Server

### Option A: Using the start script (recommended)
```bash
python start.py
```

### Option B: Using uvicorn directly
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Option C: Using Docker
```bash
docker-compose up -d
```

## 4. Access the API

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

## 5. Test It!

### Using curl:

```bash
# Health check
curl http://localhost:8001/health

# Verify single email
curl -X POST http://localhost:8001/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"email": "test@gmail.com"}'

# Verify batch
curl -X POST http://localhost:8001/api/v1/verify/batch \
  -H "Content-Type: application/json" \
  -d '{"emails": ["test1@gmail.com", "test2@gmail.com"], "max_concurrent": 2}'
```

### Using Python:

```python
import requests

# Verify single email
response = requests.post(
  "http://localhost:8001/api/v1/verify",
    json={"email": "test@gmail.com"}
)
print(response.json())
```

## That's it! 🎉

Your API is now running and ready to verify emails!
