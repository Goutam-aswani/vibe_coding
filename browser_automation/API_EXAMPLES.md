# API Examples & Testing

This document provides real-world examples of API requests and responses.

## Base URL

```
http://localhost:8000
```

## Authentication

No authentication required (runs locally).

---

## 1. Health Check

### Request
```bash
curl -X GET http://localhost:8000/health
```

### Response
```json
{
  "status": "healthy",
  "browser_ready": true,
  "active_sessions": 2
}
```

---

## 2. Start Application

### Request
```bash
curl -X POST http://localhost:8000/start-application \
  -H "Content-Type: application/json" \
  -d '{
    "job_url": "https://www.linkedin.com/jobs/view/4308463479/"
  }'
```

### PowerShell
```powershell
$body = @{
    job_url = "https://www.linkedin.com/jobs/view/4308463479/"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/start-application" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

### Response (Success - Step 1)
```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "waiting_for_input",
  "job_title": "Data Associate - Gurgaon",
  "company_name": "Circles",
  "current_step": {
    "step_number": 1,
    "step_title": "Contact info",
    "fields": [
      {
        "field_id": "single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4308463479-3755887435086266-phoneNumber-nationalNumber",
        "field_type": "phone",
        "label": "Mobile phone number",
        "placeholder": null,
        "required": true,
        "options": null,
        "current_value": "+1234567890",
        "hint": null
      },
      {
        "field_id": "text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4308463479-3755887435086266-city",
        "field_type": "text",
        "label": "City",
        "placeholder": null,
        "required": true,
        "options": null,
        "current_value": "New York",
        "hint": null
      }
    ],
    "screenshot_path": "screenshots/f47ac10b-58cc-4372-a567-0e02b2c3d479_step_1.png",
    "has_next_step": true
  },
  "message": "Extracted 2 fields from step 1. Waiting for answers.",
  "error": null,
  "total_steps": null
}
```

### Response (Failed - Not Easy Apply)
```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "failed",
  "job_title": "Data Associate - Gurgaon",
  "company_name": "Circles",
  "current_step": null,
  "message": "Easy Apply button not found or job not available for Easy Apply",
  "error": "Easy Apply not available",
  "total_steps": null
}
```

---

## 3. Submit Application (Step 1)

### Request
```bash
curl -X POST http://localhost:8000/submit-application \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "answers": [
      {
        "field_id": "single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4308463479-3755887435086266-phoneNumber-nationalNumber",
        "value": "+1234567890"
      },
      {
        "field_id": "text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4308463479-3755887435086266-city",
        "value": "New York"
      }
    ],
    "continue_to_next": true
  }'
```

### PowerShell
```powershell
$body = @{
    session_id = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    answers = @(
        @{
            field_id = "phone-field-id"
            value = "+1234567890"
        },
        @{
            field_id = "city-field-id"
            value = "New York"
        }
    )
    continue_to_next = $true
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8000/submit-application" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

### Response (More Steps)
```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "waiting_for_input",
  "job_title": "Data Associate - Gurgaon",
  "company_name": "Circles",
  "current_step": {
    "step_number": 2,
    "step_title": "Resume",
    "fields": [
      {
        "field_id": "jobs-document-upload-file-input-upload-resume",
        "field_type": "file",
        "label": "Resume",
        "placeholder": null,
        "required": true,
        "options": null,
        "current_value": null,
        "hint": "Accepted formats: .pdf, .doc, .docx"
      },
      {
        "field_id": "jobs-document-upload-file-input-upload-cover-letter",
        "field_type": "file",
        "label": "Cover Letter (optional)",
        "placeholder": null,
        "required": false,
        "options": null,
        "current_value": null,
        "hint": null
      }
    ],
    "screenshot_path": "screenshots/f47ac10b-58cc-4372-a567-0e02b2c3d479_step_2.png",
    "has_next_step": true
  },
  "message": "Moved to step 2. Extracted 2 fields.",
  "error": null,
  "total_steps": null
}
```

### Response (Completed)
```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "completed",
  "job_title": "Data Associate - Gurgaon",
  "company_name": "Circles",
  "current_step": null,
  "message": "Application submitted successfully!",
  "error": null,
  "total_steps": null
}
```

---

## 4. Complex Multi-Step Example

### Step 2 Response (Work Experience)
```json
{
  "session_id": "abc-123-def",
  "status": "waiting_for_input",
  "job_title": "Software Engineer",
  "company_name": "Tech Corp",
  "current_step": {
    "step_number": 2,
    "step_title": "Work experience",
    "fields": [
      {
        "field_id": "urn-li-jobs-screening-question-123-experience",
        "field_type": "select",
        "label": "How many years of experience do you have with Python?",
        "required": true,
        "options": [
          "Less than 1 year",
          "1-2 years",
          "3-5 years",
          "5-10 years",
          "10+ years"
        ],
        "current_value": null
      },
      {
        "field_id": "urn-li-jobs-screening-question-124-authorization",
        "field_type": "radio",
        "label": "Are you authorized to work in the United States?",
        "required": true,
        "options": ["Yes", "No"],
        "current_value": null
      },
      {
        "field_id": "urn-li-jobs-screening-question-125-relocation",
        "field_type": "radio",
        "label": "Are you willing to relocate?",
        "required": false,
        "options": ["Yes", "No"],
        "current_value": null
      },
      {
        "field_id": "urn-li-jobs-screening-question-126-sponsorship",
        "field_type": "radio",
        "label": "Will you now or in the future require sponsorship?",
        "required": true,
        "options": ["Yes", "No"],
        "current_value": null
      }
    ],
    "screenshot_path": "screenshots/abc-123-def_step_2.png",
    "has_next_step": true
  },
  "message": "Moved to step 2. Extracted 4 fields."
}
```

### Submit Step 2
```json
{
  "session_id": "abc-123-def",
  "answers": [
    {
      "field_id": "urn-li-jobs-screening-question-123-experience",
      "value": "3-5 years"
    },
    {
      "field_id": "urn-li-jobs-screening-question-124-authorization",
      "value": "Yes"
    },
    {
      "field_id": "urn-li-jobs-screening-question-125-relocation",
      "value": "Yes"
    },
    {
      "field_id": "urn-li-jobs-screening-question-126-sponsorship",
      "value": "No"
    }
  ],
  "continue_to_next": true
}
```

---

## 5. List Active Sessions

### Request
```bash
curl -X GET http://localhost:8000/sessions
```

### Response
```json
{
  "active_sessions": 3,
  "sessions": [
    {
      "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "job_title": "Data Associate - Gurgaon",
      "company_name": "Circles",
      "current_step": 2
    },
    {
      "session_id": "abc-123-def-456",
      "job_title": "Software Engineer",
      "company_name": "Tech Corp",
      "current_step": 1
    },
    {
      "session_id": "xyz-789-ghi-012",
      "job_title": "Product Manager",
      "company_name": "StartupCo",
      "current_step": 3
    }
  ]
}
```

---

## 6. Cancel Session

### Request
```bash
curl -X DELETE http://localhost:8000/session/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

### Response
```json
{
  "message": "Session f47ac10b-58cc-4372-a567-0e02b2c3d479 cancelled"
}
```

---

## Field Type Examples

### Text Input
```json
{
  "field_id": "firstName",
  "field_type": "text",
  "label": "First name",
  "required": true,
  "current_value": "John"
}
```
**Answer:** `{"field_id": "firstName", "value": "John"}`

### Email Input
```json
{
  "field_id": "emailAddress",
  "field_type": "email",
  "label": "Email address",
  "required": true,
  "current_value": "john@example.com"
}
```
**Answer:** `{"field_id": "emailAddress", "value": "john@example.com"}`

### Phone Input
```json
{
  "field_id": "phoneNumber",
  "field_type": "phone",
  "label": "Mobile phone number",
  "required": true,
  "current_value": null
}
```
**Answer:** `{"field_id": "phoneNumber", "value": "+1234567890"}`

### Select/Dropdown
```json
{
  "field_id": "experienceLevel",
  "field_type": "select",
  "label": "Years of experience",
  "required": true,
  "options": ["0-1 years", "1-3 years", "3-5 years", "5-10 years", "10+ years"],
  "current_value": null
}
```
**Answer:** `{"field_id": "experienceLevel", "value": "3-5 years"}`

### Radio Buttons
```json
{
  "field_id": "workAuthorization",
  "field_type": "radio",
  "label": "Are you authorized to work in this country?",
  "required": true,
  "options": ["Yes", "No"],
  "current_value": null
}
```
**Answer:** `{"field_id": "workAuthorization", "value": "Yes"}`

### Checkbox
```json
{
  "field_id": "agreeToTerms",
  "field_type": "checkbox",
  "label": "I agree to the terms and conditions",
  "required": true,
  "current_value": "unchecked"
}
```
**Answer:** `{"field_id": "agreeToTerms", "value": true}`

### Textarea
```json
{
  "field_id": "coverLetter",
  "field_type": "textarea",
  "label": "Why do you want to work here?",
  "required": false,
  "current_value": null
}
```
**Answer:** `{"field_id": "coverLetter", "value": "I am passionate about..."}`

### File Upload
```json
{
  "field_id": "resumeUpload",
  "field_type": "file",
  "label": "Upload Resume",
  "required": true,
  "hint": "Accepted formats: .pdf, .doc, .docx"
}
```
**Answer:** `{"field_id": "resumeUpload", "value": "resume"}`

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Failed to navigate to job URL"
}
```

### 404 Not Found
```json
{
  "detail": "Session abc-123-def not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Application start failed: Timeout waiting for selector"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Browser not initialized"
}
```

---

## Python Client Example

```python
import requests
import time

class LinkedInAutomation:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def health_check(self):
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def start_application(self, job_url):
        response = requests.post(
            f"{self.base_url}/start-application",
            json={"job_url": job_url}
        )
        return response.json()
    
    def submit_application(self, session_id, answers, continue_next=True):
        response = requests.post(
            f"{self.base_url}/submit-application",
            json={
                "session_id": session_id,
                "answers": answers,
                "continue_to_next": continue_next
            }
        )
        return response.json()
    
    def list_sessions(self):
        response = requests.get(f"{self.base_url}/sessions")
        return response.json()
    
    def cancel_session(self, session_id):
        response = requests.delete(f"{self.base_url}/session/{session_id}")
        return response.json()

# Usage
client = LinkedInAutomation()

# Check health
health = client.health_check()
print(f"Service status: {health['status']}")

# Start application
job_url = "https://www.linkedin.com/jobs/view/4308463479/"
result = client.start_application(job_url)

if result['status'] == 'waiting_for_input':
    session_id = result['session_id']
    fields = result['current_step']['fields']
    
    # Process with AI (pseudo-code)
    answers = process_with_ai(fields)
    
    # Submit
    submit_result = client.submit_application(session_id, answers)
    print(f"Submit status: {submit_result['status']}")
```

---

## Batch Processing Example

```python
import requests
import time

def apply_to_jobs(job_urls):
    base_url = "http://localhost:8000"
    results = []
    
    for i, job_url in enumerate(job_urls):
        print(f"\n[{i+1}/{len(job_urls)}] Processing: {job_url}")
        
        try:
            # Start application
            response = requests.post(
                f"{base_url}/start-application",
                json={"job_url": job_url}
            )
            data = response.json()
            
            if data['status'] == 'failed':
                results.append({
                    'url': job_url,
                    'status': 'failed',
                    'error': data['message']
                })
                continue
            
            session_id = data['session_id']
            
            # Process all steps
            while data['status'] == 'waiting_for_input':
                fields = data['current_step']['fields']
                
                # Get AI answers (you implement this)
                answers = get_ai_answers(fields)
                
                # Submit
                response = requests.post(
                    f"{base_url}/submit-application",
                    json={
                        "session_id": session_id,
                        "answers": answers,
                        "continue_to_next": True
                    }
                )
                data = response.json()
            
            # Record result
            results.append({
                'url': job_url,
                'status': data['status'],
                'job_title': data.get('job_title'),
                'company': data.get('company_name')
            })
            
            # Rate limiting
            time.sleep(5)
            
        except Exception as e:
            results.append({
                'url': job_url,
                'status': 'error',
                'error': str(e)
            })
    
    return results

# Process 800 jobs
job_urls = [...]  # Your 800-1000 URLs
results = apply_to_jobs(job_urls)

# Summary
successful = sum(1 for r in results if r['status'] == 'completed')
failed = len(results) - successful
print(f"\nCompleted: {successful}/{len(results)}")
print(f"Failed: {failed}")
```

---

## Interactive Testing with HTTPie

```bash
# Install httpie
pip install httpie

# Health check
http GET localhost:8000/health

# Start application
http POST localhost:8000/start-application \
  job_url="https://www.linkedin.com/jobs/view/4308463479/"

# Submit application
http POST localhost:8000/submit-application \
  session_id="abc-123" \
  answers:='[{"field_id":"phone","value":"+1234567890"}]' \
  continue_to_next:=true

# List sessions
http GET localhost:8000/sessions

# Cancel session
http DELETE localhost:8000/session/abc-123
```

---

## Postman Collection

Import this JSON into Postman:

```json
{
  "info": {
    "name": "LinkedIn Automation API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/health",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["health"]
        }
      }
    },
    {
      "name": "Start Application",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"job_url\": \"https://www.linkedin.com/jobs/view/4308463479/\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/start-application",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["start-application"]
        }
      }
    },
    {
      "name": "Submit Application",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"session_id\": \"{{session_id}}\",\n  \"answers\": [],\n  \"continue_to_next\": true\n}"
        },
        "url": {
          "raw": "http://localhost:8000/submit-application",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["submit-application"]
        }
      }
    }
  ]
}
```

---

That's it! Use these examples to test and integrate with your LinkedIn automation service. 🚀
