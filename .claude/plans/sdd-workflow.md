# SDD-Driven Automated Development Workflow

## Overview

This project uses a Specification-Driven Development (SDD) pipeline powered by Claude agents that communicate through GitHub issues. The workflow automates the full feature delivery cycle from issue to merged code.

## Pipeline Architecture

```
/create-features  →  /parse-requirement  →  /create-stories  →  /implement × N  →  /update-knowledge  →  /create-pr
     (entry)              (classify)            (decompose)          (build)              (docs)             (package)
```

---

## Step 1: Create Features — `/create-features`

**Agent:** `.claude/agents/create-features.md`

**Trigger:** `/create-features <product_doc_path>`

**What it does:**
- Reads the product document (PRD, HLD, architecture spec)
- Maps business capabilities and subsystems
- Decomposes into Feature/Epic backlog items (3–8 stories each)
- Creates GitHub issues directly via `mcp__github__issue_write`

**When to use:** Entry point — when you have a new product overview or PRD to turn into features.

---

## Step 2: Parse Requirement — `/parse-requirement`

**Agent:** `.claude/agents/parse-requirement.md`

**Trigger:** `/parse-requirement <issue_number>`

**What it does:**
- Fetches the GitHub issue
- Classifies it (Feature/Epic/Bug/Chore/Story)
- Extracts: problem statement, scope, constraints, acceptance criteria
- Identifies missing or unclear information (gaps)
- Posts a structured comment on the issue
- Recommends: `create-stories`, `implement-feature`, or `needs-more-info`

**When to use:** First step on any new feature or epic issue.

---

## Step 2: Create Stories — `/create-stories`

**Agent:** `.claude/agents/create-stories.md`

**Trigger:** `/create-stories <feature_issue_number>`

**What it does:**
- Reads the parsed feature issue and existing codebase
- Decomposes the feature into 4–8 implementable Story sub-issues
- Each story includes:
  - User story, goal, architecture notes
  - File structure (what to create/modify)
  - TDD plan with exact steps
  - Complexity rating
  - Recommended superpowers
- Creates all stories as GitHub sub-issues linked to the parent
- Posts a summary comment on the parent issue

**When to use:** After `/parse-requirement` on a Feature or Epic.

---

## Step 3: Implement Feature — `/implement-feature`

**Agent:** `.claude/agents/implement-feature.md`

**Trigger:** `/implement-feature <story_number>`

**What it does:**
- Reads the story's TDD plan
- Supports two modes:
  - **Plan Execution Mode:** Follows the pre-built TDD plan from the issue
  - **Standalone Mode:** Creates its own plan if none exists
- Executes the TDD cycle:
  ```
  Write failing test  →  Run (verify FAIL)  →  Write implementation  →  Run (verify PASS)  →  Commit
  ```
- Pushes commits to the feature branch
- Closes the story issue when done

**When to use:** Once per story. Repeat for all stories in the feature.

---

## Step 4: Update Knowledge — `/update-knowledge`

**Agent:** `.claude/agents/update-knowledge.md`

**Trigger:** `/update-knowledge`

**What it does:**
- Reads the current `CLAUDE.md` and docs
- Identifies gaps between what was built and what is documented
- Updates `CLAUDE.md` to reflect new file structure, endpoints, services
- Removes references to unimplemented components
- Cleans up any outdated documentation

**When to use:** After all stories are implemented, before creating the PR.

---

## Step 5: Create PR — `/create-pr`

**Agent:** `.claude/agents/create-pr.md`

**Trigger:** `/create-pr`

**What it does:**
- Collects all commits on the feature branch
- Fetches the linked feature issue and stories
- Creates a PR with:
  - Summary of what was built
  - Test plan checklist
  - Acceptance criteria checklist
  - Stories completed
  - Linked issues
- Invokes code review agent

**When to use:** After all stories complete and docs are updated.

---

## Step 6: Code Review — `/review`

**Agent:** `.claude/agents/code-review.md`

**Trigger:** `/review` or invoked by `/create-pr`

**What it does:**
- Fetches the PR diff and changed files
- Reviews for: bugs, security, quality, performance, test coverage
- Posts a structured review comment to the PR
- Can fix critical issues and push directly to the feature branch
- Sets verdict: `✅ Approved` or `⚠️ Request Changes`

**When to use:** After PR is created, before merging.

---

## Branching Strategy

### Branch Structure
```
main            — production-ready code (protected)
develop        — integration branch for completed features
feature/FEATURE-00X  — feature branches (one per feature)
```

### Feature Workflow
```
1. Ensure develop is clean and up to date:
   git checkout develop && git pull origin develop

2. Create feature branch from develop:
   git checkout -b feature/FEATURE-002 develop

3. Do ALL work on this branch:
   /parse-requirement <feature_issue_number>
   /create-stories <feature_issue_number>
   /implement-feature <story_number>
   ... (all stories)

4. Update docs and create PR:
   /update-knowledge
   /create-pr

5. After PR merges, switch back to develop and sync:
   git checkout develop && git pull origin develop

6. Delete feature branch (optional):
   git branch -d feature/FEATURE-002
```

### Rule: Never commit directly to `develop` or `main`. All work happens on feature branches.

---

## TDD Cycle (per Story)

Each story has a TDD plan embedded in its GitHub issue. The executor follows this exact sequence:

```
Step 1: Write failing test
  → Create test file or add test case
  → Run: uv run pytest tests/X -v
  → Verify: test FAILS (expected)

Step 2: Write implementation
  → Create or modify source files
  → Match the exact contract the test expects

Step 3: Run tests
  → Run: uv run pytest -v
  → Verify: test PASSES

Step 4: Commit
  → git add <files>
  → git commit -m "feat(story-N): <description>

Step 5: Push and close issue
  → git push origin feature/FEATURE-00X
  → Close story issue via GitHub MCP
```

---

## File Structure

### Agent Files (`.claude/agents/`)
| Agent | Purpose |
|-------|---------|
| `parse-requirement.md` | Entry agent — classifies and parses issues |
| `create-stories.md` | Decomposer — breaks features into stories |
| `implement-feature.md` | TDD executor — implements one story |
| `update-knowledge.md` | Docs agent — updates project knowledge |
| `create-pr.md` | Packager — creates PR from feature branch |
| `code-review.md` | Reviewer — automated code quality review |

### Command Files (`.claude/commands/`)
Each command file is a one-liner pointing to its agent:
```
agent: .claude/agents/<agent-name>.md
```

### Commands Available
| Command | Agent |
|---------|-------|
| `/create-features` | create-features.md |
| `/parse-requirement` | parse-requirement.md |
| `/create-stories` | create-stories.md |
| `/implement-feature` | implement-feature.md |
| `/update-knowledge` | update-knowledge.md |
| `/create-pr` | create-pr.md |
| `/review` | code-review.md |

---

## Example: Full Feature Lifecycle

**FEATURE-001: Request Intake Pipeline**

```bash
# 1. Start fresh on develop
git checkout develop && git pull origin develop
git checkout -b feature/FEATURE-001 develop

# 2. Create features from product docs
/create-features docs/product-overview.md docs/architecture.md
# → Created issues #36–#43

# 3. Parse the feature issue
/parse-requirement 36

# 4. Decompose into stories
/create-stories 36
# → Created story sub-issues linked to #36

# 5. Implement each story
/implement-feature <story_number>
# ... (repeat for all stories)

# 6. Update documentation
/update-knowledge

# 7. Create PR
/create-pr
# → PR created targeting develop

# 8. Review
/review
# → Code review posted, bugs fixed

# 9. Merge
# → PR merged to develop on GitHub

# 10. Sync develop
git checkout develop && git pull origin develop
```

---

## Verification Commands

```bash
# Run all tests
uv run pytest -v

# Run tests for a specific story
uv run pytest tests/unit/test_llm_service.py -v

# Run the FastAPI dev server
uv run fastapi dev src/main.py --port 8000

# Check branch status
git branch -v
```

---

## Key Constraints

- **Python 3.13+**, **uv** for package management
- Backend: FastAPI + Pydantic + SQLite + Jinja2 + OpenAI GPT
- All feature work on dedicated branches from `develop`
- Never commit directly to `develop` or `main`
- Every story follows TDD: failing test → implementation → passing test → commit
- Docs updated (`/update-knowledge`) before PR creation
- Code review (`/review`) before merge