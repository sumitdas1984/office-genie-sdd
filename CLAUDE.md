# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Install dependencies
uv sync

# Run backend (FastAPI on port 8000)
uv run fastapi dev src/main.py --port 8000

# Run frontend (Streamlit on port 8501)
uv run streamlit run frontend/app.py

# Run tests (when implemented)
uv run pytest
```

## Architecture

### Processing Pipeline

```
Employee Input → FastAPI → Prompt Templating (Jinja2) → LLM API Call → Response Parsing → Routing Logic → Database Write → Acknowledgment Response
```

Every `POST /api/submit` follows this sequence: Pydantic validation → Jinja2 prompt render → OpenAI call → Pydantic parse → routing engine → SQLite write → response.

### Backend Structure (`src/`)

- `api/` — FastAPI routes, Pydantic request/response models, middleware
- `db/` — SQLite connection management and schema initialization
- `services/` — Business logic: `llm_service` (prompt rendering, LLM calls, retry/backoff, fallback), `routing_service` (category/subcategory/urgency → queue), `persistence_service` (SQLite writes), `analytics_service` (aggregation with 60s in-memory cache)
- `templates/` — Jinja2 prompt templates (e.g. `classification_prompt.j2`)

### Frontend Structure (`frontend/`)

- `pages/` — Streamlit pages: `dashboard.py`, `submit.py`, `analytics.py`, `request_detail.py`
- `components.py` — Shared UI (error banners, category badges, status timeline)
- `api_client.py` — Backend HTTP client

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

### Routing Logic

1. Check automation rules for exact subcategory match (e.g. "Password Reset" → `it-automation-password-reset`)
2. Fall back to category direct routing (e.g. "Payroll" → `payroll-team`)
3. If `urgency=high`, append `-escalation` suffix (e.g. `it-escalation`)

### LLM Failure Handling

- Retry with exponential backoff (1s, 2s, 4s), max 3 attempts
- On final failure: return fallback response (`category=Unknown`, `subcategory=needs-review`, `status=pending`) and persist request for manual triage
- HTTP 200 is always returned to employee on submit — never 500 for LLM failures

### Structured Logging

- Every request gets a UUID4 `X-Request-ID` header (generated or extracted from incoming header)
- Logs are JSON lines to stdout with fields: `timestamp`, `level`, `request_id`, `event`, `duration_ms`, `details`
- Key events: `request_received`, `validation_passed`, `llm_call_started`, `llm_call_completed`, `db_write_completed`, `response_sent`

## Classification Categories

| Category | Subcategories |
|----------|---------------|
| **IT** | Hardware, Software, Access/Permissions, Network, Security |
| **HR** | Leave, Benefits, Policies, Employee Records |
| **Payroll** | Payslip, Deductions, Reimbursements, Tax |
| **Admin** | Facilities, Travel, Supplies, Miscellaneous |

## API Endpoints (from `docs/openapi.yaml`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/submit` | Submit request, classify via LLM, route, persist |
| `GET` | `/api/requests/{request_id}` | Get single request |
| `GET` | `/api/requests` | List requests (filter: `category`, limit: 1–100) |
| `PATCH` | `/api/requests/{request_id}/status` | Update workflow status |
| `GET` | `/api/analytics/summary` | Aggregated stats (cached 60s) |

## Constraints

- **Python 3.10+**, **uv** for package management
- Backend: FastAPI + Pydantic + SQLite + Jinja2 + OpenAI GPT
- Frontend: Streamlit + Plotly
- No external Redis or queue — analytics cache is in-memory with 60s TTL
- `OPENAI_API_KEY` must be set in environment (not hardcoded)