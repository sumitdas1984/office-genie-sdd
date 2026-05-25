# Data Models & API Contracts

Formal schemas for OfficeGenie — API request/response shapes, Pydantic models, and database schema.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/submit` | Submit request, classify via LLM, route, persist |
| `GET` | `/api/requests/{request_id}` | Get single request |
| `GET` | `/api/requests` | List requests (filter: `category`, limit: 1–100) |
| `PATCH` | `/api/requests/{request_id}/status` | Update workflow status |
| `GET` | `/api/analytics/summary` | Aggregated stats (cached 60s) |

For full API details, see `openapi.yaml`.

---

## Submit Request

```json
{
  "employee_id": "EMP-0042",
  "employee_name": "Ananya Sharma",
  "employee_email": "ananya.sharma@company.com",
  "department": "Engineering",
  "message": "I can't access my payslip for June. It shows 'file not found'. Please help."
}
```

**Fields:**
| Field | Type | Constraints |
|-------|------|-------------|
| employee_id | string | 3–20 chars, alphanumeric + hyphens |
| employee_name | string | 2–100 chars |
| employee_email | string | valid email format |
| department | string | 2–100 chars |
| message | string | 1–5000 chars |

---

## Submit Response

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

---

## LLM Response Schema

The LLM is prompted to return a strongly-typed JSON response:

```json
{
  "category": "IT|HR|Payroll|Admin",
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

---

## Classification Categories

| Category | Subcategories |
|----------|---------------|
| **IT** | Hardware, Software, Access/Permissions, Network, Security |
| **HR** | Leave, Benefits, Policies, Employee Records |
| **Payroll** | Payslip, Deductions, Reimbursements, Tax |
| **Admin** | Facilities, Travel, Supplies, Miscellaneous |

---

## Status Workflow

Requests follow a strict state machine:

```
acknowledged → in-progress → resolved → closed
```

- Invalid transitions return HTTP 400
- `updated_at` timestamp set on every status change

---

## Database Schema

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

## Request ID Format

`REQ-YYYY-NNNN` where:
- `YYYY` = current year
- `NNNN` = zero-padded 4-digit sequential number (wraps to 5 digits if needed)

Example: `REQ-2024-0158`

---

## Analytics Summary Response

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
  "top_subcategories": [
    { "subcategory": "Access / Permissions", "count": 214 },
    { "subcategory": "Payslip Access", "count": 187 }
  ]
}
```