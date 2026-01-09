---
id: 001
title: Create Project Constitution
stage: constitution
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: maryamkhanzada
command: /sp.constitution
labels: ["constitution", "governance", "principles", "spec-driven-development", "authentication", "security"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution document)
---

## Prompt

You are Claude Code operating under Spec-Kit Plus in a spec-driven, agentic development workflow.

====================
CORE PRINCIPLES
====================

1. SPEC-FIRST DEVELOPMENT (MANDATORY)
- Never implement anything without a written speon middleware

Database:
- PostgreSQL (Neon)
- Schema defined only in @specs/database/schema.md

====================
AUTHENTICATION RULES (STRICT)
====================

- Better Auth runs ONLY on the frontend.
- Authentication is JWT-based.
- JWT token must be sent in:
  Authorization: Bearer <token>
- Backend must:
  - Verify JWT signature using shared secret (BETTER_AUTH_SECRET)
  - Extract authenticated user_id from token
  - Enforce user isolation on every request
- Never trust user_id from URL without matching it against JWT.

====================
API RULES
====================

- All endpoints are RESTful and live under `/api/`
- All endpoints require authentication
- Unauthenticated requests must return 401
- Users can only access their own tasks
- Follow endpoint definitions from:
  @specs/api/rest-endpoints.md

====================
DATA OWNERSHIP & SECURITY
====================

- Every task MUST be associated with a user_id
- Every query MUST be filtered by authenticated user_id
- No cross-user data leakage is allowed
- Task ownership must be enforced on:
  - Read
  - Create
  - Update
  - Delete
  - Complete toggle

====================
CLAUDE.md HIERARCHY
====================

Always load instructions in this order:
1. Root /CLAUDE.md
2. Feature spec (e.g. @specs/features/task-crud.md)
3. API spec (@specs/api/...)
4. Database spec (@specs/database/...)
5. UI spec (@specs/ui/...)
6. Layer-specific CLAUDE.md:
   - /frontend/CLAUDE.md
   - /backend/CLAUDE.md

====================
IMPLEMENTATION RULES
====================

Frontend:
- Use Server Components by default
- Client Components only when required
- All API calls must go through a centralized API client
- JWT must be attached automatically to every request

Backend:
- Use SQLModel for all DB operations
- Use Pydantic models for validation
- Use dependency or middleware for JWT verification
- Handle errors with proper HTTP status codes

====================
PHASE AWARENESS
====================

Current Phase: Phase II – Full-Stack Web Application

Required Features:
- Task CRUD (web-based)
- Authentication (Better Auth + JWT)
- REST API
- Persistent database storage
- Responsive frontend UI

Future phases (e.g. chatbot) must NOT be implemented unless explicitly requested.

====================
SUCCESS CRITERIA
====================

- Code strictly matches specs
- All features are authenticated
- Frontend + backend are fully integrated
- No undocumented behavior
- Specs reflect the final implementation

If any instruction conflicts:
SPEC > CLAUDE.md > This Constitution > Assumptions (never assume)

## Response snapshot

Created comprehensive constitution for Frontend Todo App with version 1.0.0.

**Defined 7 Core Principles:**
1. Spec-First Development (MANDATORY) - No implementation without approved specs
2. Authentication & Security (STRICT) - JWT-based auth with user isolation
3. API Design & RESTful Standards - Consistent REST patterns under /api/
4. Data Ownership & User Isolation - Every resource owned by user, strict filtering
5. Tech Stack Enforcement - Next.js, FastAPI, PostgreSQL, Better Auth, JWT
6. Instruction Hierarchy - Clear priority: Spec > CLAUDE.md > Constitution
7. Phase-Aware Implementation - Phase II focus, no premature features

**Added Sections:**
- Implementation Rules (Frontend/Backend/Middleware requirements)
- Success Criteria (Spec compliance, Auth/Security, Integration, Data Integrity, Code Quality, Documentation)
- Governance (Authority, Amendment Process, Compliance Review, Runtime Guidance)

**Version:** 1.0.0 (Initial ratification)
**Ratified:** 2026-01-07
**Last Amended:** 2026-01-07

**Sync Impact Assessment:**
- ✅ plan-template.md - Constitution Check section already exists
- ✅ spec-template.md - Requirements align with principles
- ✅ tasks-template.md - Task organization reflects security requirements
- No template updates required

**File Created:**
- `.specify/memory/constitution.md` (309 lines)

## Outcome

- ✅ Impact: Constitution v1.0.0 created defining 7 core principles for spec-driven, secure, phase-aware development
- 🧪 Tests: N/A (governance document)
- 📁 Files: Created .specify/memory/constitution.md
- 🔁 Next prompts: Create feature specs (e.g., /sp.specify "task CRUD"), then planning (/sp.plan), then implementation
- 🧠 Reflection: Constitution establishes clear governance model with spec-first mandate, strict authentication rules, and tech stack constraints. Version 1.0.0 provides stable foundation for Phase II development.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution aligns with provided requirements
- Graders run and results (PASS/FAIL): N/A (no automated grading for constitution)
- Prompt variant (if applicable): N/A (initial constitution)
- Next experiment (smallest change to try): Monitor constitution usage during first feature spec/plan cycle to identify clarifications needed
