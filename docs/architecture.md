# Architecture

System architecture for OfficeGenie — an AI-powered first-line triage system for employee support requests.

---

## Overview

OfficeGenie follows a pipeline architecture where an employee submits a natural language request, which flows through validation → classification → routing → persistence → acknowledgment, with structured logging at every step.

---

## Processing Pipeline

```
Employee Input → FastAPI → Prompt Templating → LLM API Call → Response Parsing → Routing Logic → Database Write → Acknowledgment Response
```

1. **Input Validation** – Pydantic validates incoming request payload
2. **Prompt Templating** – Jinja2 template constructs classification+extraction prompt with few-shot examples
3. **LLM Call** – API call to OpenAI GPT with structured output schema
4. **Response Parsing** – JSON response parsed into Pydantic models
5. **Routing Logic** – Category/subcategory determines routing destination
6. **Database Write** – Request logged to SQLite with full metadata
7. **Response** – Acknowledgment returned to employee

---

## Backend Architecture

### Technology Stack

| Component | Technology |
|-----------|------------|
| Runtime | Python 3.10+ |
| API Framework | FastAPI |
| Validation | Pydantic models |
| Data Storage | SQLite (embedded, file-based) |
| LLM Integration | OpenAI GPT (API) |
| Templating | Jinja2 for prompt templates |
| Logging | Python logging (structured JSON logs) |

### Backend Structure (`src/`)

```
src/
├── api/           — FastAPI routes, Pydantic request/response models, middleware
├── db/            — SQLite connection management and schema initialization
├── services/      — Business logic: llm_service, routing_service, persistence_service, analytics_service
└── templates/      — Jinja2 prompt templates (e.g. classification_prompt.j2)
```

### Key Data Contracts

**LLM Response Schema** (returned by OpenAI, parsed into Pydantic):
```json
{
  "category": "IT|HR|Payroll|Admin",
  "subcategory": "string",
  "confidence": 0.0-1.0,
  "extracted_fields": { "date_mentioned": null, "system_name": null, "urgency": "low|medium|high", "error_message": null },
  "suggested_response": "string",
  "routing_target": "string"
}
```

**Request ID format:** `REQ-YYYY-NNNN` (auto-generated, not client-provided)

**Status workflow:** `acknowledged → in-progress → resolved → closed` (transitions enforced, invalid transitions return HTTP 400)

---

## Frontend Architecture

### Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | Streamlit |
| Language | Python |
| State Management | Streamlit session state |
| HTTP Client | requests library |
| Data Visualization | Streamlit native charts / Plotly |

### Frontend Structure (`frontend/`)

```
frontend/
├── pages/         — Streamlit pages: dashboard.py, submit.py, analytics.py, request_detail.py
├── components.py  — Shared UI (error banners, category badges, status timeline)
└── api_client.py  — Backend HTTP client
```

### Page Structure

1. **Main Dashboard (Home)** – Sidebar nav, KPI cards, recent requests table, category quick links
2. **Submit** – Natural language input form with instant classification feedback
3. **Request Detail** – Full request data, status timeline, extracted fields, copyable response
4. **Analytics** – Charts (bar/pie/line), KPI cards, top subcategories table

### UI/UX Principles

- **Conversational Input** – Large free-form text area for natural language input, not rigid category dropdowns
- **Instant Feedback** – Classification result and extracted fields shown immediately after submission
- **Transparency** – Displays extracted fields so user can verify correct understanding
- **Mobile Responsive** – Streamlit's responsive layout adapts to mobile and desktop

---

## Routing Logic

1. Check automation rules for exact subcategory match (e.g. "Password Reset" → `it-automation-password-reset`)
2. Fall back to category direct routing (e.g. "Payroll" → `payroll-team`)
3. If `urgency=high`, append `-escalation` suffix (e.g. `it-escalation`)

---

## LLM Failure Handling

- Retry with exponential backoff (1s, 2s, 4s), max 3 attempts
- On final failure: return fallback response (`category=Unknown`, `subcategory=needs-review`, `status=pending`) and persist request for manual triage
- HTTP 200 is always returned to employee on submit — never 500 for LLM failures

---

## Structured Logging

- Every request gets a UUID4 `X-Request-ID` header (generated or extracted from incoming header)
- Logs are JSON lines to stdout with fields: `timestamp`, `level`, `request_id`, `event`, `duration_ms`, `details`
- Key events: `request_received`, `validation_passed`, `llm_call_started`, `llm_call_completed`, `db_write_completed`, `response_sent`

---

## Constraints

- **Python 3.10+**, **uv** for package management
- Backend: FastAPI + Pydantic + SQLite + Jinja2 + OpenAI GPT
- Frontend: Streamlit + Plotly
- No external Redis or queue — analytics cache is in-memory with 60s TTL
- `OPENAI_API_KEY` must be set in environment (not hardcoded)