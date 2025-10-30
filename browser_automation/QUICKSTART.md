# Quick Setup Guide

## Step 1: Install Python Dependencies

```powershell
# Navigate to project
cd z:\vibe_coding\browser_automation

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Step 2: Configure Environment

```powershell
# Copy example config
copy .env.example .env

# Edit with notepad
notepad .env
```

**Minimum required settings:**
```env
HEADLESS=false
RESUME_PATH=./documents/resume.pdf
```

## Step 3: Add Your Documents

```powershell
# Copy your resume to documents folder
copy "C:\path\to\your\resume.pdf" .\documents\resume.pdf
```

## Step 4: Start the Service

```powershell
# Make sure venv is activated
.\venv\Scripts\activate

# Run the server
python main.py
```

**First time:** Browser will open, log in to LinkedIn manually. Session will be saved.

## Step 5: Test It

Open a new PowerShell terminal:

```powershell
# Test with curl
curl -X POST http://localhost:8000/start-application -H "Content-Type: application/json" -d "{\"job_url\": \"https://www.linkedin.com/jobs/view/4308463479/\"}"
```

Or visit: http://localhost:8000/docs for interactive API documentation

## Step 6: Create n8n Workflow

1. Open n8n (http://localhost:5678)
2. Create new workflow
3. Add **HTTP Request** node:
   - Method: POST
   - URL: `http://localhost:8000/start-application`
   - Body: `{"job_url": "{{ $json.job_url }}"}`

4. Add **Google Gemini** node:
   - Prompt: See README for full prompt
   
5. Add another **HTTP Request** node:
   - Method: POST
   - URL: `http://localhost:8000/submit-application`
   - Body: `{{ $json }}`

6. Test with a job URL!

## Common Issues

**"Browser not initialized"**
- Wait 10 seconds after starting the service
- Check terminal for errors

**"Easy Apply not found"**
- Job might not be Easy Apply
- Try a different job URL

**Fields not filling**
- Check screenshots in `screenshots/` folder
- Verify your answers match the expected format

## Next Steps

- Read the full README.md
- Check the n8n workflow example
- Test with multiple job applications
- Set up rate limiting for batch processing

---

That's it! You're ready to automate LinkedIn applications! 🚀
