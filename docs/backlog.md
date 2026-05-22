# OfficeGenie — Feature Backlog

Generated from: `docs/product-overview.md`
Scope: Full stack — FastAPI backend + Streamlit frontend + LLM integration

---

## 📋 FEATURE-001: Pydantic Input Validation & Structured Error Handling

### 1. User Story / Objective
- **As a:** FastAPI application
- **I want to:** reject malformed submit requests with precise, actionable error messages
- **So that:** downstream LLM calls receive well-formed data and clients get actionable feedback

### 2. Functional Description
The `POST /api/submit` endpoint validates all incoming fields via Pydantic models before any processing occurs. Validation failures return HTTP 422 with a structured JSON body listing each field error. This applies to all inbound API payloads.

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - `employee_id`: string, 3–20 chars, alphanumeric + hyphens — reject if missing/empty/whitespace-only
  - `employee_name`: string, 2–100 chars — reject if empty or pure whitespace
  - `employee_email`: string, valid email format — reject malformed addresses
  - `department`: string, 2–100 chars — reject if empty
  - `message`: string, 1–5000 chars — reject if empty or exceeds 5000 chars
* **Expected Output/Response:**
  - `Return Payload`: `{ "detail": [ {"loc": ["body","field"], "msg": "field required", "type": "value_error.missing"} ] }`
  - `Expected Schema`: FastAPI validationError JSON structure (RFC 7807 compatible)
* **Error Handling States:**
  - If field missing/empty -> HTTP 422, list all validation errors
  - If field exceeds max length -> HTTP 422 with specific field and limit
  - If email malformed -> HTTP 422 with "value_error.email" type

### 4. Behavioral & Execution Workflow
```text
Inbound Request ───> Pydantic Validation ───> [PASS] ───> Continue to Processing
                              │
                         [FAIL] ───> HTTP 422 with structured error body
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): Valid payload with all required fields returns HTTP 200 (no validation errors raised)
- [ ] AC-2 (Edge Case - Null/Empty): Missing `employee_id` returns 422 with field-level error at `"loc": ["body","employee_id"]`
- [ ] AC-3 (Input Normalization): Message with leading/trailing whitespace is accepted (not stripped before length check)
- [ ] AC-4 (Boundary Constraint): Message with 5001 characters returns 422 with "string_too_long" error type

### 🛠️ Downstream Implementation Tasks
- [ ] Define Pydantic models for SubmitRequest in `api/models.py`
- [ ] Add Error schema for structured 422 responses
- [ ] Wire validation to `POST /api/submit` route handler
- [ ] Add validation tests in `tests/test_validation.py`

---

## 📋 FEATURE-002: LLM Prompt Templating & Structured Output Parsing

### 1. User Story / Objective
- **As a:** FastAPI application
- **I want to:** construct deterministic, few-shot prompts from Jinja2 templates and parse LLM JSON responses into typed Pydantic models
- **So that:** classification and field extraction are reproducible, testable, and provider-agnostic

### 2. Functional Description
The system uses Jinja2 templates to build classification prompts with category definitions, subcategory options, and 2–3 few-shot examples loaded from a templates directory. The LLM returns a strongly-typed JSON response which is parsed via Pydantic model validation. Structured output failures trigger a fallback without crashing the request.

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - `message`: string (1–5000 chars) — the employee raw input
  - `templates/classification_prompt.j2`: Jinja2 template file
  - `OPENAI_API_KEY`: environment variable for API credential
* **Expected Output/Response:**
  - `Return Payload`: `{ "category": "Payroll", "subcategory": "Payslip Access", "confidence": 0.94, "extracted_fields": {...}, "suggested_response": "...", "routing_target": "payroll-team" }`
  - `Expected Schema`: matches LLMResponse Pydantic model
* **Error Handling States:**
  - If LLM returns malformed JSON -> Catch JSONDecodeError, log raw response, return `{ "category": "Unknown", "subcategory": "Unclassified", "confidence": 0.0, ... }` with status "needs-review"
  - If OPENAI_API_KEY missing -> Raise ConfigError, do not attempt API call
  - If LLM returns HTTP 429/503 -> Apply exponential backoff (1s, 2s, 4s), max 3 retries, then return fallback response

### 4. Behavioral & Execution Workflow
```text
Validated SubmitRequest ───> Render Jinja2 Template ───> OpenAI API Call ───> Parse JSON into Pydantic ───> Return LLMResponse
                                  │                         │
                            [Missing Key]              [Rate Limit/Error] ───> Retry with backoff ───> [Fail] ───> Fallback response
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): Payloads with clear "payslip" keywords return `category: "Payroll"` and `subcategory: "Payslip Access"` with confidence > 0.7
- [ ] AC-2 (Edge Case - Null/Empty): Empty/whitespace message returns fallback response with confidence 0.0 and status "needs-review"
- [ ] AC-3 (Input Normalization): Message truncated to 4000 chars before prompt construction if original exceeds 4000
- [ ] AC-4 (Boundary Constraint): If LLM response is missing `routing_target` field, default to "general-support" queue

### 🛠️ Downstream Implementation Tasks
- [ ] Create `templates/classification_prompt.j2` with category definitions and few-shot examples
- [ ] Implement `services/llm_service.py` with `call_llm(message: str) -> LLMResponse`
- [ ] Implement retry logic with exponential backoff in `services/llm_service.py`
- [ ] Add Pydantic model `LLMResponse` in `api/models.py`
- [ ] Write unit tests for prompt rendering and response parsing

---

## 📋 FEATURE-003: Smart Routing Engine

### 1. User Story / Objective
- **As a:** FastAPI application
- **I want to:** map classification results (category + subcategory + urgency) to routing destinations
- **So that:** requests reach the correct department queue, automation trigger, or escalation path

### 2. Functional Description
The routing engine receives classification data (category, subcategory, urgency from LLM extracted_fields) and applies routing rules to determine the target queue or automation. Direct routing maps categories to queues. Automation triggers fire for known solvable issues (e.g., password reset). High-urgency flags escalate to senior staff. The routing target is stored with the request and returned in the response.

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - `category`: string (IT|HR|Payroll|Admin)
  - `subcategory`: string
  - `extracted_fields.urgency`: string (low|medium|high) — defaults to "medium" if null
* **Expected Output/Response:**
  - `Return Payload`: routing target string, e.g. `"payroll-team"`, `"it-automation-password-reset"`, `"hr-escalation"`
  - `Expected Schema`: single string field `routing_target`
* **Error Handling States:**
  - If category is "Unknown" or null -> Route to "general-support" queue
  - If subcategory maps to no automation rule -> Use category-based direct routing
  - If urgency is "high" -> Append "-escalation" suffix to routing target

### 4. Behavioral & Execution Workflow
```text
LLM Classification ───> Extract category + subcategory + urgency ───> Check Automation Rules ───> [Match] ───> Automation trigger ID
                                                                                │
                                                                        [No Match] ───> Category Direct Routing ───> Department queue
                                                                                │
                                                                        [Urgency=high] ───> Append "-escalation"
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): category="Payroll" with any subcategory routes to "payroll-team"
- [ ] AC-2 (Edge Case - Null/Empty): missing urgency field defaults to "medium" and does NOT trigger escalation
- [ ] AC-3 (Input Normalization): subcategory "Password Reset" (case-insensitive) maps to automation "it-automation-password-reset"
- [ ] AC-4 (Boundary Constraint): urgency="high" + IT category produces routing target "it-escalation"

### 🛠️ Downstream Implementation Tasks
- [ ] Define routing rules config (YAML or JSON) with category-to-queue mappings and automation triggers
- [ ] Implement `services/routing_service.py` with `determine_routing(category, subcategory, urgency) -> str`
- [ ] Add escalation suffix logic for high-urgency requests
- [ ] Write unit tests for routing logic with all category/subcategory/urgency combinations

---

## 📋 FEATURE-004: Request Logging & SQLite Persistence

### 1. User Story / Objective
- **As a:** FastAPI application
- **I want to:** persist every submitted request to SQLite with full metadata including classification, extracted fields, and routing target
- **So that:** request history is queryable and audit-trails are maintained

### 2. Functional Description
On successful LLM classification and routing, the system generates a unique `request_id` (format: `REQ-YYYY-NNNN`), writes the full request record to SQLite, and returns the `request_id` in the response. The `requests` table stores all fields as defined in the database schema. Writes are synchronous; failures abort the request with HTTP 500.

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - `request_id`: auto-generated string (not client-provided)
  - `employee_id`, `employee_name`, `department`, `message`: from validated submit request
  - `category`, `subcategory`, `extracted_fields`, `routing_target`: from LLM response
  - `status`: defaults to "acknowledged"
  - `created_at`: defaults to `CURRENT_TIMESTAMP`
* **Expected Output/Response:**
  - `Return Payload`: Full RequestDetail record persisted to SQLite
  - `Expected Schema`: matches `requests` table schema
* **Error Handling States:**
  - If SQLite write fails (disk full, locked) -> Return HTTP 500 with `{ "detail": "Failed to persist request" }`, log full exception
  - If request_id collision (extremely unlikely) -> Regenerate with nanoseconds appended

### 4. Behavioral & Execution Workflow
```text
LLM Response + Routing ───> Generate request_id ───> SQLite INSERT ───> [Success] ───> Return SubmitResponse with request_id
                                                    │
                                              [Failure] ───> HTTP 500, do not return SubmitResponse
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): Submit request returns `request_id` matching pattern `REQ-2024-\d{4}` and record exists in SQLite
- [ ] AC-2 (Edge Case - Null/Empty): Submit with `department=null` stores `"department": null` in SQLite (not empty string)
- [ ] AC-3 (Input Normalization): `extracted_fields` dict is serialized as JSON string in SQLite TEXT column
- [ ] AC-4 (Boundary Constraint): Message with special chars (quotes, backslashes) is stored correctly and retrievable via GET /api/requests/{request_id}

### 🛠️ Downstream Implementation Tasks
- [ ] Implement `db/init_db.py` with SQLite schema creation and connection management
- [ ] Implement `services/persistence_service.py` with `save_request(request_detail) -> str`
- [ ] Add `created_at` and `updated_at` timestamp management via triggers or Python-side
- [ ] Write integration test that submits request and verifies row exists in SQLite

---

## 📋 FEATURE-005: Request Retrieval & List Filtering

### 1. User Story / Objective
- **As a:** FastAPI application
- **I want to:** expose GET endpoints to retrieve individual requests by ID and list requests with optional category filter and pagination
- **So that:** the frontend and external consumers can query request state

### 2. Functional Description
`GET /api/requests/{request_id}` returns the full request record or 404 if not found. `GET /api/requests` returns a list of requests ordered by `created_at DESC`, with optional `category` filter and `limit` (default 20, max 100). `PATCH /api/requests/{request_id}/status` allows updating the workflow status (acknowledged → in-progress → resolved → closed).

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - `request_id`: string, must match `REQ-\d{4}-\d{4}` pattern for path param
  - `category`: string enum (IT|HR|Payroll|Admin) for query filter
  - `limit`: integer 1–100, default 20
* **Expected Output/Response:**
  - `Return Payload`: RequestDetail object or array of RequestDetail objects
  - `Expected Schema`: matches OpenAPI `RequestDetail` schema
* **Error Handling States:**
  - If request_id not found -> HTTP 404 with `{ "detail": "Request 'REQ-XXXX' not found" }`
  - If invalid category filter -> HTTP 400 with validation error
  - If limit > 100 -> Cap at 100 (do not error)

### 4. Behavioral & Execution Workflow
```text
GET /api/requests/{request_id} ───> SQLite SELECT ───> [Found] ───> Return RequestDetail JSON
                                                    │
                                              [Not Found] ───> HTTP 404

GET /api/requests ───> SQLite SELECT with WHERE ───> Return JSON array
PATCH /api/requests/{request_id}/status ───> SQLite UPDATE ───> Return updated RequestDetail
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): GET /api/requests/REQ-2024-0158 returns full RequestDetail with all fields
- [ ] AC-2 (Edge Case - Null/Empty): GET /api/requests with no records returns `[]` (empty array, not null)
- [ ] AC-3 (Input Normalization): GET /api/requests?category=payroll (lowercase) is accepted and returns IT,HR,Payroll,Admin matches (case-insensitive)
- [ ] AC-4 (Boundary Constraint): GET /api/requests?limit=200 returns max 100 records (capped, no error)

### 🛠️ Downstream Implementation Tasks
- [ ] Implement `api/routes.py` with GET /api/requests/{request_id}, GET /api/requests, PATCH /api/requests/{request_id}/status
- [ ] Add SQLite query helpers in `services/query_service.py`
- [ ] Add `updated_at` auto-set on status PATCH
- [ ] Write tests for 404 case, filter cases, and pagination boundary

---

## 📋 FEATURE-006: Analytics Aggregation & Summary Endpoint

### 1. User Story / Objective
- **As a:** FastAPI application
- **I want to:** compute aggregate statistics from the requests table and return them via GET /api/analytics/summary
- **So that:** dashboard users can see volume trends, category distribution, and team workload

### 2. Functional Description
The analytics endpoint aggregates all stored requests to compute: total request count, breakdown by category, average response time (time from `created_at` to `updated_at` where status = resolved), and top 10 subcategories by frequency. Results are cached in-memory for 60 seconds to avoid repeated full-table scans.

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - `GET /api/analytics/summary`: no parameters
* **Expected Output/Response:**
  - `Return Payload`: `{ "total_requests": 1247, "by_category": {"IT":523,...}, "avg_response_time_seconds": 4.2, "top_subcategories": [...] }`
  - `Expected Schema`: matches OpenAPI `AnalyticsSummary` schema
* **Error Handling States:**
  - If no requests in database -> Return `{ "total_requests": 0, "by_category": {}, "avg_response_time_seconds": null, "top_subcategories": [] }`
  - If cache miss and DB query fails -> Return HTTP 500 with error detail

### 4. Behavioral & Execution Workflow
```text
GET /api/analytics/summary ───> Check Cache ───> [Hit] ───> Return cached result
                                                │
                                          [Miss] ───> SQLite aggregation query ───> Store in cache (60s TTL) ───> Return result
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): With 100 requests across categories, response includes all 4 categories in `by_category` with counts summing to 100
- [ ] AC-2 (Edge Case - Null/Empty): With zero requests, `total_requests` is 0, `by_category` is empty dict `{}`, `avg_response_time_seconds` is null
- [ ] AC-3 (Input Normalization): `top_subcategories` sorted descending by count, limited to 10 entries
- [ ] AC-4 (Boundary Constraint): `avg_response_time_seconds` calculated only from resolved requests; unresolved requests excluded from average

### 🛠️ Downstream Implementation Tasks
- [ ] Implement `services/analytics_service.py` with `get_analytics_summary() -> AnalyticsSummary`
- [ ] Implement in-memory cache with 60-second TTL
- [ ] Add SQLite aggregation queries (COUNT, GROUP BY, AVG with WHERE status=resolved)
- [ ] Write tests for empty DB, single category, and multi-category aggregations

---

## 📋 FEATURE-007: Structured JSON Logging & Request Tracing

### 1. User Story / Objective
- **As a:** FastAPI application
- **I want to:** emit structured JSON logs for every request lifecycle event with correlation IDs
- **So that:** production debugging and observability are possible

### 2. Functional Description
Every inbound HTTP request receives a unique `X-Request-ID` header (UUID4). Logs are emitted at key lifecycle points: request received, validation passed/failed, LLM call started/completed/failed, database write completed, response sent. All log entries are JSON with fields: `timestamp`, `level`, `request_id`, `event`, `duration_ms`, `details`. Logs go to stdout (for container log aggregation) and optionally to a log file.

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - Every inbound HTTP request to any endpoint
  - LLM API call start/completion/error
  - SQLite write start/completion/error
* **Expected Output/Response:**
  - `Return Payload`: Log lines to stdout/stderr as JSON lines
  - `Expected Schema`: `{ "timestamp": "2024-06-15T10:32:00Z", "level": "INFO", "request_id": "uuid", "event": "llm_call_completed", "duration_ms": 1243 }`
* **Error Handling States:**
  - If logging fails (disk full) -> Do not block request processing, emit warning to stderr
  - If request_id header already present -> Use existing value instead of generating new one

### 4. Behavioral & Execution Workflow
```text
Inbound Request ───> Generate/Extract request_id ───> Log "request_received" ───> Process ───> Log "response_sent" ───> Emit JSON log line
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): Every API response includes `X-Request-ID` header with UUID4 value
- [ ] AC-2 (Edge Case - Null/Empty): LLM call failure logs include error message and full request context
- [ ] AC-3 (Input Normalization): Duration `duration_ms` is calculated as elapsed milliseconds from request receipt to response sent
- [ ] AC-4 (Boundary Constraint): Log output is valid JSON lines (one JSON object per line, no surrounding array brackets)

### 🛠️ Downstream Implementation Tasks
- [ ] Configure Python `logging` module with JSON formatter in `config.py`
- [ ] Add request_id middleware in `api/middleware.py`
- [ ] Add logging calls at all lifecycle points in route handlers and service layers
- [ ] Verify log output is valid JSON using `python -c "import json; ..."` pipeline

---

## 📋 FEATURE-008: Streamlit Dashboard & Navigation

### 1. User Story / Objective
- **As a:** Employee
- **I want to:** access a web-based dashboard with sidebar navigation, quick stats, and a request submission form
- **So that:** I can submit support requests and view my recent requests without navigating away from the home page

### 2. Functional Description
The Streamlit frontend has a sidebar with navigation links: Home/Dashboard, Submit Request, Analytics. The main dashboard shows welcome message, 3 KPI cards (Total Requests, Avg Response Time, Resolution Rate), category quick-link cards, and a table of recent requests with status badges. All pages share session state for authenticated employee context.

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - User navigates to the app root URL
  - Streamlit session is initialized with `employee_id` and `employee_name` from session state
* **Expected Output/Response:**
  - `Return Payload`: Streamlit rendered page with sidebar navigation and KPI cards
  - `Expected Schema`: Streamlit widget tree (no JSON contract — UI rendering)
* **Error Handling States:**
  - If API is unreachable -> Show error banner "Unable to connect to backend" with retry button
  - If employee session expired -> Clear session state and show login redirect message

### 4. Behavioral & Execution Workflow
```text
Page Load ───> Streamlit Session Init ───> Fetch /api/analytics/summary ───> Render KPI Cards + Recent Requests Table
                                              │
                                        [API Error] ───> Render Error Banner
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): Dashboard page loads within 3 seconds and shows 3 KPI cards (Total, Avg Time, Resolution Rate)
- [ ] AC-2 (Edge Case - Null/Empty): When no requests exist, dashboard shows "No requests yet" message in the recent requests table
- [ ] AC-3 (Input Normalization): KPI cards format `avg_response_time_seconds` as "4.2s" (one decimal)
- [ ] AC-4 (Boundary Constraint): Sidebar navigation highlights the current active page

### 🛠️ Downstream Implementation Tasks
- [ ] Create `frontend/pages/dashboard.py` with sidebar navigation and KPI cards
- [ ] Implement API client module `frontend/api_client.py` with `get_analytics_summary()` and `get_recent_requests(limit)`
- [ ] Add error handling with retry button in `frontend/components.py`
- [ ] Write Playwright E2E test for dashboard load and KPI display

---

## 📋 FEATURE-009: Natural Language Request Submission & Instant Feedback

### 1. User Story / Objective
- **As a:** Employee
- **I want to:** type a free-form natural language message describing my issue and receive instant classification feedback
- **So that:** I know my request was understood and correctly routed

### 2. Functional Description
The submit page presents a single large text area for the employee's message, an optional file attachment placeholder (not implemented in MVP), and a submit button. On submission, the frontend calls `POST /api/submit`, then displays the returned category badge, extracted fields panel, and AI-generated acknowledgment response. A success state shows a green checkmark and next steps.

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - User types message (1–5000 chars) and clicks Submit
  - Frontend calls `POST /api/submit` with pre-filled `employee_id`, `employee_name`, `employee_email`, `department` from session state
* **Expected Output/Response:**
  - `Return Payload`: SubmitResponse with `request_id`, `status`, `category`, `subcategory`, `extracted_fields`, `suggested_response`, `routed_to`
  - `Expected Schema`: matches OpenAPI `SubmitResponse` schema
* **Error Handling States:**
  - If API returns 422 -> Display inline validation errors under each field
  - If API returns 500 -> Show error alert "Submission failed. Please try again or contact support."
  - If LLM fallback triggered -> Still show success with "needs-review" status indicator

### 4. Behavioral & Execution Workflow
```text
User Types Message ───> Click Submit ───> API POST /api/submit ───> [Success] ───> Show Category Badge + Extracted Fields + Response
                                                                              │
                                                                    [Validation Error] ───> Show inline field errors
                                                                    [Server Error] ───> Show error alert with retry

```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): Submitting "I can't access my payslip for June" returns category="Payroll", subcategory contains "Payslip"
- [ ] AC-2 (Edge Case - Null/Empty): Submitting empty message shows "Message is required" inline error before API call
- [ ] AC-3 (Input Normalization): Message with 4500 chars is accepted and submitted successfully
- [ ] AC-4 (Boundary Constraint): Message with 5001 chars shows "Message cannot exceed 5000 characters" error

### 🛠️ Downstream Implementation Tasks
- [ ] Create `frontend/pages/submit.py` with text area, submit button, and result display
- [ ] Implement `frontend/api_client.py` `submit_request(message)` method
- [ ] Add client-side validation for empty message and character limit before API call
- [ ] Add success state component with category badge, extracted fields, and response text
- [ ] Write E2E test for successful submission and validation error display

---

## 📋 FEATURE-010: Request Detail View & Status Timeline

### 1. User Story / Objective
- **As a:** Employee or support agent
- **I want to:** view the full details of a submitted request including classification, extracted fields, status timeline, and AI-generated response
- **So that:** I can verify the system's understanding and track resolution progress

### 2. Functional Description
The request detail page displays: request header (ID, employee name, submitted timestamp), category and subcategory badges (color-coded), extracted fields in a formatted key-value panel, status timeline (step indicator: Acknowledged → In Progress → Resolved → Closed), and the AI-generated acknowledgment response with a copy button.

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - User clicks a request from the recent requests table or navigates to `/request/{request_id}`
* **Expected Output/Response:**
  - `Return Payload`: RequestDetail object from `GET /api/requests/{request_id}`
  - `Expected Schema`: matches OpenAPI `RequestDetail` schema
* **Error Handling States:**
  - If request not found (404) -> Show "Request not found" page with link back to dashboard
  - If API error -> Show "Unable to load request details" with retry button

### 4. Behavioral & Execution Workflow
```text
Navigate to /request/{request_id} ───> API GET /api/requests/{request_id} ───> [Success] ───> Render Detail Page
                                                                          │
                                                                    [404] ───> Render "Not Found" page
                                                                    [Error] ───> Render Error with Retry
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): Request detail page shows all fields from RequestDetail schema with correct types
- [ ] AC-2 (Edge Case - Null/Empty): If `extracted_fields` is empty/null object, show "No additional details extracted" message
- [ ] AC-3 (Input Normalization): Status timeline highlights the current status step and greys out completed steps
- [ ] AC-4 (Boundary Constraint): Category badge uses correct color: IT=blue, HR=green, Payroll=orange, Admin=purple

### 🛠️ Downstream Implementation Tasks
- [ ] Create `frontend/pages/request_detail.py` with all display sections
- [ ] Implement status timeline component in `frontend/components.py`
- [ ] Add category badge color mapping
- [ ] Add copy-to-clipboard button for suggested_response
- [ ] Write E2E test for request detail page load and 404 handling

---

## 📋 FEATURE-011: Analytics Dashboard & Data Visualization

### 1. User Story / Objective
- **As a:** Support manager or team lead
- **I want to:** view charts and tables showing request volume trends, category distribution, top subcategories, and team workload
- **So that:** I can identify bottlenecks, balance workload, and make data-driven decisions

### 2. Functional Description
The analytics page fetches data from `GET /api/analytics/summary` and renders: KPI cards (total, avg response time, resolution rate), bar chart of requests by category (using Plotly), line chart of daily request volume over the past 30 days, table of top 10 subcategories with counts, and requests-per-team workload summary.

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - User navigates to Analytics page
* **Expected Output/Response:**
  - `Return Payload`: Rendered Streamlit charts and tables
  - `Expected Schema`: UI rendering from `AnalyticsSummary` API response
* **Error Handling States:**
  - If API fails -> Show "Analytics data unavailable" with retry option
  - If `top_subcategories` is empty -> Show "No data available yet" instead of empty chart

### 4. Behavioral & Execution Workflow
```text
Analytics Page Load ───> Fetch GET /api/analytics/summary ───> [Success] ───> Render Charts + Tables
                                                            │
                                                      [Error] ───> Render Error State
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): Bar chart shows 4 bars for IT, HR, Payroll, Admin with heights proportional to counts
- [ ] AC-2 (Edge Case - Null/Empty): When `avg_response_time_seconds` is null, card shows "—" instead of "null"
- [ ] AC-3 (Input Normalization): Table is sorted by count descending (highest subcategory first)
- [ ] AC-4 (Boundary Constraint): Charts gracefully handle 0 requests (empty state message, no crash)

### 🛠️ Downstream Implementation Tasks
- [ ] Create `frontend/pages/analytics.py` with Plotly charts and Streamlit tables
- [ ] Implement `get_analytics_summary()` in `frontend/api_client.py`
- [ ] Add empty state handling for charts
- [ ] Write E2E test for analytics page load and chart rendering

---

## 📋 FEATURE-012: Graceful Degradation & LLM Failure Fallback

### 1. User Story / Objective
- **As a:** FastAPI application
- **I want to:** continue serving requests even when the LLM API is unavailable or returns errors
- **So that:** employees receive acknowledgment that their request was received, even if classification is delayed

### 2. Functional Description
When LLM calls fail (timeout, rate limit, API error), the system: (1) logs the failure with full context, (2) returns a fallback SubmitResponse with `category: "Unknown"`, `subcategory: "needs-review"`, `status: "pending"`, and a generic acknowledgment message, (3) persists the request to DB so it can be manually triaged later. The fallback does NOT block the employee from receiving a response.

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - LLM API returns HTTP 429, 500, 503
  - LLM API times out (configurable timeout, default 30s)
  - LLM returns non-JSON response after 3 parsing retries
* **Expected Output/Response:**
  - `Return Payload`: SubmitResponse with `status: "pending"`, `category: "Unknown"`, `subcategory: "needs-review"`, `suggested_response: "We have received your request and will process it shortly."`
  - `Expected Schema`: valid SubmitResponse shape with fallback values
* **Error Handling States:**
  - If LLM fails -> Fallback response generated, request persisted, HTTP 200 returned (not 500)
  - If database write fails after LLM failure -> HTTP 500 returned (cannot acknowledge without persistence)

### 4. Behavioral & Execution Workflow
```text
Submit Request ───> Prompt + LLM Call ───> [LLM Success] ───> Normal response
                                          │
                                    [LLM Failure] ───> Log error + generate fallback response ───> Persist with status=pending ───> Return HTTP 200
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): When LLM is healthy, normal classification occurs (not fallback)
- [ ] AC-2 (Edge Case - Null/Empty): Fallback response always has `confidence: 0.0` and `category: "Unknown"`
- [ ] AC-3 (Input Normalization): Fallback `suggested_response` still includes employee name from the request
- [ ] AC-4 (Boundary Constraint): After 3 LLM retries with backoff, fallback is triggered — total time does not exceed 45 seconds per request

### 🛠️ Downstream Implementation Tasks
- [ ] Implement fallback response generation in `services/llm_service.py`
- [ ] Add retry logic with exponential backoff (1s, 2s, 4s) in LLM service
- [ ] Ensure fallback still persists request to DB with `status: "pending"`
- [ ] Write integration test that simulates LLM failure and verifies fallback response shape

---

## 📋 FEATURE-013: Status Update Workflow & Request Lifecycle

### 1. User Story / Objective
- **As a:** Support agent
- **I want to:** update the workflow status of a request as I work through it
- **So that:** employees and managers can track resolution progress

### 2. Functional Description
Support agents can update a request's status via `PATCH /api/requests/{request_id}/status`. Valid transitions: `acknowledged → in-progress → resolved → closed`. Status updates also set the `updated_at` timestamp. Attempting invalid transitions (e.g., `closed → in-progress`) returns HTTP 400.

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - `request_id`: must exist in database
  - `status`: one of ["acknowledged", "in-progress", "resolved", "closed"]
* **Expected Output/Response:**
  - `Return Payload`: Updated RequestDetail with new status and updated `updated_at`
  - `Expected Schema`: matches OpenAPI `RequestDetail` schema
* **Error Handling States:**
  - If request_id not found -> HTTP 404
  - If status not in enum -> HTTP 400 with `"detail": "Invalid status value"`
  - If transition not allowed (e.g., resolved → acknowledged) -> HTTP 400 with specific error message

### 4. Behavioral & Execution Workflow
```text
PATCH /api/requests/{request_id}/status ───> Validate status enum ───> Check transition validity ───> [Valid] ───> SQLite UPDATE ───> Return updated record
                                                                                          │
                                                                                    [Invalid Transition] ───> HTTP 400
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): PATCH with `status: "resolved"` on an acknowledged request returns 200 with `"status": "resolved"` and `updated_at` set
- [ ] AC-2 (Edge Case - Null/Empty): PATCH with missing `status` field returns 422 validation error
- [ ] AC-3 (Input Normalization): PATCH with `status: " IN-PROGRESS "` (whitespace) normalizes to `"in-progress"` (accepted)
- [ ] AC-4 (Boundary Constraint): PATCH with `status: "closed"` on an already-closed request returns 400 "Transition not allowed"

### 🛠️ Downstream Implementation Tasks
- [ ] Implement `PATCH /api/requests/{request_id}/status` in `api/routes.py`
- [ ] Add transition validation in `services/status_service.py`
- [ ] Add `updated_at` auto-set on every status update
- [ ] Write tests for all valid transitions and invalid transition rejections

---

## 📋 FEATURE-014: Frontend State Management & Loading Indicators

### 1. User Story / Objective
- **As a:** Employee using the Streamlit frontend
- **I want to:** see clear loading states while requests are being processed
- **So that:** I know the system is working and haven't accidentally double-submitted

### 2. Functional Description
The frontend uses Streamlit session state to manage: current page, employee context (name, email, department), submission in-progress flag, and last submission result. During API calls, a spinner with "Processing your request..." message is shown. Double-submit is prevented by disabling the submit button while a request is in-flight.

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - User clicks Submit button
  - API call is in-flight
* **Expected Output/Response:**
  - `Return Payload`: UI state change (button disabled, spinner visible)
  - `Expected Schema`: Streamlit widget state changes (not JSON contract)
* **Error Handling States:**
  - If API call completes -> Hide spinner, show result or error
  - If API call fails -> Hide spinner, show error alert, re-enable submit button

### 4. Behavioral & Execution Workflow
```text
Click Submit ───> Disable Button + Show Spinner ───> API POST /api/submit ───> [Success] ───> Show Result + Enable Button
                                                                              │
                                                                    [Error] ───> Show Error Alert + Enable Button
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): Submit button is disabled during API call and re-enabled after response received
- [ ] AC-2 (Edge Case - Null/Empty): After failed submission, submit button is re-enabled allowing retry
- [ ] AC-3 (Input Normalization): Session state `last_submission_result` is cleared when user navigates away from submit page
- [ ] AC-4 (Boundary Constraint): Spinner timeout — if API takes >60s, show "This is taking longer than expected" message

### 🛠️ Downstream Implementation Tasks
- [ ] Implement session state management in `frontend/pages/submit.py`
- [ ] Add spinner and disable logic using Streamlit's `st.spinner()` context manager
- [ ] Implement 60-second timeout warning for long-running submissions
- [ ] Write E2E test verifying button disable/enable behavior