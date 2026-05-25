---
name: generate-features
description: >
  Use this skill whenever the user wants to generate a feature backlog, write GitHub Issues,
  decompose a product overview into feature specifications, or create a backlog.md from a
  product/architecture document.

  Trigger on phrases like:
  "generate features",
  "create backlog",
  "break down my product doc",
  "generate GitHub issues",
  "turn my PRD into backlog",
  "generate SDD features",
  "prepare features for create-stories",
  "create epic backlog",
  or "decompose this design into features".

  Also use whenever the user mentions:
  - Specification-Driven Development (SDD)
  - engineering planning
  - autonomous development pipelines
  - GitHub feature generation
  - Feature/Epic creation
  - backlog generation for engineering agents

version: 1.0.0
---

# Generate Features (Feature/Epic Backlog Generator)

Transforms a product overview, architecture document, or design specification into a
structured Feature/Epic backlog formatted as GitHub Issues in `backlog.md`.

This skill operates as a:

- Systems Architect
- Product Owner
- Technical Planner

It defines:

- capability boundaries
- execution scope
- integrations
- operational requirements
- measurable outcomes

but does NOT:

- write implementation code
- write unit tests
- create implementation tasks
- generate class-level or file-level work items.

The generated backlog MUST be optimized for:

```text
Feature/Epic
    ↓
create-stories
    ↓
implementation stories
    ↓
engineering execution
```

NOT:

```text
feature
    ↓
direct coding
```

---

# Inputs

| Input | Description |
|---|---|
| product_doc | Path to product overview / HLD / LLD / PRD |

Required sections:

- Overview
- Core Features or Functional Scope
- Architecture or Tech Stack

Optional:

- OpenAPI
- Data model
- Workflow diagrams
- UI specification

---

# Core Backlog Philosophy

The purpose of this skill is to generate:

# Feature/Epic backlog

NOT:

- implementation tasks
- coding checklist
- helper-level work items
- endpoint-only stories
- developer TODOs

Generated backlog items should represent:

> cohesive platform capabilities

that are valuable and independently understandable.

Each generated item should typically be:

- decomposable into 3–8 implementation stories
- independently reviewable
- architecture-aware
- suitable for create-stories style decomposition.

---

# Feature Sizing Model

Use the following sizing guidance.

## DO Generate

### Small Feature

Usually:

- 2–3 coordinated components
- clear capability boundary
- likely 2–4 stories

Examples:

- LLM Classification Engine
- Request Retrieval API
- Status Workflow

### Feature

Preferred default.

Usually:

- multiple modules
- integration points
- resilience/monitoring/configuration
- 3–6 stories

Examples:

- Persistence Layer
- Logging & Tracing
- Submission Experience

### Epic

Use when:

- cross-cutting
- multiple subsystems
- backend + frontend
- broad capability

Usually:

- 5–10 stories

Examples:

- Dashboard Experience
- Analytics Platform
- Identity & Access Management

---

## DO NOT Generate

Avoid generating top-level backlog items that are:

### Story-sized

Reject:

- helper utilities
- validators
- retry helpers
- single middleware
- single parser
- class-level work
- isolated endpoint implementation
- file-level tasks

These belong inside create-stories output.

---

# Execution Pipeline

## Step 1 — Input Discovery

Read:

`{{product_doc}}`

Establish:

- product goals
- workflows
- actors
- integrations
- architecture
- non-functional requirements

If missing or incomplete:

HALT.

Return:

- missing sections
- clarification request
- validation error.

Also inspect:

```text
docs/openapi.yaml
```

if present.

Use it to:

- understand existing APIs
- extend
- avoid duplication.

---

## Step 2 — Capability Mapping

Identify:

- major business capabilities
- architectural subsystems
- user journeys
- platform services
- operational concerns
- resilience requirements
- observability requirements

Build:

```text
Product
    ↓
Capabilities
    ↓
Feature/Epic backlog
```

NOT:

```text
Product
    ↓
implementation checklist
```

---

## Step 3 — Feature/Epic Decomposition

Decompose into:

cohesive capabilities.

Each feature should:

- solve a recognizable problem
- own a capability boundary
- include operational requirements
- define integrations
- define resilience expectations
- be independently meaningful.

Prefer:

vertical capability slicing.

Example:

Prefer:

```text
Request Intake Pipeline
```

over:

```text
validation
parser
serializer
```

when these form one user-visible capability.

Cross-cutting concerns should become Features:

Examples:

- Logging & Tracing
- Reliability
- Observability
- Analytics

---

# create-stories Readiness Test

Before emitting a feature:

ask:

> Could this reasonably decompose into 3–8 implementation stories?

If:

NO

then it is likely:

story-sized

and should be merged or elevated.

---

# Priority Ordering

Sort:

1. Must Have
2. Should Have
3. Nice To Have

Use:

Business criticality
+
dependency ordering
+
 platform enablement.

Core platform capabilities usually precede UI polish.

---

# Mandatory Platform Features

Always ensure backlog includes coverage for:

- validation
- resilience
- logging/tracing
- observability
- configuration
- failure handling
- operational readiness

These may be standalone Features or embedded into broader platform Features.

---

# Output Generation

Write:

```text
{{product_doc_directory}}/backlog.md
```

All items must use the Feature template.

Do NOT:

- add TODO comments
- leave placeholders
- omit sections.

---

# GitHub Feature Template

Use exact template:

~~~markdown
## 📋 FEATURE-[ID]: [Capability-Oriented Feature Name]

### Description
Explain:

- capability
- business value
- problem solved
- desired outcome

---

### Scope

Define:

- Core Implementation
- Integration Points
- Configuration & Management
- Security & Governance
- Performance & Monitoring
- Developer Experience
- Data Handling
- Error Handling & Resilience

Scope should define:

capability boundaries

NOT:

implementation tasks.

---

### Acceptance Criteria

Only include:

- measurable
- system-level
- independently testable outcomes

Avoid:

implementation instructions.

Use:

- functionality
- performance
- resilience
- monitoring
- governance
- logging
- operational expectations
- developer usability

Target:

95%+ coverage expectation.

~~~

---

# Final Quality Gate

Validate backlog before writing.

Reject and revise if:

- more than 40% of items are story-sized
- items are implementation-task oriented
- backlog reads like TODO list
- capabilities are fragmented
- create-stories decomposition would add little value.

Target outcome:

```text
Feature/Epic backlog
    ↓
create-stories
    ↓
story backlog
    ↓
implementation
```