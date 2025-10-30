# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         n8n Workflow                            │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                 │
│  │  Trigger │───▶│  Gemini  │───▶│ HTTP Req │                 │
│  │  (URLs)  │    │    AI    │    │(Submit)  │                 │
│  └──────────┘    └────▲─────┘    └─────┬────┘                 │
│                        │                │                       │
│                        └────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              LinkedIn Automation Service (FastAPI)              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    REST API Endpoints                     │  │
│  │  /start-application  │  /submit-application │  /health   │  │
│  └─────────────┬────────────────────┬───────────────────────┘  │
│                │                    │                           │
│  ┌─────────────▼────────┐  ┌───────▼──────────┐               │
│  │  Browser Manager     │  │   Form Filler    │               │
│  │  - Playwright        │  │  - Fill fields   │               │
│  │  - Session mgmt      │  │  - Click buttons │               │
│  │  - Stealth mode      │  │  - Submit forms  │               │
│  └─────────┬────────────┘  └──────────────────┘               │
│            │                                                    │
│  ┌─────────▼────────────┐                                      │
│  │ Question Extractor   │                                      │
│  │ - Detect fields      │                                      │
│  │ - Extract options    │                                      │
│  │ - Capture metadata   │                                      │
│  └──────────────────────┘                                      │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   │ Playwright Protocol
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Chromium Browser                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    LinkedIn Website                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │  Job Page  │─▶│ Easy Apply │─▶│   Forms    │         │  │
│  │  └────────────┘  └────────────┘  └────────────┘         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                   │
                   │ Persistent Storage
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    File System                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ browser_data │  │ screenshots  │  │  documents   │         │
│  │  (session)   │  │   (images)   │  │   (resume)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────┐
│ Job URLs │ (800-1000 links)
└────┬─────┘
     │
     ▼
┌─────────────────────────────────┐
│ n8n Workflow Loop               │
│ For each URL:                   │
└────┬────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│ Step 1: Start Application                   │
│ POST /start-application                     │
│ Input: {"job_url": "..."}                   │
└────┬────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│ Browser Actions:                            │
│ 1. Navigate to job URL                      │
│ 2. Click "Easy Apply" button                │
│ 3. Wait for modal to load                   │
└────┬────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│ Extract Form Fields:                        │
│ - Text inputs (name, email, etc)            │
│ - Dropdowns (experience, education)         │
│ - Radio buttons (yes/no questions)          │
│ - Checkboxes (agreements)                   │
│ - File uploads (resume, cover letter)       │
│ - Capture screenshot                        │
└────┬────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│ Return JSON Response:                       │
│ {                                           │
│   "session_id": "abc-123",                  │
│   "status": "waiting_for_input",            │
│   "current_step": {                         │
│     "step_number": 1,                       │
│     "fields": [                             │
│       {                                     │
│         "field_id": "phone",                │
│         "field_type": "phone",              │
│         "label": "Phone number",            │
│         "required": true                    │
│       },                                    │
│       ...                                   │
│     ]                                       │
│   }                                         │
│ }                                           │
└────┬────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│ Gemini AI Processing:                       │
│ - Receive field descriptions                │
│ - Analyze question context                  │
│ - Generate professional answers             │
│ - Format as JSON array                      │
└────┬────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│ AI Response:                                │
│ [                                           │
│   {"field_id": "phone",                     │
│    "value": "+1234567890"},                 │
│   {"field_id": "experience",                │
│    "value": "3-5 years"},                   │
│   ...                                       │
│ ]                                           │
└────┬────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│ Step 2: Submit Application                  │
│ POST /submit-application                    │
│ Input: {                                    │
│   "session_id": "abc-123",                  │
│   "answers": [...],                         │
│   "continue_to_next": true                  │
│ }                                           │
└────┬────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│ Form Filling Actions:                       │
│ 1. Locate each field by ID                  │
│ 2. Fill with corresponding value            │
│ 3. Validate input                           │
│ 4. Capture screenshot                       │
└────┬────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│ Check Navigation:                           │
│ - Has "Next" button? → Next step            │
│ - Has "Review" button? → Review page        │
│ - Has "Submit" button? → Submit             │
└────┬────────────────────────────────────────┘
     │
     ├─────────────────────────────────────┐
     │ More steps?                         │ No
     │                                     │
     │ Yes                                 ▼
     │                            ┌──────────────────┐
     │                            │ Submit & Verify  │
     │                            │ - Click Submit   │
     │                            │ - Check success  │
     │                            │ - Close modal    │
     │                            └────┬─────────────┘
     │                                 │
     ▼                                 ▼
┌─────────────────────────┐  ┌──────────────────────┐
│ Extract Next Step       │  │ Return Success       │
│ - New fields            │  │ {                    │
│ - Loop to Gemini        │  │   "status":          │
│ (Repeat process)        │  │     "completed"      │
└─────────────────────────┘  │ }                    │
                             └────┬─────────────────┘
                                  │
                                  ▼
                           ┌──────────────────────┐
                           │ Move to Next Job URL │
                           │ (Repeat from top)    │
                           └──────────────────────┘
```

## Component Interaction

```
┌────────────────────────────────────────────────────────────┐
│                    Application Flow                        │
└────────────────────────────────────────────────────────────┘

main.py (FastAPI)
    │
    ├─── /start-application
    │    │
    │    ├──▶ browser_manager.navigate_to_job()
    │    │    └──▶ Playwright → LinkedIn Job Page
    │    │
    │    ├──▶ browser_manager.click_easy_apply()
    │    │    └──▶ Playwright → Click Button
    │    │
    │    ├──▶ question_extractor.extract_all_fields()
    │    │    ├──▶ extract_text_inputs()
    │    │    ├──▶ extract_select_fields()
    │    │    ├──▶ extract_radio_buttons()
    │    │    ├──▶ extract_checkboxes()
    │    │    └──▶ extract_file_inputs()
    │    │
    │    ├──▶ browser_manager.take_screenshot()
    │    │
    │    └──▶ Return ApplicationResponse
    │
    ├─── /submit-application
    │    │
    │    ├──▶ form_filler.fill_field() (for each answer)
    │    │    ├──▶ _fill_text_input()
    │    │    ├──▶ _fill_select()
    │    │    ├──▶ _fill_radio()
    │    │    ├──▶ _fill_checkbox()
    │    │    └──▶ _upload_file()
    │    │
    │    ├──▶ form_filler.click_next() / click_review()
    │    │
    │    ├──▶ question_extractor.extract_all_fields()
    │    │    (if more steps)
    │    │
    │    └──▶ form_filler.submit_application()
    │         └──▶ form_filler.check_success()
    │
    └─── /sessions, /health, etc.
```

## State Management

```
Session Lifecycle:

┌──────────────┐
│ No Session   │
└──────┬───────┘
       │ POST /start-application
       ▼
┌──────────────────┐
│ Session Created  │
│ Status: started  │
└──────┬───────────┘
       │ Fields extracted
       ▼
┌───────────────────────┐
│ Waiting for Input     │
│ Status: waiting       │
│ Step: 1               │
│ Fields: [...]         │
└──────┬────────────────┘
       │ POST /submit-application
       ▼
┌───────────────────────┐
│ Processing            │
│ Status: in_progress   │
└──────┬────────────────┘
       │
       ├──▶ More steps?
       │    │
       │    Yes
       │    │
       │    ▼
       │  ┌─────────────────────┐
       │  │ Waiting for Input   │
       │  │ Step: 2             │
       │  │ Fields: [...]       │
       │  └─────┬───────────────┘
       │        │
       │        └──▶ Loop back
       │
       No
       │
       ▼
┌───────────────────────┐
│ Completed             │
│ Status: completed     │
│ Session Cleaned Up    │
└───────────────────────┘

OR

       │
       ▼
┌───────────────────────┐
│ Failed                │
│ Status: failed        │
│ Error: [message]      │
└───────────────────────┘
```

## File System Structure

```
browser_automation/
│
├── main.py                    # Entry point, FastAPI app
│   └── Defines endpoints
│       └── Uses BrowserManager, QuestionExtractor, FormFiller
│
├── src/
│   ├── models.py             # Pydantic data models
│   │   ├── FormField
│   │   ├── ApplicationStep
│   │   ├── ApplicationResponse
│   │   └── ...
│   │
│   ├── browser_manager.py    # Browser automation
│   │   ├── initialize() → Start Playwright
│   │   ├── navigate_to_job() → Open URL
│   │   ├── click_easy_apply() → Click button
│   │   ├── take_screenshot() → Capture image
│   │   └── ensure_logged_in() → Check session
│   │
│   ├── question_extractor.py # Field detection
│   │   ├── extract_text_inputs()
│   │   ├── extract_select_fields()
│   │   ├── extract_radio_buttons()
│   │   ├── extract_checkboxes()
│   │   ├── extract_file_inputs()
│   │   └── get_current_step_info()
│   │
│   └── form_filler.py        # Form interaction
│       ├── fill_field() → Dispatch by type
│       ├── _fill_text_input()
│       ├── _fill_select()
│       ├── _fill_radio()
│       ├── _fill_checkbox()
│       ├── _upload_file()
│       ├── click_next()
│       ├── submit_application()
│       └── check_success()
│
├── documents/
│   ├── resume.pdf            # User's resume
│   └── cover_letter.pdf      # User's cover letter
│
├── screenshots/              # Generated at runtime
│   ├── [session-id]_job_page.png
│   ├── [session-id]_step_1.png
│   ├── [session-id]_step_1_filled.png
│   └── ...
│
├── browser_data/             # Playwright persistent context
│   └── [Chrome profile]      # Saves login session
│
└── .env                      # Configuration
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                    Technology Stack                     │
└─────────────────────────────────────────────────────────┘

Backend:
├── Python 3.9+
├── FastAPI (REST API framework)
├── Uvicorn (ASGI server)
├── Pydantic (Data validation)
└── Python-dotenv (Config management)

Browser Automation:
├── Playwright (Browser control)
├── Playwright-stealth (Anti-detection)
└── Chromium (Browser engine)

Data Processing:
├── AsyncIO (Async operations)
├── JSON (Data format)
└── Pillow (Image processing)

Integration:
├── n8n (Workflow automation)
├── Google Gemini (AI processing)
└── HTTP/REST (Communication)

Storage:
├── File system (Screenshots, documents)
├── Browser profile (Session persistence)
└── In-memory (Active sessions)
```

## Security & Privacy

```
┌─────────────────────────────────────────────────────────┐
│                  Security Measures                      │
└─────────────────────────────────────────────────────────┘

Authentication:
├── Manual LinkedIn login (first time)
├── Session persistence (browser_data/)
└── No credentials stored in code

API Security:
├── CORS enabled (configurable)
├── Input validation (Pydantic models)
└── Error sanitization

Privacy:
├── Data stays local (no cloud upload)
├── Screenshots saved locally
├── Session data in memory only
└── .env file for sensitive config

Anti-Detection:
├── Stealth plugin
├── Real browser profile
├── Human-like delays
├── Realistic user agent
└── Non-headless mode option
```

This architecture provides a robust, scalable solution for automating LinkedIn Easy Apply applications! 🚀
