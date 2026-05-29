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

# Run tests
uv run pytest -v
```

## Architecture

### Processing Pipeline

```
Employee Input → FastAPI → Pydantic Validation → LLM Classification (stub) → Routing Logic (stub) → SQLite Persistence (stub) → Acknowledgment Response
```

Current implementation uses stub services. Full LLM classification, routing, and persistence come in FEATURE-002/003/004.

### Backend Structure (`src/`)

- `api/` — FastAPI routes, Pydantic request/response models, exception handlers
- `db/` — SQLite schema and connection management
- `middleware/` — RequestIDMiddleware, JSONLogHandler for structured logging
- `services/` — Business logic: llm_service, routing_service, id_generator, persistence_service, analytics_service
- `templates/` — Jinja2 prompt templates (e.g. `classification_prompt.j2`)

### Frontend Structure (`frontend/`)

- `pages/` — Streamlit pages: dashboard, submit, analytics, request_detail
- `components.py` — Shared UI (category badges, status timeline, error banners)
- `api_client.py` — Backend HTTP client

### Key Data Contracts

**SubmitRequest** (employee-provided):
- `employee_id`, `employee_name`, `employee_email`, `department`, `message`

**SubmitResponse** (returned by POST /api/submit):
- `request_id`, `status`, `category`, `subcategory`, `extracted_fields`, `suggested_response`, `routed_to`, `created_at`

**LLM Response Schema** (from OpenAI, parsed into dict):
```json
{
  "category": "IT|HR|Payroll|Admin|Unknown",
  "subcategory": "string",
  "confidence": 0.0-1.0,
  "extracted_fields": { "date_mentioned": null, "system_name": null, "urgency": "low|medium|high", "error_message": null },
  "suggested_response": "string",
  "routing_target": "string"
}
```

**Request ID format:** `REQ-YYYY-NNNN` (auto-generated, not client-provided)

**Status workflow:** `acknowledged → in-progress → resolved → closed` (transitions enforced; invalid transitions return HTTP 400)

### Classification Categories

| Category | Subcategories |
|----------|---------------|
| **IT** | Hardware, Software, Access/Permissions, Network, Security |
| **HR** | Leave, Benefits, Policies, Employee Records |
| **Payroll** | Payslip, Deductions, Reimbursements, Tax |
| **Admin** | Facilities, Travel, Supplies, Miscellaneous |

### Routing Logic

1. Exact subcategory automation rules (e.g. "Password Reset" → `it-automation-password-reset`)
2. Category direct routing (e.g. "Payroll" → `payroll-team`)
3. `urgency=high` appends `-escalation` suffix

### LLM Failure Handling

- Retry with exponential backoff (1s, 2s, 4s), max 3 attempts
- Auth errors (401) fail immediately without retry
- On final failure: fallback response (`category=Unknown`, `subcategory=needs-review`, `confidence=0.0`) persisted for manual triage
- HTTP 200 always returned to employee — never 500 for LLM failures

### Structured Logging

- Every request gets a UUID4 `X-Request-ID` header (generated or extracted from incoming)
- JSON logs to stdout: `timestamp`, `level`, `request_id`, `event`, `duration_ms`, `details`
- Key events: `request_received`, `validation_passed`, `llm_call_started`, `llm_call_completed`, `db_write_completed`, `response_sent`

## SDD Pipeline

This project uses a Specification-Driven Development pipeline with Claude agents. All work happens on feature branches from `develop`.

### Pipeline Commands

| Command | Agent | What it does |
|---------|-------|--------------|
| `/create-features` | `create-features.md` | Transform product docs into Feature/Epic GitHub issues |
| `/parse-requirement` | `parse-requirement.md` | Classify and parse a GitHub issue |
| `/create-stories` | `create-stories.md` | Decompose a feature into Story sub-issues |
| `/implement-feature` | `implement-feature.md` | Execute TDD cycle for one story |
| `/update-knowledge` | `update-knowledge.md` | Update CLAUDE.md and docs after implementation |
| `/create-pr` | `create-pr.md` | Create PR with summary, checklists, linked issues |
| `/review` | `code-review.md` | Automated code quality review |

### Branching Strategy

```
main            — production (protected)
develop        — integration branch for completed features
feature/FEATURE-00X  — feature branches from develop
```

**Sequence:** Branch from `develop` → implement all stories → update docs → create PR → review → merge to `develop` → sync `develop`

### TDD Cycle (per Story)

```
Write failing test  →  Run (verify FAIL)  →  Write implementation  →  Run (verify PASS)  →  Commit
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/submit` | Submit request, classify, route, return acknowledgment (stub) |
| `GET` | `/api/requests/{request_id}` | Retrieve single request (stub) |
| `GET` | `/api/requests` | List requests (filter by category, limit) (stub) |
| `PATCH` | `/api/requests/{request_id}/status` | Update request status (stub) |
| `GET` | `/api/analytics/summary` | Aggregated statistics (stub) |

## Constraints

- **Python 3.13+**, **uv** for package management
- Backend: FastAPI + Pydantic v2 + SQLite + Jinja2 + OpenAI GPT (stub)
- Frontend: Streamlit + Plotly
- `OPENAI_API_KEY` required in environment (not hardcoded)
- No external Redis or queue — analytics cache is in-memory with 60s TTL
