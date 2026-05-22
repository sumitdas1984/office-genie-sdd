---
name: generate-features
description: >
  Use this skill whenever the user wants to generate a feature backlog, write GitHub Issues,
  decompose a product overview into specs, or create a tasks/backlog.md from a product document.
  Trigger on phrases like "generate features", "create backlog", "break down my product doc",
  "write feature specs", "generate GitHub issues from my overview", or "turn my PRD into tasks".
  Also use when the user mentions Specification-Driven Development (SDD), wants to prepare work
  items for engineering agents, or asks to decompose any product/requirements document into
  structured, testable feature definitions.
version: 1.0.0
---

# Generate Features (SDD Backlog Generator)

Transforms a product overview document into an exhaustive, structured feature backlog formatted
as GitHub Issues in `tasks/backlog.md`. This skill operates as a Systems Architect + Product Owner
subagent — it defines crisp execution parameters and data contracts, but does NOT write application
code or unit tests.

---

## Inputs

| Input | Description |
|-------|-------------|
| `product_doc` | Path to the product overview markdown (e.g. `docs/product-overview.md`). Must contain at minimum: **Overview**, **Core Features**, and **Tech Stack** sections. |

---

## Execution Pipeline

### Step 1 — Input Discovery

Read the product scoping document at `{{product_doc}}` to establish full functional context.

- If the file is **missing or lacks clear functional parameters**, halt and report a detailed
  input validation error to the user. Do not proceed with incomplete input.
- Also check for `docs/openapi.yaml` in the same directory. If it exists, read it to understand
  the already-specified API surface — **extend it, don't redo it**.

### Step 2 — Architectural Decomposition

Deconstruct the product overview into **atomic, independent features**.

- Decouple frontend presentation layers and backend analytical schemas into separate tracking blocks.
- For each feature, define tight technical boundaries: what inputs must yield what specific outputs.
- Sort by priority: **Must Have → Should Have → Nice to Have** (see Priority table below).
- Always include at least one feature covering: structured error handling, input validation,
  request logging/tracing, and observability.

### Step 3 — Write `{{product_doc_directory}}/backlog.md`

Compile all features into a single file at `{{product_doc_directory}}/backlog.md` (in the same directory as the input product document).

Every feature **must** use the GitHub Issue template below. Do not abbreviate, omit sections,
or leave placeholder comments like `<!-- Add details later -->`.

---

## GitHub Issue Template

Use this exact schema for every feature:

~~~markdown
## 📋 FEATURE-[ID]: [Short, Actionable Feature Name]

### 1. User Story / Objective
- **As a:** [User Persona or Core System Component]
- **I want to:** [Clear statement of functional intent]
- **So that:** [The engineering value or business outcome]

### 2. Functional Description
[2-3 sentence overview of the feature's behavior and user interaction loop.
Focus on WHAT the system does — no implementation or internal code specifics.]

### 3. Technical Data Contract & Boundaries
* **Trigger/Input Conditions:**
  - `Parameter`: [Data Type & Limits] - [Constraint Description]
* **Expected Output/Response:**
  - `Return Payload`: [Data Type or Pydantic Structure]
  - `Expected Schema`: [Literal JSON representation of fields]
* **Error Handling States:**
  - If [Input condition fails] -> Throw [Specific Exception or HTTP Status Code]
  - If [System failure] -> Catch cleanly, log data, and return [Graceful Fallback State]

### 4. Behavioral & Execution Workflow
```text
[Input Triggered] ───> [Schema Validation] ───> [Core Logic Execution] ───> [Output Rendered]
```

### 5. Binary Acceptance Criteria (QA Guardrails)
- [ ] AC-1 (Happy Path): [Explicitly testable assertion]
- [ ] AC-2 (Edge Case - Null/Empty): [Explicitly testable assertion]
- [ ] AC-3 (Input Normalization): [Explicitly testable assertion]
- [ ] AC-4 (Boundary Constraint): [Explicitly testable assertion]

### 🛠️ Downstream Implementation Tasks
- [ ] Define data validation schemas (Pydantic / Frontend Models).
- [ ] Implement core business logic and matching calculations.
- [ ] Expose endpoint/interface bindings.
~~~

---

## Priority Reference

| Priority | Meaning |
|----------|---------|
| **Must Have** | Blocking — system cannot function safely or correctly without it |
| **Should Have** | Improves correctness or UX meaningfully but has workarounds |
| **Nice to Have** | Polish or advanced capabilities |

---

## Strict Output Guardrails

- **Binary ACs only.** Every Acceptance Criterion must be an explicitly testable assertion.
  Never use vague words like "user-friendly", "performant", or "optimized".
  ✅ Good: "Verify that execution returns HTTP 422 if text exceeds 5,000 characters"
  ❌ Bad: "Ensure the response is fast and user-friendly"

- **No implementation bias.** Do not write code loops or instruct developers on how to implement.
  Restrict content to data boundaries, validation states, and output expectations.

- **No duplication.** Do not re-document features already fully specified in the OpenAPI spec.

- **No tech stack violations.** Do not suggest features that contradict the defined tech stack.

- **MVP focus.** Resist feature bloat. Features must be practical and prioritized.

---

## Output

Write the complete feature backlog to `{{product_doc_directory}}/backlog.md`.