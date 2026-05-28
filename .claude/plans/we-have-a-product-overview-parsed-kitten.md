# Plan: Docs Directory Reorganization

## Context

The `docs/` directory has grown organically and now contains overlapping concerns:
- `product-overview.md` tries to be product vision, architecture, data models, API contracts, and UI spec all at once
- `openapi.yaml` duplicates API descriptions already in `product-overview.md`
- `product-idea.md` is an early-stage artifact now superseded by `product-overview.md`
- `feature-template.md` lives at the root level but belongs with feature specs
- `archive/` contains old agent docs that are no longer referenced

This creates drift risk and makes it hard to find things. The reorganization cleans this up with a "one concept per file" principle, without adding unnecessary formality like HLD/LLD distinction.

---

## Proposed Structure

```
docs/
├── product-overview.md      # Product vision, capabilities, tech philosophy (WHAT & WHY)
├── architecture.md           # System architecture, data flow, component responsibilities (HOW)
├── api-contract/
│   ├── openapi.yaml         # Formal API surface (already exists)
│   └── data-models.md       # Pydantic models & DB schema (extracted from product-overview)
├── features/
│   ├── feature-template.md  # Template for writing feature specs
│   └── backlog.md           # Generated feature/Epic backlog
└── ui/
    └── ui-mockup.png        # Design reference (move from root)
```

**What stays:**
- `product-overview.md` — trimmed to product vision + capabilities + tech philosophy (no technical details)
- `openapi.yaml` — no changes needed

**What moves:**
- DB schema, data models, Pydantic schemas → `api-contract/data-models.md`
- `feature-template.md` → `features/feature-template.md`
- `backlog.md` → `features/backlog.md`
- `ui-mockup.png` → `ui/ui-mockup.png`

**What is deleted:**
- `product-idea.md` (superseded by product-overview)
- `archive/` (old agent docs, no longer referenced)

---

## Steps

1. **Create new directories:**
   - `docs/api-contract/`
   - `docs/features/`
   - `docs/ui/`

2. **Create `docs/architecture.md`** — extract system architecture section from `product-overview.md`:
   - Processing pipeline (7 steps)
   - Backend/frontend component responsibilities
   - Routing logic description
   - LLM failure handling
   - Structured logging approach

3. **Create `docs/api-contract/data-models.md`** — extract from `product-overview.md`:
   - LLM Response schema (structured output)
   - Database schema (SQL CREATE TABLE)
   - Request ID format (REQ-YYYY-NNNN)
   - Status workflow (acknowledged → in-progress → resolved → closed)

4. **Trim `docs/product-overview.md`** — remove:
   - Backend specification (moved to architecture.md + data-models.md)
   - Frontend specification (moved to architecture.md)
   - Database schema (moved to data-models.md)
   - Keep only: Overview, Core Product Features (6 items), Summary

5. **Move files:**
   - `feature-template.md` → `features/`
   - `backlog.md` → `features/`
   - `ui-mockup.png` → `ui/`

6. **Delete obsolete files:**
   - `docs/product-idea.md`
   - `docs/archive/` (entire directory)

---

## Verification

After reorganization:
1. `docs/product-overview.md` should be focused on "what problem does it solve and how does it help users"
2. `docs/architecture.md` should describe "how the system works technically"
3. `docs/openapi.yaml` should be the single source of truth for API contracts
4. `docs/api-contract/data-models.md` should contain all schema definitions
5. No file should duplicate content already described elsewhere
6. `docs/features/` should contain feature specs and the backlog

Run: `ls -la docs/` and `ls -la docs/api-contract/ docs/features/ docs/ui/` to confirm structure.