# Skills List: OfficeGenie

## Skill Areas
- [Backend](#backend)
- [Frontend](#frontend)
- [LLM Integration](#llm-integration)
- [Analytics](#analytics)
- [Ops](#ops)

---

## Backend

### submit-request

**Purpose:** Accept incoming support requests via POST /api/submit, validate input, classify via LLM, extract structured fields, generate acknowledgment response, and route to the appropriate team queue.

**Commands:**
```bash
cd backend && uvicorn main:app --reload --port 8000
```

**Key Patterns:**
- Pydantic request validation with clear error messages
- Jinja2 prompt templating with few-shot examples
- OpenAI structured output parsing into typed models
- Category-based routing to department queues

**File Structure:**
```
backend/
├── main.py              # FastAPI app entry point, POST /api/submit endpoint
├── models.py            # Pydantic models for request/response validation
├── database.py          # SQLite database operations
├── router.py            # Request routing logic by category
├── llm_service.py       # OpenAI API client and response parsing
└── templates/
    └── classify_request.j2  # Jinja2 prompt template for LLM classification
```

**Important Notes:**
- Set `OPENAI_API_KEY` environment variable before starting
- Database file is `backend/office_genie.db` (SQLite)
- Correlation ID propagated through all log entries
- LLM call includes few-shot examples from the Jinja2 template
- Routing target derived from category: IT→it-team, HR→hr-team, Payroll→payroll-team, Admin→admin-team

**Implementation Details:**
- `POST /api/submit` accepts `{employee_id, employee_name, employee_email, department, message}`
- Returns `{request_id, status, category, subcategory, extracted_fields, suggested_response, routed_to, created_at}`
- Input validation via Pydantic: all fields required except optional future extensions
- LLM call uses OpenAI structured output schema returning JSON with category, subcategory, confidence, extracted_fields, suggested_response, routing_target
- If LLM call fails, return error with fallback message — do not store incomplete request
- Request ID format: `REQ-YYYY-NNNN` (e.g., REQ-2024-0158)
- All requests logged with correlation ID before LLM call and after response

---

### request-status

**Purpose:** Manage request lifecycle with GET (retrieve single), GET /requests (list with filter), and PATCH (update status) endpoints.

**Commands:**
```bash
cd backend && uvicorn main:app --reload --port 8000
```

**Key Patterns:**
- SQLite query with optional category filter and LIMIT
- Status validation against allowed values: acknowledged, in-progress, resolved, closed
- 404 response when request not found

**File Structure:**
```
backend/
├── main.py              # GET /api/requests, GET /api/requests/{request_id}, PATCH /api/requests/{request_id}/status
├── models.py            # StatusUpdate, RequestDetail Pydantic models
└── database.py          # SQLite queries for filtering and updates
```

**Important Notes:**
- Category filter is case-insensitive (IT, HR, Payroll, Admin)
- Default limit for GET /api/requests is 20, max 100
- Results ordered by most recent first (created_at DESC)
- PATCH updates both status and updated_at timestamp
- updated_at is nullable — null means never updated

**Implementation Details:**
- `GET /api/requests?category=IT&limit=20` returns `[{request_id, employee_name, category, subcategory, status, created_at}, ...]`
- `GET /api/requests/{request_id}` returns full RequestDetail object or 404
- `PATCH /api/requests/{request_id}/status` accepts `{status: "resolved"}` returns updated RequestDetail
- Status transitions: acknowledged → in-progress → resolved → closed (enforced in application logic, not DB)
- Invalid status value returns 400 with error detail

---

## Frontend

### dashboard

**Purpose:** Streamlit web application for employees to submit support requests and view their request history and status.

**Commands:**
```bash
cd frontend && streamlit run app.py --port 8501
```

**Key Patterns:**
- Streamlit session state for request history and form state
- requests library to call FastAPI backend on port 8000
- Category color coding for status badges

**File Structure:**
```
frontend/
├── app.py               # Streamlit entry point, main dashboard page
└── pages/               # Streamlit page modules (optional)
```

**Important Notes:**
- Backend must be running on port 8000 before starting frontend
- Employee ID is passed from session (no auth at MVP — trust input)
- Keep request submission text area large and prominent (natural language input, not dropdowns)
- Show extracted fields after submission so user can verify understanding

**Implementation Details:**
- Main page shows: welcome message, KPI cards (total requests, avg response time, resolution rate), submission form, recent requests table
- Submission form: large text area for message, employee info fields, submit button
- After submit: show classification result (category badge, subcategory), extracted fields panel, suggested response
- Recent requests table: columns = date, category, subcategory, status badge, request_id
- Status badges: 🟡 acknowledged, 🔵 in-progress, 🟢 resolved, ⚪ closed
- Error state: red alert with retry option and fallback contact email
- Loading state: typing indicator animation while LLM processes

**UI States:**
| State | Visual Treatment |
|-------|------------------|
| Empty | Welcoming message, sample prompts as suggestions |
| Loading | Typing indicator animation while LLM processes |
| Success | Green checkmark, category badge, extracted fields shown |
| Error | Red alert with retry option and fallback contact info |

---

## LLM Integration

### classification

**Purpose:** OpenAI GPT integration for classifying support requests into categories (IT, HR, Payroll, Admin) and subcategories, extracting structured fields, and generating acknowledgment responses.

**Commands:**
```bash
# Requires OPENAI_API_KEY set in environment
cd backend && OPENAI_API_KEY=sk-... uvicorn main:app --reload --port 8000
```

**Key Patterns:**
- Jinja2 prompt templates with few-shot examples
- OpenAI structured output schema (JSON mode)
- Confidence threshold handling (retry if confidence < 0.7)
- Fallback on API failure

**File Structure:**
```
backend/
├── llm_service.py       # OpenAI API client, prompt rendering, response parsing
└── templates/
    └── classify_request.j2  # Jinja2 template with system prompt and few-shot examples
```

**Important Notes:**
- Set `OPENAI_API_KEY` before starting — will error immediately if missing
- Use `gpt-4o` or `gpt-3.5-turbo` with JSON mode for structured output
- Prompt includes 3-5 few-shot examples showing input message → expected JSON output
- Confidence below 0.7 triggers re-call with explicit instruction to be more confident
- On API failure: log error, return 503 to client, do not store incomplete request

**Implementation Details:**
- System prompt: "You are an AI assistant that classifies employee support requests. Return valid JSON only."
- Few-shot examples in template:
  ```json
  {"input": "I forgot my password", "output": {"category": "IT", "subcategory": "Password Reset", "confidence": 0.95, ...}}
  {"input": "How many leave days do I have?", "output": {"category": "HR", "subcategory": "Leave", "confidence": 0.92, ...}}
  ```
- LLM Output Schema (expected JSON):
  ```json
  {
    "category": "IT|HR|Payroll|Admin",
    "subcategory": "string (specific subcategory)",
    "confidence": 0.0-1.0,
    "extracted_fields": {
      "date_mentioned": "string|null",
      "system_name": "string|null",
      "urgency": "low|medium|high",
      "error_message": "string|null",
      "employee_id": "string|null"
    },
    "suggested_response": "string (acknowledgment message for employee)",
    "routing_target": "string (department queue or automation identifier)"
  }
  ```
- Extracted fields vary by category: IT includes error_message, HR includes date_mentioned for leave requests, Payroll includes month/year
- Routing target: category-name-transformed-to-kebab-case + "-team" (e.g., "payroll-team")

---

## Analytics

### summary

**Purpose:** Aggregated statistics via GET /api/analytics/summary — total requests, breakdown by category, average response time, and top subcategories.

**Commands:**
```bash
cd backend && uvicorn main:app --reload --port 8000
```

**Key Patterns:**
- SQLite aggregation queries (COUNT, AVG, GROUP BY)
- Computed on-the-fly from requests table (no separate analytics store)

**File Structure:**
```
backend/
├── main.py              # GET /api/analytics/summary endpoint
└── database.py          # SQL aggregation queries
```

**Important Notes:**
- avg_response_time_seconds is computed from created_at of requests (time to first status update)
- top_subcategories limited to top 5 by count
- For empty database, return zeros: `{total_requests: 0, by_category: {IT:0, HR:0, Payroll:0, Admin:0}, avg_response_time_seconds: 0, top_subcategories: []}`

**Implementation Details:**
- Response shape:
  ```json
  {
    "total_requests": 1247,
    "by_category": {"IT": 523, "HR": 312, "Payroll": 287, "Admin": 125},
    "avg_response_time_seconds": 4.2,
    "top_subcategories": [
      {"subcategory": "Access/Permissions", "count": 214},
      {"subcategory": "Payslip Access", "count": 187},
      {"subcategory": "Leave", "count": 156},
      {"subcategory": "Password Reset", "count": 134},
      {"subcategory": "Software Install", "count": 98}
    ]
  }
  ```
- avg_response_time = AVG(time between created_at and updated_at) for all requests
- by_category = COUNT GROUP BY category
- top_subcategories = COUNT GROUP BY subcategory ORDER BY count DESC LIMIT 5

---

## Ops

### logging

**Purpose:** Structured JSON logging with correlation IDs for request tracing, health check endpoint, and error handling middleware.

**Commands:**
```bash
cd backend && python -m logging_config && uvicorn main:app --reload --port 8000
```

**Key Patterns:**
- Python logging with JSON formatter (structured output)
- Correlation ID (request_id) propagated through all log entries per request
- Health check endpoint returning service status

**File Structure:**
```
backend/
├── main.py              # GET /health endpoint
├── logging_config.py    # JSON formatter, correlation ID middleware
└── middleware.py         # Request logging middleware
```

**Important Notes:**
- All logs output as single-line JSON for grepability and log aggregator compatibility
- Each request gets a correlation ID (request_id) printed in every log line
- Health endpoint returns: `{status: "ok", version: "1.0.0", timestamp: "ISO8601"}`
- Error responses always JSON: `{detail: "error message"}`
- Request timing logged: `{"event": "request_complete", "request_id": "...", "duration_ms": 142, "status": 200}`

**Implementation Details:**
- Log format: `{"timestamp": "ISO8601", "level": "INFO", "request_id": "REQ-2024-0158", "event": "...", "message": "...", ...extra_fields}`
- Correlation ID stored in `logging.mdc` (mapped diagnostic context) and included in all subsequent log calls
- Middleware logs: request received, LLM call start/end, response sent, errors
- Health check: `GET /health` — no auth required, returns 200 if service is running
- Error handling: all exceptions caught by middleware, logged with stack trace, return 500 with sanitized message (no internal details exposed)

---

## MVP Scope

Minimum features to ship a working first version (Must Have, sorted by priority then effort):

1. **submit-request** — POST /api/submit with validation, LLM classification, routing, storage
2. **request-status** — GET/PATCH endpoints for request lifecycle
3. **classification** — OpenAI integration with Jinja2 templating and structured output
4. **dashboard** — Streamlit UI with submission form and recent requests table
5. **summary** — Analytics aggregation endpoint
6. **logging** — Structured JSON logs with correlation IDs and health check

---

## Nice-to-Have Extensions

Features to add after MVP (Should Have / Nice to Have):

1. **frontend-analytics** — Streamlit charts (bar/pie for category distribution, line for volume over time, KPI cards)
2. **token-tracking** — Log OpenAI token counts per request for cost monitoring
3. **db-backup** — Periodic SQLite backup and restore capability
4. **request-ownership** — Enforce employees can only view their own requests
5. **status-notifications** — Email/Slack notification when request status changes
6. **latency-metrics** — p50/p95/p99 response times in analytics endpoint
7. **error-rate-dashboard** — Count of failed LLM/API calls in analytics