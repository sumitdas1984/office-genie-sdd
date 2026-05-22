# OfficeGenie – Product Overview

## Overview

OfficeGenie is an AI-powered first-line triage system for employee support requests. It provides a conversational interface where employees submit natural language queries about IT, HR, Payroll, and Admin issues. The system automatically classifies requests, extracts structured information, generates instant responses, and routes issues to the appropriate team or automation.

OfficeGenie reduces response times, eliminates manual triage overhead, and provides employees with immediate acknowledgment that their request has been received and routed.

---

## Core Product Features

### 1. Natural Language Query Submission
Employees submit support requests through a web-based chat or form interface. Unlike traditional ticketing systems that require selecting categories and filling structured fields, OfficeGenie accepts free-form text like:

> "I can't access my payslip for June. It shows 'file not found'. Please help."

### 2. AI-Powered Classification
The system uses a Large Language Model to classify each query into:

| Category | Subcategories |
|----------|---------------|
| **IT** | Hardware, Software, Access/Permissions, Network, Security |
| **HR** | Leave, Benefits, Policies, Employee Records |
| **Payroll** | Payslip, Deductions, Reimbursements, Tax |
| **Admin** | Facilities, Travel, Supplies, Miscellaneous |

### 3. Structured Field Extraction
Beyond classification, the LLM extracts structured details:

- **Dates** – leave dates, request timestamps, payroll periods
- **System names** – applications, servers, tools referenced
- **Urgency indicators** – explicit urgency or SLA-implied priority
- **Employee identifiers** – names, IDs, departments
- **Error messages** – specific error text for IT issues

### 4. Automated Acknowledgment
Instant response is sent to the employee confirming their request has been received and routed:

> "Hi [Name], we've shared your payslip issue with the Payroll team. You'll get an update shortly."

### 5. Smart Routing
Requests are routed to the correct department or automation based on classification:

- **Direct routing** – category-based routing to departmental queues
- **Automation triggers** – common issues handled by automated workflows (e.g., password reset)
- **Escalation rules** – high-urgency or complex issues escalated to senior staff

### 6. Analytics & Logging
All requests are logged for:

- Volume trends by category and department
- Average response and resolution times
- Common issues identification
- Team workload balancing

---

## Backend Specification

### Technology Stack

| Component | Technology |
|-----------|------------|
| Runtime | Python 3.10+ |
| LLM Integration | OpenAI GPT (API) |
| Data Storage | SQLite (embedded, file-based) |
| Data Processing | Python standard library / sqlite3 |
| Templating | Jinja2 for prompt templates |
| Logging | Python logging (structured JSON logs) |
| API Framework | FastAPI |
| Validation | Pydantic models |

### API Endpoints

#### `POST /api/submit`
Submit a new support request.

**Request Body:**
```json
{
  "employee_id": "EMP-0042",
  "employee_name": "Ananya Sharma",
  "employee_email": "ananya.sharma@company.com",
  "department": "Engineering",
  "message": "I can't access my payslip for June. It shows 'file not found'. Please help."
}
```

**Response Body:**
```json
{
  "request_id": "REQ-2024-0158",
  "status": "acknowledged",
  "category": "Payroll",
  "subcategory": "Payslip Access",
  "extracted_fields": {
    "month": "June",
    "year": "2024",
    "error_message": "file not found"
  },
  "suggested_response": "Hi Ananya, we've shared your payslip issue with the Payroll team. You'll get an update shortly.",
  "routed_to": "payroll-team",
  "created_at": "2024-06-15T10:32:00Z"
}
```

#### `GET /api/requests/{request_id}`
Retrieve status and details of a specific request.

#### `GET /api/analytics/summary`
Retrieve aggregated analytics data.

**Response Body:**
```json
{
  "total_requests": 1247,
  "by_category": {
    "IT": 523,
    "HR": 312,
    "Payroll": 287,
    "Admin": 125
  },
  "avg_response_time_seconds": 4.2,
  "top_subcategories": [...]
}
```

### Processing Flow

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

### Structured Output Schema (LLM Response)

The LLM is prompted to return a strongly-typed JSON response:

```json
{
  "category": "string (IT|HR|Payroll|Admin)",
  "subcategory": "string (specific subcategory)",
  "confidence": "float (0.0-1.0)",
  "extracted_fields": {
    "date_mentioned": "string|null",
    "system_name": "string|null",
    "urgency": "low|medium|high",
    "error_message": "string|null",
    "employee_id": "string|null"
  },
  "suggested_response": "string",
  "routing_target": "string (department queue or automation identifier)"
}
```

### Database Schema

```sql
CREATE TABLE requests (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    employee_name TEXT NOT NULL,
    department TEXT,
    message TEXT NOT NULL,
    category TEXT,
    subcategory TEXT,
    extracted_fields TEXT,  -- JSON stored as text
    routing_target TEXT,
    status TEXT DEFAULT 'acknowledged',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## Frontend Specification

### Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | Streamlit |
| Language | Python (for UI logic) |
| Styling | Streamlit built-in + custom CSS |
| State Management | Streamlit session state |
| HTTP Client | requests library |
| Data Visualization | Streamlit native charts / Plotly |
| Deployment | Streamlit Cloud or Docker |

### Page Structure

#### 1. Main Dashboard (Home)
- **Sidebar** – Navigation menu, user info, category filters
- **Main Content Area** – Welcome message, quick stats cards
- **Request Submission Form** – Large text area for natural language input
- **Recent Requests Table** – Sortable table of recent submissions with status badges
- **Category Quick Links** – Cards to filter by IT, HR, Payroll, Admin

#### 2. Request Detail View
- **Request Header** – Request ID, employee name, submitted timestamp
- **Category & Subcategory Badge** – Color-coded classification
- **Extracted Fields Panel** – Formatted key-value pairs of extracted data
- **Status Timeline** – Step indicator showing request lifecycle
- **Response Display** – AI-generated response with copy/edit options

#### 3. Analytics Dashboard
- **KPI Cards** – Total requests, avg response time, resolution rate
- **Category Distribution** – Bar/pie chart of requests by category
- **Volume Over Time** – Line chart of daily/weekly request volume
- **Top Subcategories** – Table of most common issue types
- **Team Workload** – Requests per department queue

### UI/UX Principles

- **Conversational Input** – Large free-form text area for natural language input, not rigid category dropdowns
- **Instant Feedback** – Classification result and extracted fields shown immediately after submission
- **Transparency** – Displays extracted fields so user can verify if the system understood correctly
- **Mobile Responsive** – Streamlit's responsive layout adapts to mobile and desktop
- **Quick Stats at a Glance** – Dashboard cards show key metrics without navigating away

### Key UI States

| State | Visual Treatment |
|-------|-----------------|
| **Empty** | Welcoming message, sample prompts as suggestions |
| **Loading** | Typing indicator animation while LLM processes |
| **Success** | Green checkmark, category badge, next steps shown |
| **Error** | Red alert with retry option and fallback contact info |
| **Redirect** | Amber notice if category seems wrong, offers to redirect |

### Sample UI Layout (Streamlit Dashboard)

```
┌──────────────────────────────────────────────────────────────────┐
│  🧙 OfficeGenie                          [ Analytics ] [ Help ] │
├──────────────┬───────────────────────────────────────────────────┤
│             │                                                    │
│  Navigation │   Welcome back, Ananya!                           │
│  ─────────  │   Here's your support dashboard.                  │
│  📊 Home    │                                                    │
│  📝 Submit  │   ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  📈 Stats   │   │  1247   │  │  4.2s   │  │  98.1%  │           │
│             │   │ Total   │  │ Avg Time│  │Resolved │           │
│  Categories │   └─────────┘  └─────────┘  └─────────┘           │
│  ─────────  │                                                    │
│  🖥️ IT      │   Submit a New Request                            │
│  👥 HR      │   ┌───────────────────────────────────────────┐   │
│  💰 Payroll │   │ Type your request here...                 │   │
│  🏢 Admin  │   │ I can't access my payslip for June...     │   │
│             │   └───────────────────────────────────────────┘   │
│             │                        [ Submit Request ]             │
│             │                                                    │
│             │   Recent Requests                                  │
│             │   ┌─────────────────────────────────────────────┐ │
│             │   │ June 15 | Payroll – Payslip Access | 🟡 Open │ │
│             │   │ June 12 | IT – Password Reset      | 🟢 Done │ │
│             │   └─────────────────────────────────────────────┘ │
└──────────────┴───────────────────────────────────────────────────┘
```

---

## Summary

OfficeGenie transforms employee support from a manual, slow process into an instant, AI-powered experience. Employees get immediate acknowledgment and routing confirmation. Support teams receive properly classified, pre-extracted requests ready for action. Analytics provide visibility into volume trends and team performance.

The system is designed for rapid deployment, using proven technologies (FastAPI backend with Streamlit frontend, SQLite) and well-documented LLM APIs, while remaining flexible enough to swap in different LLM providers as needed.