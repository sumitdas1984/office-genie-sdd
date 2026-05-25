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

## Summary

OfficeGenie transforms employee support from a manual, slow process into an instant, AI-powered experience. Employees get immediate acknowledgment and routing confirmation. Support teams receive properly classified, pre-extracted requests ready for action. Analytics provide visibility into volume trends and team performance.

The system is designed for rapid deployment, using proven technologies (FastAPI backend with Streamlit frontend, SQLite) and well-documented LLM APIs, while remaining flexible enough to swap in different LLM providers as needed.

---

## Further Reading

- [Architecture](architecture.md) — System architecture, processing pipeline, component responsibilities
- [API Contracts](api-contract/openapi.yaml) — Formal API specification (OpenAPI)
- [Data Models](api-contract/data-models.md) — Pydantic schemas and database schema
- [Feature Backlog](features/backlog.md) — Feature/Epic backlog for implementation planning