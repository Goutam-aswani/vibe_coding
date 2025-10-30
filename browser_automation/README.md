# LinkedIn Easy Apply Automation 🤖

Automate LinkedIn Easy Apply job applications using browser automation and AI-powered form filling. Integrate with n8n for complete workflow automation.

## 🌟 Features

- **Browser Automation**: Uses Playwright with stealth mode to avoid detection
- **Smart Form Extraction**: Automatically detects and extracts all form fields (text, select, radio, checkboxes, file uploads)
- **AI Integration**: Returns form fields as JSON for processing with Gemini or other AI models
- **Multi-Step Support**: Handles LinkedIn's multi-step Easy Apply forms
- **Session Management**: Maintains browser sessions with login persistence
- **REST API**: FastAPI endpoints for easy n8n integration
- **Screenshot Capture**: Takes screenshots at each step for verification
- **Human-like Behavior**: Adds delays and realistic interactions to avoid detection

## 📋 Prerequisites

- Python 3.9+
- Windows/Linux/Mac
- LinkedIn account
- Resume and cover letter PDFs (optional)

## 🚀 Quick Start

### 1. Installation

```powershell
# Clone or navigate to the project directory
cd z:\vibe_coding\browser_automation

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configuration

```powershell
# Copy the example env file
copy .env.example .env

# Edit .env with your settings
notepad .env
```

**Important `.env` settings:**

```env
# Browser Settings
HEADLESS=false  # Set to true for headless mode (not recommended for LinkedIn)
SLOW_MO=100     # Delay between actions (milliseconds)

# File Paths
RESUME_PATH=./documents/resume.pdf
COVER_LETTER_PATH=./documents/cover_letter.pdf

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Prepare Documents

Place your resume and cover letter in the `documents/` folder:

```powershell
# Copy your files
copy "C:\path\to\your\resume.pdf" .\documents\resume.pdf
copy "C:\path\to\your\cover_letter.pdf" .\documents\cover_letter.pdf
```

### 4. Run the Service

```powershell
# Activate virtual environment if not already activated
.\venv\Scripts\activate

# Run the server
python main.py
```

The service will:
1. Start the browser
2. Open LinkedIn
3. Wait for you to log in manually (if not already logged in)
4. Keep the session persistent for future applications

**First-time login**: A browser window will open. Log in to LinkedIn manually. The session will be saved for future use.

## 📡 API Endpoints

### Health Check
```http
GET http://localhost:8000/health
```

### Start Application
```http
POST http://localhost:8000/start-application
Content-Type: application/json

{
  "job_url": "https://www.linkedin.com/jobs/view/1234567890/"
}
```

**Response:**
```json
{
  "session_id": "abc-123-def",
  "status": "waiting_for_input",
  "job_title": "Data Associate",
  "company_name": "Circles",
  "current_step": {
    "step_number": 1,
    "step_title": "Contact info",
    "fields": [
      {
        "field_id": "firstName",
        "field_type": "text",
        "label": "First Name",
        "required": true,
        "current_value": "John"
      },
      {
        "field_id": "phone",
        "field_type": "phone",
        "label": "Phone number",
        "required": true,
        "current_value": null
      }
    ],
    "screenshot_path": "screenshots/abc-123-def_step_1.png",
    "has_next_step": true
  },
  "message": "Extracted 5 fields from step 1. Waiting for answers."
}
```

### Submit Answers
```http
POST http://localhost:8000/submit-application
Content-Type: application/json

{
  "session_id": "abc-123-def",
  "answers": [
    {
      "field_id": "phone",
      "value": "+1234567890"
    },
    {
      "field_id": "yearsOfExperience",
      "value": "3-5 years"
    }
  ],
  "continue_to_next": true
}
```

**Response (if more steps):**
```json
{
  "session_id": "abc-123-def",
  "status": "waiting_for_input",
  "job_title": "Data Associate",
  "company_name": "Circles",
  "current_step": {
    "step_number": 2,
    "fields": [...]
  },
  "message": "Moved to step 2. Extracted 3 fields."
}
```

**Response (if complete):**
```json
{
  "session_id": "abc-123-def",
  "status": "completed",
  "job_title": "Data Associate",
  "company_name": "Circles",
  "message": "Application submitted successfully!"
}
```

### List Active Sessions
```http
GET http://localhost:8000/sessions
```

### Cancel Session
```http
DELETE http://localhost:8000/session/{session_id}
```

## 🔗 n8n Integration

### Workflow Overview

```
[Gemini Node] → [HTTP Request: Start] → [AI Process Fields] → [HTTP Request: Submit] → [Loop or Done]
```

### Example n8n Workflow

1. **Webhook Trigger** - Receives job URL
2. **HTTP Request Node** - Start Application
   - Method: POST
   - URL: `http://localhost:8000/start-application`
   - Body: `{ "job_url": "{{$json.job_url}}" }`

3. **Google Gemini Node** - Process Questions
   - Prompt: 
   ```
   You are filling out a LinkedIn job application. Answer these questions:
   {{JSON.stringify($json.current_step.fields)}}
   
   Respond ONLY with a JSON array in this format:
   [{"field_id": "...", "value": "..."}]
   ```

4. **Code Node** - Parse AI Response
   ```javascript
   return [{
     json: {
       session_id: $json.session_id,
       answers: JSON.parse($json.gemini_response),
       continue_to_next: true
     }
   }];
   ```

5. **HTTP Request Node** - Submit Answers
   - Method: POST
   - URL: `http://localhost:8000/submit-application`
   - Body: `{{$json}}`

6. **IF Node** - Check if complete
   - If `status === "waiting_for_input"` → Loop back to step 3
   - If `status === "completed"` → Success notification

### n8n Workflow JSON

Create a new workflow in n8n and import this configuration:

```json
{
  "name": "LinkedIn Auto Apply",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "job-apply",
        "responseMode": "responseNode",
        "options": {}
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8000/start-application",
        "options": {},
        "bodyParametersJson": "={{ {\"job_url\": $json.job_url} }}"
      },
      "name": "Start Application",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300]
    },
    {
      "parameters": {
        "prompt": "=You are filling a LinkedIn job application. Answer these questions professionally based on a candidate with relevant experience:\n\n{{ JSON.stringify($json.current_step.fields, null, 2) }}\n\nReturn ONLY a JSON array with this exact format:\n[{\"field_id\": \"field_name\", \"value\": \"your_answer\"}]\n\nRules:\n- For phone numbers, use format: +1234567890\n- For years of experience, use format: 3-5 years\n- For yes/no questions, answer: Yes or No\n- For file uploads, answer: resume or cover_letter\n- Be specific and professional"
      },
      "name": "Gemini Answer",
      "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
      "position": [650, 300]
    },
    {
      "parameters": {
        "jsCode": "const geminiResponse = $json.response;\nlet answers;\n\ntry {\n  answers = JSON.parse(geminiResponse);\n} catch (e) {\n  // Try to extract JSON from markdown code blocks\n  const match = geminiResponse.match(/```json\\n?([\\s\\S]*?)```/);\n  if (match) {\n    answers = JSON.parse(match[1]);\n  } else {\n    throw new Error('Could not parse Gemini response');\n  }\n}\n\nreturn [{\n  json: {\n    session_id: $('Start Application').item.json.session_id,\n    answers: answers,\n    continue_to_next: true\n  }\n}];"
      },
      "name": "Parse Response",
      "type": "n8n-nodes-base.code",
      "position": [850, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8000/submit-application",
        "options": {},
        "bodyParametersJson": "={{ $json }}"
      },
      "name": "Submit Answers",
      "type": "n8n-nodes-base.httpRequest",
      "position": [1050, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.status }}",
              "value2": "waiting_for_input"
            }
          ]
        }
      },
      "name": "More Steps?",
      "type": "n8n-nodes-base.if",
      "position": [1250, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Start Application", "type": "main", "index": 0}]]
    },
    "Start Application": {
      "main": [[{"node": "Gemini Answer", "type": "main", "index": 0}]]
    },
    "Gemini Answer": {
      "main": [[{"node": "Parse Response", "type": "main", "index": 0}]]
    },
    "Parse Response": {
      "main": [[{"node": "Submit Answers", "type": "main", "index": 0}]]
    },
    "Submit Answers": {
      "main": [[{"node": "More Steps?", "type": "main", "index": 0}]]
    },
    "More Steps?": {
      "main": [
        [{"node": "Gemini Answer", "type": "main", "index": 0}],
        []
      ]
    }
  }
}
```

## 📊 Field Types

The system detects and handles these field types:

| Type | Description | Example Values |
|------|-------------|----------------|
| `text` | Text input | "John Doe" |
| `email` | Email input | "john@example.com" |
| `phone` | Phone input | "+1234567890" |
| `number` | Numeric input | "5" |
| `textarea` | Large text | "I am passionate about..." |
| `select` | Dropdown | "3-5 years" |
| `radio` | Radio buttons | "Yes" or "No" |
| `checkbox` | Checkbox | true/false |
| `file` | File upload | "resume" or "cover_letter" |

## 🎯 Usage Examples

### Simple Test

```powershell
# Start the service
python main.py

# In another terminal, test the API
curl -X POST http://localhost:8000/start-application -H "Content-Type: application/json" -d "{\"job_url\": \"https://www.linkedin.com/jobs/view/4308463479/\"}"
```

### Python Script

```python
import requests

# Start application
response = requests.post(
    "http://localhost:8000/start-application",
    json={"job_url": "https://www.linkedin.com/jobs/view/4308463479/"}
)

data = response.json()
session_id = data["session_id"]
fields = data["current_step"]["fields"]

print(f"Session: {session_id}")
print(f"Fields to fill: {len(fields)}")

# Process fields with AI (pseudo-code)
answers = ai_process_fields(fields)

# Submit answers
response = requests.post(
    "http://localhost:8000/submit-application",
    json={
        "session_id": session_id,
        "answers": answers,
        "continue_to_next": True
    }
)

print(response.json())
```

## 🔧 Troubleshooting

### Browser doesn't start
- Run: `playwright install chromium`
- Check if port 8000 is available
- Try setting `HEADLESS=false` in `.env`

### "Easy Apply button not found"
- Job might not support Easy Apply
- Page might still be loading - increase `TIMEOUT` in `.env`
- LinkedIn UI might have changed - check selectors

### "User not logged in"
- Set `HEADLESS=false` in `.env`
- Restart the service and log in manually when browser opens
- Browser profile is saved in `browser_data/` folder

### Fields not filling correctly
- Check the field ID in the error logs
- Verify the answer format matches the field type
- Some fields might have validation - check screenshots

### Rate limiting
- LinkedIn may limit applications per day
- Add delays between applications using `RATE_LIMIT_DELAY`
- Use realistic values (5-10 seconds minimum)

## ⚠️ Important Notes

### LinkedIn Terms of Service
- Automated use of LinkedIn violates their Terms of Service
- Use this tool responsibly and at your own risk
- Your account could be restricted or banned
- This is meant for educational/personal use only

### Best Practices
- **Rate Limiting**: Don't apply to more than 10-20 jobs per hour
- **Human Verification**: Review applications before submitting
- **Realistic Data**: Use accurate information about your experience
- **Monitor Screenshots**: Check screenshots folder to verify correctness
- **Session Management**: Don't run multiple sessions simultaneously

### Limitations
- Only works with "Easy Apply" jobs
- Cannot handle CAPTCHAs
- Some custom form fields might not be detected
- File uploads limited to resume and cover letter
- Complex multi-part questions might need manual review

## 📁 Project Structure

```
browser_automation/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .env                   # Your configuration (create this)
├── .gitignore            # Git ignore rules
├── src/
│   ├── browser_manager.py    # Browser automation
│   ├── question_extractor.py # Form field extraction
│   ├── form_filler.py        # Form filling logic
│   └── models.py             # Data models
├── documents/
│   ├── resume.pdf           # Your resume (add this)
│   └── cover_letter.pdf     # Your cover letter (add this)
├── screenshots/             # Auto-generated screenshots
└── browser_data/            # Persistent browser profile
```

## 🔄 Workflow Diagram

```
┌─────────────┐
│   n8n Job   │
│  URL Input  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  POST /start-application    │
│  - Navigate to job          │
│  - Click Easy Apply         │
│  - Extract form fields      │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Return Fields as JSON      │
│  {fields: [...], session_id}│
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  n8n → Gemini AI            │
│  Process questions          │
│  Generate answers           │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  POST /submit-application   │
│  - Fill form fields         │
│  - Click Next/Submit        │
│  - Extract next step        │
└──────┬──────────────────────┘
       │
       ├─► More steps? → Loop back to Gemini
       │
       └─► Completed! ✓
```

## 🚀 Scaling to 800-1000 Jobs

### Batch Processing Script

```python
import requests
import time
import json

jobs = [
    "https://www.linkedin.com/jobs/view/123/",
    "https://www.linkedin.com/jobs/view/456/",
    # ... 800-1000 more URLs
]

API_URL = "http://localhost:8000"
DELAY_BETWEEN_APPS = 10  # seconds

def apply_to_job(job_url):
    try:
        # Start application
        response = requests.post(
            f"{API_URL}/start-application",
            json={"job_url": job_url}
        )
        
        data = response.json()
        
        if data["status"] == "failed":
            print(f"❌ {job_url}: {data['message']}")
            return False
        
        session_id = data["session_id"]
        
        # Process all steps
        while data["status"] == "waiting_for_input":
            fields = data["current_step"]["fields"]
            
            # Get AI answers (integrate with your Gemini setup)
            answers = get_ai_answers(fields)
            
            # Submit
            response = requests.post(
                f"{API_URL}/submit-application",
                json={
                    "session_id": session_id,
                    "answers": answers,
                    "continue_to_next": True
                }
            )
            
            data = response.json()
        
        if data["status"] == "completed":
            print(f"✅ Applied to {data['job_title']} at {data['company_name']}")
            return True
        else:
            print(f"⚠️  {job_url}: {data['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error applying to {job_url}: {e}")
        return False

# Process all jobs
successful = 0
failed = 0

for i, job_url in enumerate(jobs):
    print(f"\n[{i+1}/{len(jobs)}] Processing: {job_url}")
    
    if apply_to_job(job_url):
        successful += 1
    else:
        failed += 1
    
    # Rate limiting
    if i < len(jobs) - 1:
        print(f"Waiting {DELAY_BETWEEN_APPS} seconds...")
        time.sleep(DELAY_BETWEEN_APPS)

print(f"\n✅ Successful: {successful}")
print(f"❌ Failed: {failed}")
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review screenshots in `screenshots/` folder
3. Check logs in the terminal
4. Review LinkedIn's UI for changes

## 📜 License

This project is for educational purposes only. Use at your own risk.

---

**Happy job hunting! 🎯**
