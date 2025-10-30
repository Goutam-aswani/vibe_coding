# n8n Workflow Configuration

This document explains how to set up the complete n8n workflow for LinkedIn automation.

## Prerequisites

- n8n installed and running (http://localhost:5678)
- LinkedIn automation service running (http://localhost:8000)
- Google Gemini API key

## Workflow Overview

```
Trigger → Start Application → Gemini AI → Parse Response → Submit → Check Status → Loop or Complete
```

## Node Configuration

### 1. Manual Trigger / Webhook
**Purpose:** Start the workflow with a job URL

**Configuration:**
- Node Type: `Webhook` or `Manual Trigger`
- Input: `{ "job_url": "https://linkedin.com/jobs/view/..." }`

---

### 2. HTTP Request - Start Application
**Purpose:** Send job URL to automation service

**Configuration:**
```
Node Type: HTTP Request
Method: POST
URL: http://localhost:8000/start-application
Headers:
  Content-Type: application/json
Body (JSON):
{
  "job_url": "{{ $json.job_url }}"
}
```

**Output Example:**
```json
{
  "session_id": "abc-123-def",
  "status": "waiting_for_input",
  "job_title": "Data Associate",
  "company_name": "Circles",
  "current_step": {
    "step_number": 1,
    "fields": [
      {
        "field_id": "phone",
        "field_type": "phone",
        "label": "Phone number",
        "required": true
      }
    ]
  }
}
```

---

### 3. Google Gemini Node
**Purpose:** Process form fields and generate answers

**Configuration:**
```
Node Type: Google Gemini
Model: gemini-1.5-pro
Temperature: 0.3

Prompt:
You are an AI assistant helping to fill out a LinkedIn job application form professionally.

Below are the form fields that need to be filled. Generate appropriate answers based on a qualified candidate profile.

Form Fields:
{{ JSON.stringify($json.current_step.fields, null, 2) }}

Job Information:
- Title: {{ $json.job_title }}
- Company: {{ $json.company_name }}

Instructions:
1. Answer each field professionally and accurately
2. For phone numbers, use format: +1234567890
3. For years of experience dropdowns, choose realistic values like "3-5 years"
4. For yes/no questions, provide clear Yes or No answers
5. For text fields, provide concise, professional responses
6. For file upload fields, respond with either "resume" or "cover_letter"
7. Return ONLY a JSON array with no additional text

Response format (CRITICAL - only return this, nothing else):
[
  {"field_id": "field_name_here", "value": "your_answer_here"},
  {"field_id": "another_field", "value": "another_answer"}
]
```

**Advanced Prompt (with candidate context):**
```
You are filling a LinkedIn job application. Use this candidate profile:

Name: John Doe
Email: john.doe@example.com
Phone: +1234567890
Years of Experience: 5
Current Location: New York, NY
Work Authorization: Yes
LinkedIn: linkedin.com/in/johndoe
GitHub: github.com/johndoe

Answer these form fields:
{{ JSON.stringify($json.current_step.fields, null, 2) }}

Return ONLY this JSON format:
[{"field_id": "...", "value": "..."}]
```

---

### 4. Code Node - Parse Gemini Response
**Purpose:** Clean and parse AI response into proper format

**Configuration:**
```javascript
// Get the Gemini response
const geminiResponse = $input.first().json.response || 
                       $input.first().json.text || 
                       $input.first().json;

let answers;

try {
  // If response is already an object with answers
  if (Array.isArray(geminiResponse)) {
    answers = geminiResponse;
  } 
  // If response is a string
  else if (typeof geminiResponse === 'string') {
    // Try to extract JSON from markdown code blocks
    const jsonMatch = geminiResponse.match(/```json\s*([\s\S]*?)\s*```/);
    if (jsonMatch) {
      answers = JSON.parse(jsonMatch[1]);
    } 
    // Try to extract JSON array directly
    else if (geminiResponse.includes('[') && geminiResponse.includes(']')) {
      const arrayMatch = geminiResponse.match(/\[[\s\S]*\]/);
      if (arrayMatch) {
        answers = JSON.parse(arrayMatch[0]);
      } else {
        answers = JSON.parse(geminiResponse);
      }
    }
    else {
      answers = JSON.parse(geminiResponse);
    }
  }
  else {
    throw new Error('Unexpected response format');
  }
} catch (e) {
  console.error('Parse error:', e);
  console.error('Response was:', geminiResponse);
  throw new Error(`Failed to parse Gemini response: ${e.message}`);
}

// Get session ID from the start application response
const sessionId = $('HTTP Request').first().json.session_id;

// Return formatted data for submission
return [{
  json: {
    session_id: sessionId,
    answers: answers,
    continue_to_next: true
  }
}];
```

---

### 5. HTTP Request - Submit Application
**Purpose:** Submit the AI-generated answers

**Configuration:**
```
Node Type: HTTP Request
Method: POST
URL: http://localhost:8000/submit-application
Headers:
  Content-Type: application/json
Body (JSON): {{ $json }}
```

**Output Example:**
```json
{
  "session_id": "abc-123-def",
  "status": "waiting_for_input",  // or "completed"
  "current_step": {
    "step_number": 2,
    "fields": [...]
  }
}
```

---

### 6. IF Node - Check Status
**Purpose:** Determine if there are more steps or application is complete

**Configuration:**
```
Node Type: IF
Conditions:
  - {{ $json.status }} equals "waiting_for_input"

If TRUE: Connect back to Gemini Node (step 3) - more steps to process
If FALSE: Go to success notification
```

---

### 7. Success Notification (Optional)
**Purpose:** Send notification when application completes

**Options:**

**Slack:**
```
Message: ✅ Successfully applied to {{ $('Submit Application').item.json.job_title }} at {{ $('Submit Application').item.json.company_name }}
```

**Email:**
```
To: your-email@example.com
Subject: LinkedIn Application Successful
Body: 
Applied to: {{ $json.job_title }}
Company: {{ $json.company_name }}
Status: {{ $json.status }}
Session: {{ $json.session_id }}
```

**Webhook:**
```
POST to your tracking system with application results
```

---

## Complete Workflow JSON

```json
{
  "name": "LinkedIn Auto Apply with Gemini",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "linkedin-apply",
        "responseMode": "responseNode"
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [240, 300],
      "webhookId": "linkedin-apply"
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
      "position": [460, 300]
    },
    {
      "parameters": {
        "model": "gemini-1.5-pro",
        "options": {
          "temperature": 0.3
        },
        "text": "=You are filling a LinkedIn job application.\n\nJob: {{ $json.job_title }} at {{ $json.company_name }}\n\nForm fields to complete:\n{{ JSON.stringify($json.current_step.fields, null, 2) }}\n\nProvide professional answers. Return ONLY a JSON array:\n[{\"field_id\": \"...\", \"value\": \"...\"}]\n\nGuidelines:\n- Phone: +1234567890\n- Experience: \"3-5 years\"\n- Yes/No: \"Yes\" or \"No\"\n- Files: \"resume\" or \"cover_letter\""
      },
      "name": "Gemini Answer Questions",
      "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
      "position": [680, 300],
      "credentials": {
        "googleGeminiOAuth2Api": {
          "id": "1",
          "name": "Google Gemini account"
        }
      }
    },
    {
      "parameters": {
        "jsCode": "const response = $input.first().json.response || $input.first().json.text;\n\nlet answers;\ntry {\n  const match = response.match(/\\[[\\s\\S]*\\]/);\n  answers = JSON.parse(match ? match[0] : response);\n} catch (e) {\n  throw new Error('Failed to parse: ' + response);\n}\n\nreturn [{\n  json: {\n    session_id: $('Start Application').first().json.session_id,\n    answers: answers,\n    continue_to_next: true\n  }\n}];"
      },
      "name": "Parse Response",
      "type": "n8n-nodes-base.code",
      "position": [900, 300]
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
      "position": [1120, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.status }}",
              "operation": "equals",
              "value2": "waiting_for_input"
            }
          ]
        }
      },
      "name": "More Steps?",
      "type": "n8n-nodes-base.if",
      "position": [1340, 300]
    },
    {
      "parameters": {
        "content": "=✅ **Application Complete!**\n\n**Job:** {{ $json.job_title }}\n**Company:** {{ $json.company_name }}\n**Status:** {{ $json.status }}\n**Session:** {{ $json.session_id }}",
        "height": 464,
        "width": 404
      },
      "name": "Success Note",
      "type": "n8n-nodes-base.stickyNote",
      "position": [1540, 180]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Start Application", "type": "main", "index": 0}]]
    },
    "Start Application": {
      "main": [[{"node": "Gemini Answer Questions", "type": "main", "index": 0}]]
    },
    "Gemini Answer Questions": {
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
        [{"node": "Gemini Answer Questions", "type": "main", "index": 0}],
        []
      ]
    }
  },
  "pinData": {}
}
```

## Testing the Workflow

### 1. Manual Test
1. Save the workflow
2. Click "Execute Workflow"
3. Enter a LinkedIn job URL
4. Watch it process each step

### 2. Webhook Test
```powershell
curl -X POST http://localhost:5678/webhook/linkedin-apply -H "Content-Type: application/json" -d "{\"job_url\": \"https://www.linkedin.com/jobs/view/4308463479/\"}"
```

### 3. Batch Processing
Create a loop to process multiple URLs:

```javascript
// In a Code node before the workflow
const jobUrls = [
  "https://www.linkedin.com/jobs/view/123/",
  "https://www.linkedin.com/jobs/view/456/",
  // ... more URLs
];

return jobUrls.map(url => ({
  json: { job_url: url }
}));
```

## Monitoring

### Check Application Status
```powershell
curl http://localhost:8000/sessions
```

### Cancel a Session
```powershell
curl -X DELETE http://localhost:8000/session/{session_id}
```

### View Execution History
- Go to n8n > Executions tab
- Filter by workflow name
- View detailed logs for each run

## Tips

1. **Rate Limiting**: Add a "Wait" node between iterations (5-10 seconds)
2. **Error Handling**: Add error workflow to handle failures
3. **Logging**: Use "Set" nodes to log intermediate data
4. **Testing**: Test with 1-2 jobs before running batch of 800+
5. **Monitoring**: Keep an eye on screenshots folder

## Troubleshooting

**Gemini returns text instead of JSON**
- Improve the prompt to emphasize JSON-only output
- Add more examples in the prompt
- Increase temperature if responses are too rigid

**Session timeout**
- Sessions are active until completed or cancelled
- Check `/sessions` endpoint to see active sessions
- Cancel stale sessions manually

**Fields not mapping correctly**
- Check the Parse Response code node logs
- Verify field IDs match between extraction and submission
- Review screenshots to see what was actually filled

---

## Advanced: Multiple Job Sources

You can trigger this workflow from:
- **Google Sheets**: Read job URLs from a spreadsheet
- **Airtable**: Track applications with status
- **RSS Feed**: Monitor job boards
- **Email**: Forward job links via email
- **Scheduler**: Process saved jobs daily

Example with Google Sheets:
```
Google Sheets → For Each Row → LinkedIn Workflow → Update Status
```

---

That's it! Your n8n workflow is ready to automate hundreds of LinkedIn applications! 🎯
