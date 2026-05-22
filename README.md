# OfficeGenie

AI-powered first-line triage system for employee support requests. Employees submit natural language queries about IT, HR, Payroll, and Admin issues — the system automatically classifies, extracts structured data, generates instant responses, and routes to the appropriate team.

## Quick Start

```bash
uv sync
uv run fastapi dev src/main.py --port 8000
```

## Tech Stack

**Backend:** FastAPI + Pydantic + SQLite + Jinja2 + OpenAI GPT  
**Frontend:** Streamlit  
**Runtime:** Python 3.10+

## Project Structure

```
src/
  api/          # FastAPI routes, models, middleware
  db/           # SQLite schema + connection management
  services/     # Business logic (LLM, routing, analytics, persistence)
  templates/    # Jinja2 prompt templates
frontend/
  pages/        # Streamlit pages (dashboard, submit, analytics, detail)
  components.py # Shared UI components
  api_client.py # Backend API client
docs/
  product-overview.md   # Product specification
  openapi.yaml          # API contract
  backlog.md           # Feature backlog
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/submit` | Submit a support request |
| `GET` | `/api/requests/{id}` | Get request details |
| `GET` | `/api/requests` | List requests (filter by category, limit) |
| `PATCH` | `/api/requests/{id}/status` | Update request status |
| `GET` | `/api/analytics/summary` | Get analytics summary |

## Feature Backlog

See `docs/backlog.md` for the full feature specification.