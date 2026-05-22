# OfficeGenie – Product Idea

## Overview

OfficeGenie is an AI-powered assistant that acts as a first-line triage system for employee support requests. It classifies natural language queries (e.g., IT, HR, Admin), extracts key details, and routes the issue to the correct team — with an instant response.

---

## Core Features

- 📝 Accepts user queries via web form
- 🧠 Classifies requests (IT, HR, Payroll, etc.)
- 🔍 Extracts structured info like system names, urgency, dates, etc.
- 📬 Sends automated acknowledgment
- 🔁 Routes request to the right department or automation
- 📊 Logs requests for future analytics

---

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.10+
- **LLM**: OpenAI
- **Data**: JSON-based input/output + optional SQLite
- **Other**: Prompt templating, Logging

---

## Sample Use Case

> **User Message:** "I can't access my payslip for June. It shows 'file not found'. Please help."

**Predicted Output:**

```json
{
  "category": "Payroll",
  "subcategory": "Payslip Access",
  "extracted_fields": {
    "month": "June",
    "error_message": "file not found"
  },
  "suggested_response": "Hi Ananya, we've shared your payslip issue with the Payroll team. You'll get an update shortly."
}
```
