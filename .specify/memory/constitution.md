<!--
Sync Impact Report:
Version change: Initial → 1.0.0
Principles defined:
  - Spec-First Development (MANDATORY)
  - Authentication & Security (STRICT)
  - API Design & RESTful Standards
  - Data Ownership & User Isolation
  - Tech Stack Enforcement
  - Instruction Hierarchy
  - Phase-Aware Implementation
Added sections:
  - Core Principles (7 principles)
  - Implementation Rules
  - Success Criteria
  - Governance
Templates requiring updates:
  ✅ plan-template.md - Constitution Check section already present
  ✅ spec-template.md - Requirements sections align with constitution principles
  ✅ tasks-template.md - Task organization reflects authentication and security requirements
Follow-up TODOs: None
-->

# Frontend Todo App Constitution

## Core Principles

### I. Spec-First Development (MANDATORY)

Never implement anything without a written specification. All code must trace back to an approved spec document.

**Rules:**
- No feature implementation without a corresponding spec in `specs/<feature>/spec.md`
- All API endpoints must be documented in `specs/api/rest-endpoints.md` before implementation
- Database schema changes must be defined in `specs/database/schema.md` before migration
- Specs must be reviewed and approved before implementation begins
- Implementation must strictly match the spec - no undocumented behavior

**Rationale:** Spec-first development ensures clear requirements, enables independent review of design decisions before implementation cost is incurred, and creates living documentation that reflects system behavior. This prevents scope creep, reduces rework, and ensures all stakeholders understand what will be built.

### II. Authentication & Security (STRICT)

Authentication is JWT-based with strict user isolation enforced at all layers.

**Rules:**
- Better Auth runs ONLY on the frontend (Next.js)
- JWT tokens must be sent in `Authorization: Bearer <token>` header
- Backend MUST verify JWT signature using shared secret (BETTER_AUTH_SECRET)
- Backend MUST extract authenticated user_id from validated JWT token
- Backend MUST enforce user isolation on every data access request
- Never trust user_id from URL/request body - only from validated JWT
- Unauthenticated requests MUST return HTTP 401
- Unauthorized access attempts MUST return HTTP 403

**Rationale:** Security is non-negotiable. JWT-based authentication with server-side verification prevents token forgery and ensures only authenticated users access the system. User isolation prevents data leakage between accounts, which is critical for multi-tenant applications.

### III. API Design & RESTful Standards

All API endpoints follow REST conventions and live under `/api/` with consistent patterns.

**Rules:**
- All endpoints are RESTful and use appropriate HTTP verbs (GET, POST, PUT, DELETE)
- All endpoints require authentication unless explicitly documented as public
- Endpoints must follow pattern: `/api/<resource>` or `/api/<resource>/<id>`
- Response status codes must be semantically correct (200, 201, 400, 401, 403, 404, 500)
- Errors must return structured JSON with `{ "error": "message" }` format
- All endpoint contracts must be defined in `specs/api/rest-endpoints.md`
- Backend must handle CORS appropriately for frontend requests

**Rationale:** Consistent API design reduces cognitive load, makes the system predictable, and enables frontend developers to work independently once contracts are defined. REST conventions are widely understood and supported by tooling.

### IV. Data Ownership & User Isolation

Every data resource must be owned by a user, and users can only access their own data.

**Rules:**
- Every task record MUST include a `user_id` field
- Every database query MUST filter by authenticated `user_id`
- No cross-user data leakage is allowed under any circumstances
- Task ownership must be enforced on all operations: Read, Create, Update, Delete, Complete toggle
- Database constraints should enforce data ownership where possible
- All API responses must only include data owned by the authenticated user

**Rationale:** User isolation is the foundation of data security in multi-tenant applications. Without strict enforcement at the data layer, authorization vulnerabilities can expose user data to unauthorized parties, violating user trust and potentially regulations (GDPR, CCPA, etc.).

### V. Tech Stack Enforcement

Technology choices are locked to ensure consistency and prevent fragmentation.

**Stack:**
- **Frontend:** Next.js 15+ (App Router), React Server Components, TypeScript, Tailwind CSS
- **Backend:** FastAPI (Python), SQLModel for ORM
- **Database:** PostgreSQL (Neon hosted)
- **Authentication:** Better Auth (frontend only), JWT tokens
- **Validation:** Pydantic models (backend), Zod schemas (frontend)
- **HTTP Client:** Centralized API client on frontend with automatic JWT attachment

**Rules:**
- Use Server Components by default; Client Components only when required (hooks, events, browser APIs)
- All backend database operations use SQLModel
- All API calls from frontend go through centralized API client
- JWT must be automatically attached to every authenticated request
- Use dependency injection or middleware for JWT verification on backend

**Rationale:** Stack consistency reduces onboarding time, simplifies dependency management, and ensures team expertise is concentrated rather than fragmented across multiple technologies. These specific choices balance developer experience, performance, and ecosystem maturity.

### VI. Instruction Hierarchy

When instructions conflict, follow this priority order to resolve ambiguity.

**Priority Order (highest to lowest):**
1. **Spec documents** (`specs/<feature>/spec.md`, `specs/api/rest-endpoints.md`, etc.)
2. **Root CLAUDE.md** (this file)
3. **Layer-specific CLAUDE.md** (`frontend/CLAUDE.md`, `backend/CLAUDE.md`)
4. **Constitution** (`.specify/memory/constitution.md`)
5. **Assumptions** (never assume - if not documented, ask for clarification)

**Load Order:**
1. Root `/CLAUDE.md`
2. Feature spec (e.g., `specs/features/task-crud.md`)
3. API spec (`specs/api/*`)
4. Database spec (`specs/database/*`)
5. UI spec (`specs/ui/*`)
6. Layer-specific CLAUDE.md files

**Rationale:** Clear hierarchy prevents decision paralysis when instructions conflict. Specs have highest priority because they represent explicit, reviewed requirements. CLAUDE.md provides workflow guidance. Constitution defines principles. Assumptions are forbidden to prevent undocumented behavior.

### VII. Phase-Aware Implementation

Implementation must respect the current project phase and avoid premature features.

**Current Phase:** Phase II – Full-Stack Web Application

**Phase II Required Features:**
- Task CRUD operations (web-based UI)
- User authentication (Better Auth + JWT)
- REST API (FastAPI backend)
- Persistent database storage (PostgreSQL via Neon)
- Responsive frontend UI (Next.js)

**Explicitly Out of Scope:**
- Chatbot features (reserved for future phases)
- Mobile native applications
- Real-time collaboration
- Advanced analytics
- Third-party integrations

**Rules:**
- Only implement features explicitly listed in current phase
- Future phase features must NOT be implemented unless explicitly requested and documented
- Phase transitions require updated specs and constitution amendments
- Avoid premature abstractions for future features

**Rationale:** Phase discipline prevents over-engineering and keeps implementation focused on delivering current value. Building for speculative future requirements increases complexity, testing burden, and time to delivery without proven benefit.

## Implementation Rules

### Frontend Rules

**Server Components (Default):**
- Use React Server Components by default for all pages and layouts
- Server Components enable direct data fetching, reduced client bundle, better SEO
- No `'use client'` directive unless hooks, event handlers, or browser APIs required

**Client Components (When Required):**
- Use `'use client'` directive for: useState, useEffect, event handlers, browser APIs
- Keep Client Components small and focused
- Prefer Server Components for data fetching and business logic

**API Integration:**
- All API calls MUST go through centralized API client (`lib/api-client.ts` or similar)
- JWT token MUST be automatically attached to every request
- Handle authentication errors (401) by redirecting to login
- Handle authorization errors (403) with appropriate user feedback
- Display loading states during API calls
- Handle and display API errors to users

### Backend Rules

**Database Operations:**
- Use SQLModel for all database models and queries
- All queries MUST filter by authenticated `user_id`
- Use async database operations where supported
- Handle database connection errors gracefully

**Validation:**
- Use Pydantic models for request/response validation
- Validate all input at API boundary
- Return 400 Bad Request for validation failures with clear error messages

**JWT Verification:**
- Use FastAPI dependency injection for JWT verification
- Create a dependency that validates JWT and extracts `user_id`
- Apply dependency to all protected endpoints
- Handle JWT expiration, invalid signatures, missing tokens

**Error Handling:**
- Use appropriate HTTP status codes (400, 401, 403, 404, 500)
- Return structured JSON errors: `{ "error": "Human-readable message" }`
- Log errors server-side for debugging
- Never expose internal error details to clients

### Middleware Requirements

**Authentication Middleware (Backend):**
- Verify JWT signature on every authenticated request
- Extract and validate `user_id` from token claims
- Attach `user_id` to request context for downstream use
- Return 401 for missing/invalid tokens

**CORS Middleware (Backend):**
- Configure allowed origins (frontend URL)
- Allow credentials for cookie-based flows if needed
- Set appropriate headers for preflight requests

## Success Criteria

Implementation is considered successful when ALL of the following are met:

**Spec Compliance:**
- [ ] Code strictly matches approved specifications
- [ ] No undocumented behavior or features
- [ ] All API endpoints match `specs/api/rest-endpoints.md`
- [ ] Database schema matches `specs/database/schema.md`

**Authentication & Security:**
- [ ] All features require authentication
- [ ] JWT verification works correctly
- [ ] User isolation is enforced on all data operations
- [ ] No cross-user data leakage possible
- [ ] Unauthenticated requests return 401
- [ ] Unauthorized requests return 403

**Integration:**
- [ ] Frontend successfully communicates with backend
- [ ] JWT tokens automatically attached to requests
- [ ] Authentication errors handled gracefully
- [ ] Loading and error states displayed to users

**Data Integrity:**
- [ ] All tasks associated with `user_id`
- [ ] Users can only see/modify their own tasks
- [ ] Database constraints enforce ownership

**Code Quality:**
- [ ] TypeScript types are correct and complete
- [ ] No type `any` without justification
- [ ] Error handling covers expected failure modes
- [ ] Logging implemented for debugging

**Documentation:**
- [ ] Specs exist and are up to date
- [ ] README explains how to run the application
- [ ] Environment variables documented
- [ ] API endpoints documented

## Governance

### Constitution Authority

This constitution supersedes all other practices and guidelines. When conflicts arise, constitution principles take precedence after specs and CLAUDE.md hierarchy.

### Amendment Process

**Constitution amendments require:**
1. Documented rationale for the change
2. Impact assessment on existing specs and code
3. User/team approval
4. Version bump according to semantic versioning
5. Migration plan for affected artifacts
6. Update to this file with new `Last Amended` date

**Version Bumping Rules:**
- **MAJOR (X.0.0):** Backward incompatible changes, principle removals, or redefinitions that invalidate existing implementations
- **MINOR (0.X.0):** New principles added, material expansions to existing guidance that affect workflow
- **PATCH (0.0.X):** Clarifications, wording improvements, typo fixes, non-semantic refinements

### Compliance Review

**All development activities must verify compliance with:**
- Spec-first development (no implementation without spec)
- Authentication rules (JWT verification, user isolation)
- API design standards (REST conventions, error handling)
- Tech stack requirements (no unauthorized dependencies)
- Phase boundaries (no future-phase features)

**Code reviews must check:**
- User isolation on all data queries
- JWT verification on all protected endpoints
- Proper error handling and status codes
- Spec traceability for all features

**Complexity justification required when:**
- Adding new dependencies outside approved stack
- Introducing abstractions beyond current requirements
- Implementing features not in current phase
- Deviating from REST conventions

### Runtime Guidance

For detailed runtime development guidance, refer to:
- `/CLAUDE.md` - Workflow and agent behavior
- `frontend/CLAUDE.md` - Frontend-specific guidance (if exists)
- `backend/CLAUDE.md` - Backend-specific guidance (if exists)

---

**Version**: 1.0.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-01-07
