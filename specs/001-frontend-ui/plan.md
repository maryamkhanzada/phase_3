# Implementation Plan: Frontend UI for Todo Application

**Branch**: `001-frontend-ui` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-frontend-ui/spec.md`

**Note**: This plan covers FRONTEND ONLY. Backend API is assumed to exist and is out of scope.

## Summary

Build a complete frontend UI for the Todo application using Next.js 15+ App Router, Better Auth for JWT-based authentication, and Tailwind CSS for styling. The frontend will consume existing REST API endpoints with automatic JWT token attachment, implement protected routing, and provide a responsive task management interface across authentication, task CRUD, and UX enhancement phases.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 15+
**Primary Dependencies**: Next.js (App Router), React 18+, Better Auth, Tailwind CSS, Zod (validation)
**Storage**: Browser localStorage/cookies for JWT tokens (frontend session management only)
**Testing**: Jest + React Testing Library for unit tests, Playwright for E2E (optional)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
**Project Type**: Web application frontend
**Performance Goals**: First Contentful Paint < 1.5s, task operations < 300ms, 100 tasks render < 2s
**Constraints**: Mobile-first (320px+), keyboard accessible, JWT-based auth only, frontend-only scope
**Scale/Scope**: Single-page application, 5 routes, ~10 reusable components, optimized for <100 tasks per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**✅ Spec-First Development (MANDATORY)**
- Specification completed in specs/001-frontend-ui/spec.md
- All functional requirements documented (40 FRs)
- Success criteria defined (10 measurable outcomes)
- Ready to proceed with implementation planning

**✅ Authentication & Security (STRICT)**
- Better Auth runs on frontend only ✓
- JWT tokens sent via Authorization: Bearer header ✓
- Frontend automatically attaches JWT to authenticated requests ✓
- Protected routes redirect unauthenticated users to /login ✓
- 401 responses trigger token clearing and redirect ✓
- No backend implementation in this plan (out of scope) ✓

**✅ API Design & RESTful Standards**
- Frontend consumes existing REST API at /api/ ✓
- Assumes backend enforces authentication and returns proper status codes ✓
- Frontend API client handles 401, 403, 404, 500 errors ✓
- No API implementation in this plan (backend out of scope) ✓

**✅ Data Ownership & User Isolation**
- Frontend trusts backend to enforce user isolation ✓
- JWT contains user_id (verified backend-side) ✓
- Frontend displays only data returned by authenticated API calls ✓
- No client-side user_id manipulation ✓

**✅ Tech Stack Enforcement**
- Next.js 15+ App Router ✓
- React Server Components (default) + Client Components (as needed) ✓
- TypeScript with strict mode ✓
- Tailwind CSS for styling ✓
- Better Auth for JWT authentication ✓
- Centralized API client with automatic JWT attachment ✓

**✅ Instruction Hierarchy**
- Spec document (spec.md) is primary source of truth ✓
- Constitution principles followed ✓
- No assumptions made without documentation ✓

**✅ Phase-Aware Implementation**
- Phase II: Full-Stack Web Application (frontend portion) ✓
- No backend, database, or chatbot work included ✓
- Mobile-native apps explicitly out of scope ✓
- Real-time collaboration out of scope ✓

**GATE PASSED**: All constitution principles satisfied. Proceeding to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/001-frontend-ui/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (already exists)
├── research.md          # Phase 0 output (generated below)
├── data-model.md        # Phase 1 output (frontend data types)
├── quickstart.md        # Phase 1 output (setup instructions)
├── contracts/           # Phase 1 output (API contracts assumed from backend)
│   └── api-endpoints.md # REST API contract reference
└── checklists/
    └── requirements.md  # Spec quality checklist (already exists)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Landing/redirect page
│   │   ├── login/
│   │   │   └── page.tsx     # Login page
│   │   ├── signup/
│   │   │   └── page.tsx     # Signup page
│   │   └── app/             # Protected routes group
│   │       ├── layout.tsx   # App layout with navbar
│   │       └── tasks/
│   │           ├── page.tsx           # Task list page
│   │           ├── new/
│   │           │   └── page.tsx       # New task page
│   │           └── [id]/
│   │               └── edit/
│   │                   └── page.tsx   # Edit task page
│   ├── components/          # Reusable UI components
│   │   ├── ui/              # Base UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Loader.tsx
│   │   ├── layouts/         # Layout components
│   │   │   ├── AuthLayout.tsx
│   │   │   ├── AppLayout.tsx
│   │   │   └── Navbar.tsx
│   │   ├── tasks/           # Task-specific components
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskCard.tsx
│   │   │   └── TaskForm.tsx
│   │   └── auth/            # Auth components
│   │       ├── LoginForm.tsx
│   │       └── SignupForm.tsx
│   ├── lib/                 # Utility libraries
│   │   ├── api-client.ts    # Centralized API client
│   │   ├── auth.ts          # Better Auth configuration
│   │   └── utils.ts         # Helper functions
│   ├── types/               # TypeScript type definitions
│   │   ├── task.ts
│   │   ├── user.ts
│   │   └── api.ts
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.ts       # Auth state hook
│   │   ├── useTasks.ts      # Task data hook
│   │   └── useApi.ts        # API call hook
│   └── middleware.ts        # Next.js middleware for protected routes
├── public/                  # Static assets
│   ├── favicon.ico
│   └── images/
├── .env.local               # Environment variables
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies
```

**Structure Decision**: Frontend-only web application structure using Next.js App Router conventions. The `/app` directory contains all routes (login, signup, protected app routes). Components are organized by type (ui, layouts, tasks, auth) for clear separation of concerns. API client and utilities live in `/lib`. TypeScript types ensure type safety across the application.

## Complexity Tracking

> No constitution violations - all principles satisfied by the planned frontend architecture.

---

## Phase 0: Research & Technology Validation

**Objective**: Validate technology choices, document Better Auth integration patterns, confirm API contract assumptions, and establish frontend architecture patterns.

**Prerequisites**: Spec complete, Constitution Check passed

### Research Tasks

1. **Better Auth Integration Research**
   - Research Better Auth JWT token storage (localStorage vs httpOnly cookies)
   - Document Better Auth setup for Next.js App Router
   - Confirm JWT token extraction and automatic attachment patterns
   - Establish session persistence strategy across page refreshes

2. **Next.js App Router Protected Routes**
   - Research middleware-based route protection in App Router
   - Document redirect patterns for unauthenticated access
   - Establish loading states during auth checks
   - Confirm Server Component vs Client Component patterns for auth

3. **API Client Architecture**
   - Research fetch wrapper patterns with automatic JWT injection
   - Document error handling for 401, 403, 404, 500 responses
   - Establish retry logic and network error handling
   - Confirm environment variable usage for API base URL

4. **State Management Strategy**
   - Research whether React Context, Zustand, or component state is sufficient
   - Document data fetching patterns (Server Components vs Client hooks)
   - Establish cache invalidation strategy (optimistic updates, refetching)
   - Confirm form state management patterns (controlled inputs)

5. **Tailwind CSS Setup**
   - Document Tailwind configuration for mobile-first responsive design
   - Establish component styling patterns (cn utility for conditional classes)
   - Confirm accessibility utilities (focus states, aria attributes)
   - Document color scheme and spacing conventions

**Output**: `research.md` with decisions, rationales, and implementation patterns for all unknowns

**Completion Criteria**:
- All NEEDS CLARIFICATION items from Technical Context resolved
- Better Auth setup pattern documented
- Protected route strategy confirmed
- API client architecture defined
- State management approach selected
- Tailwind setup validated

---

## Phase 1: Design Artifacts

**Objective**: Define frontend data models, document assumed API contracts, create quickstart guide for local development.

**Prerequisites**: Phase 0 research complete

### 1.1 Data Model (Frontend Types)

Create `data-model.md` defining TypeScript interfaces for:

**Entities**:
- **User** (frontend session):
  - `email: string`
  - `id: string` (extracted from JWT, not stored separately)
  - `token: string` (JWT, stored in localStorage/cookies)

- **Task** (matches API response):
  - `id: string` (UUID from backend)
  - `title: string` (required)
  - `description: string | null` (optional)
  - `completed: boolean`
  - `user_id: string` (from backend, not displayed)
  - `created_at: string` (ISO timestamp)
  - `updated_at: string` (ISO timestamp)

**API Response Types**:
- `TaskListResponse: { tasks: Task[] }`
- `TaskResponse: { task: Task }`
- `ErrorResponse: { error: string }`
- `AuthResponse: { token: string, user: { id: string, email: string } }`

**Form Types**:
- `LoginFormData: { email: string, password: string }`
- `SignupFormData: { email: string, password: string }`
- `TaskFormData: { title: string, description?: string }`

**Completion Criteria**:
- All entities from spec mapped to TypeScript types
- API response types match backend contract assumptions
- Form data types include validation requirements

### 1.2 API Contracts (Assumed Backend)

Create `contracts/api-endpoints.md` documenting assumed REST API:

**Authentication Endpoints**:
- `POST /api/auth/signup` - Create account
  - Request: `{ email, password }`
  - Response: `{ token, user: { id, email } }`
  - Errors: 400 (validation), 409 (email exists)

- `POST /api/auth/login` - Authenticate user
  - Request: `{ email, password }`
  - Response: `{ token, user: { id, email } }`
  - Errors: 400 (validation), 401 (invalid credentials)

**Task Endpoints** (all require `Authorization: Bearer <token>`):
- `GET /api/tasks` - Fetch all user tasks
  - Response: `{ tasks: Task[] }`
  - Errors: 401 (unauthorized)

- `POST /api/tasks` - Create new task
  - Request: `{ title, description? }`
  - Response: `{ task: Task }`
  - Errors: 400 (validation), 401 (unauthorized)

- `PUT /api/tasks/:id` - Update task
  - Request: `{ title?, description?, completed? }`
  - Response: `{ task: Task }`
  - Errors: 400 (validation), 401 (unauthorized), 404 (not found)

- `DELETE /api/tasks/:id` - Delete task
  - Response: 204 No Content
  - Errors: 401 (unauthorized), 404 (not found)

**Completion Criteria**:
- All API endpoints from spec documented
- Request/response formats defined
- Error responses specified
- Authentication requirements noted

### 1.3 Quickstart Guide

Create `quickstart.md` for local development setup:

**Prerequisites**:
- Node.js 18+ installed
- Backend API running (out of scope, assumed available)
- Backend API URL known (e.g., http://localhost:8000)

**Setup Steps**:
1. Install dependencies: `npm install`
2. Copy `.env.example` to `.env.local`
3. Set `NEXT_PUBLIC_API_URL=http://localhost:8000`
4. Run development server: `npm run dev`
5. Access application: `http://localhost:3000`

**Development Workflow**:
1. Signup at `/signup`
2. Login at `/login`
3. Access tasks at `/app/tasks`
4. Create/edit/delete tasks
5. Logout from navbar

**Troubleshooting**:
- 401 errors: Check JWT token storage and backend API availability
- CORS errors: Ensure backend allows frontend origin
- Redirect loops: Verify protected route middleware logic

**Completion Criteria**:
- Local setup steps documented
- Prerequisites listed
- Common issues addressed
- Development workflow clear

---

## Phase 2: Implementation Phases

### Phase 2.0: Environment & Project Setup

**Objective**: Initialize Next.js project, configure TypeScript, Tailwind, and Better Auth, set up project structure.

**Files/Folders**:
- `frontend/package.json` - Dependencies
- `frontend/next.config.js` - Next.js config
- `frontend/tailwind.config.js` - Tailwind config
- `frontend/tsconfig.json` - TypeScript config
- `frontend/.env.local` - Environment variables
- `frontend/src/lib/auth.ts` - Better Auth init

**Dependencies**: None (initial setup)

**Tasks**:
1. Create Next.js app with TypeScript: `npx create-next-app@latest frontend --typescript --tailwind --app`
2. Install Better Auth: `npm install better-auth`
3. Install additional dependencies: `npm install zod clsx tailwind-merge`
4. Configure `NEXT_PUBLIC_API_URL` in `.env.local`
5. Initialize Better Auth configuration in `src/lib/auth.ts`
6. Create base folder structure (`components/`, `types/`, `hooks/`, `lib/`)
7. Configure Tailwind with custom theme (colors, spacing)
8. Set up TypeScript strict mode in `tsconfig.json`

**Completion Criteria**:
- Next.js dev server runs without errors
- Tailwind classes apply correctly
- TypeScript compiles with no errors
- Better Auth imports successfully
- Environment variables accessible

### Phase 2.1: Authentication Foundation (Better Auth)

**Objective**: Implement login, signup, logout functionality with JWT token storage and session management.

**Files/Folders**:
- `src/lib/api-client.ts` - API client base (without auth, initial version)
- `src/lib/auth.ts` - Better Auth config (complete)
- `src/types/user.ts` - User types
- `src/types/api.ts` - Auth API types
- `src/hooks/useAuth.ts` - Auth state hook
- `src/components/auth/LoginForm.tsx` - Login form component
- `src/components/auth/SignupForm.tsx` - Signup form component
- `src/components/ui/Button.tsx` - Reusable button
- `src/components/ui/Input.tsx` - Reusable input
- `src/app/login/page.tsx` - Login page
- `src/app/signup/page.tsx` - Signup page

**Dependencies**: Phase 2.0 complete

**Tasks**:
1. Define User and Auth API types in `types/`
2. Create base API client in `lib/api-client.ts` (fetch wrapper, error handling)
3. Complete Better Auth config with JWT storage strategy
4. Build `useAuth` hook for login, signup, logout, token management
5. Create `Button` and `Input` UI components (Tailwind styled, accessible)
6. Build `LoginForm` with email/password fields, validation, loading state
7. Build `SignupForm` with email/password fields, validation, loading state
8. Implement `/login` page using `LoginForm`, handle successful auth
9. Implement `/signup` page using `SignupForm`, handle successful account creation
10. Test auth flow: signup → login → JWT token stored → redirect

**Completion Criteria**:
- Users can signup and login successfully
- JWT tokens stored in browser (localStorage or cookies)
- Invalid credentials show error messages
- Loading states display during API calls
- Successful auth redirects to `/app/tasks`

### Phase 2.2: Protected Routes & Middleware

**Objective**: Implement protected route middleware, redirect unauthenticated users, handle 401 responses globally.

**Files/Folders**:
- `src/middleware.ts` - Next.js middleware for route protection
- `src/hooks/useAuth.ts` - Update with redirect logic
- `src/lib/api-client.ts` - Update with 401 handling

**Dependencies**: Phase 2.1 complete (auth foundation)

**Tasks**:
1. Create middleware in `src/middleware.ts` to protect `/app/*` routes
2. Check for JWT token in middleware, redirect to `/login` if missing
3. Update `useAuth` hook to provide logout functionality
4. Update API client to intercept 401 responses globally
5. On 401: clear JWT token, redirect to `/login`
6. Test unauthenticated access: direct `/app/tasks` URL → redirect to `/login`
7. Test expired token: mock 401 → logout and redirect

**Completion Criteria**:
- Unauthenticated users cannot access `/app/*` routes
- Direct URL access to protected routes redirects to `/login`
- 401 responses trigger automatic logout and redirect
- Logout button clears token and redirects to `/login`

### Phase 2.3: Layouts & Navigation

**Objective**: Build public layout (auth pages), protected app layout with navbar, implement logout functionality.

**Files/Folders**:
- `src/components/layouts/AuthLayout.tsx` - Public layout
- `src/components/layouts/AppLayout.tsx` - Protected app layout
- `src/components/layouts/Navbar.tsx` - Navigation bar with user info
- `src/app/layout.tsx` - Root layout
- `src/app/app/layout.tsx` - App-specific layout

**Dependencies**: Phase 2.2 complete (protected routes)

**Tasks**:
1. Create `AuthLayout` component: centered form container, no navbar
2. Apply `AuthLayout` to `/login` and `/signup` pages
3. Create `Navbar` component: display user email, logout button
4. Create `AppLayout` component: navbar + main content area
5. Implement logout in `Navbar`: call `useAuth().logout()`, redirect to `/login`
6. Apply `AppLayout` to `/app/*` routes via `/app/layout.tsx`
7. Style layouts with Tailwind: responsive, mobile-first
8. Test navigation: login → see navbar with email → logout → redirect

**Completion Criteria**:
- Auth pages use centered layout without navbar
- Protected pages use app layout with navbar
- Navbar displays authenticated user email
- Logout button works and redirects to `/login`
- Layouts are responsive (mobile, tablet, desktop)

### Phase 2.4: API Client & State Management

**Objective**: Complete API client with JWT auto-attachment, error handling, and establish state management for task data.

**Files/Folders**:
- `src/lib/api-client.ts` - Complete with JWT injection
- `src/hooks/useApi.ts` - Generic API call hook
- `src/hooks/useTasks.ts` - Task data hook
- `src/types/task.ts` - Task types
- `src/types/api.ts` - Task API types

**Dependencies**: Phase 2.3 complete (layouts ready)

**Tasks**:
1. Define Task types in `types/task.ts` (match data-model.md)
2. Define Task API types in `types/api.ts` (request/response shapes)
3. Update API client to automatically attach JWT from Better Auth
4. Implement error handling: 400, 401, 403, 404, 500 with user-friendly messages
5. Create `useApi` hook for generic API calls with loading/error states
6. Create `useTasks` hook: fetch tasks, create, update, delete, toggle
7. Implement optimistic updates for toggle completion
8. Handle API errors gracefully with error messages

**Completion Criteria**:
- API client attaches JWT to all authenticated requests
- `useTasks` hook provides CRUD operations
- Loading states tracked for all API calls
- Error messages user-friendly and actionable
- Optimistic UI updates for toggle completion

### Phase 2.5: Task List View (Read)

**Objective**: Display all user tasks, show loading skeleton, handle empty state, implement delete with confirmation.

**Files/Folders**:
- `src/components/tasks/TaskList.tsx` - Task list container
- `src/components/tasks/TaskCard.tsx` - Individual task card
- `src/components/ui/Modal.tsx` - Reusable modal
- `src/components/ui/Loader.tsx` - Loading skeleton
- `src/app/app/tasks/page.tsx` - Task list page

**Dependencies**: Phase 2.4 complete (API client ready)

**Tasks**:
1. Build `Loader` component: skeleton UI for loading state
2. Build `Modal` component: reusable confirmation dialog
3. Build `TaskCard` component: display title, description, completed status, edit/delete buttons
4. Implement toggle completion in `TaskCard` using `useTasks`
5. Build `TaskList` component: map tasks to `TaskCard`, handle empty state
6. Implement delete with `Modal` confirmation
7. Build `/app/tasks` page: use `TaskList`, show loader while fetching
8. Style task cards with Tailwind: completed tasks have strikethrough, color change
9. Test: login → see tasks → toggle completion → delete task

**Completion Criteria**:
- Task list displays all user tasks
- Loading skeleton shows while fetching
- Empty state displays "Create your first task" message
- Completed tasks visually distinct (strikethrough, color)
- Toggle completion updates immediately (optimistic UI)
- Delete shows confirmation modal and removes task

### Phase 2.6: Task Creation (Create)

**Objective**: Implement new task page with form, validation, loading state, and redirect to task list after creation.

**Files/Folders**:
- `src/components/tasks/TaskForm.tsx` - Reusable task form
- `src/app/app/tasks/new/page.tsx` - New task page

**Dependencies**: Phase 2.5 complete (task list ready)

**Tasks**:
1. Build `TaskForm` component: title input, description textarea, submit/cancel buttons
2. Implement client-side validation: title required, show error if empty
3. Connect form to `useTasks` hook for task creation
4. Show loading state on submit button during API call
5. Display API errors inline on form
6. Redirect to `/app/tasks` after successful creation
7. Implement cancel button: navigate back to `/app/tasks`
8. Build `/app/tasks/new` page using `TaskForm`
9. Add "New Task" button to `/app/tasks` page (top right)
10. Test: click "New Task" → fill form → submit → see new task in list

**Completion Criteria**:
- "New Task" button navigates to `/app/tasks/new`
- Form validates title is not empty
- Loading state shows during submission
- Errors display inline
- Successful creation redirects to task list with new task visible
- Cancel button returns to task list without saving

### Phase 2.7: Task Editing (Update)

**Objective**: Implement edit task page with pre-filled form, validation, and redirect after update.

**Files/Folders**:
- `src/app/app/tasks/[id]/edit/page.tsx` - Edit task page

**Dependencies**: Phase 2.6 complete (task form component ready)

**Tasks**:
1. Build `/app/tasks/[id]/edit` page using `TaskForm` component
2. Fetch task by ID from `useTasks` hook
3. Pre-fill form with existing task title and description
4. Show loading state while fetching task
5. Handle task not found error (404)
6. Implement update logic using `useTasks` hook
7. Redirect to `/app/tasks` after successful update
8. Add "Edit" button to `TaskCard` component
9. Test: click "Edit" → modify task → save → see updated task in list

**Completion Criteria**:
- Edit button navigates to `/app/tasks/[id]/edit`
- Form pre-filled with existing task data
- Validation works (title required)
- Loading state during update
- Successful update redirects to task list
- Cancel returns to task list without saving
- 404 error handled gracefully

### Phase 2.8: UX Enhancements & Responsiveness

**Objective**: Polish UI for mobile/tablet/desktop, add accessibility, improve loading states, refine empty states.

**Files/Folders**:
- All components (refinement)
- `src/lib/utils.ts` - Utility functions (cn, formatDate)

**Dependencies**: Phase 2.7 complete (all core features implemented)

**Tasks**:
1. Test all pages on mobile (320px), tablet (768px), desktop (1024px+)
2. Refine Tailwind responsive classes: mobile-first approach
3. Add keyboard navigation: tab order, enter to submit forms
4. Add aria-labels to icon buttons (edit, delete, toggle)
5. Ensure form labels associated with inputs for screen readers
6. Add focus states to all interactive elements
7. Improve loading skeletons with animation
8. Refine empty state with helpful message and "Create Task" CTA
9. Add date formatting utility for task timestamps
10. Truncate long task descriptions with "..." and show full text on hover/click

**Completion Criteria**:
- Application fully functional on 320px+ screens
- All interactive elements keyboard accessible
- Buttons have descriptive aria-labels
- Form inputs have associated labels
- Loading states clear and animated
- Empty state helpful and actionable
- Long text truncated gracefully

### Phase 2.9: Error Handling & Edge Cases

**Objective**: Handle all edge cases from spec, including network failures, concurrent operations, invalid tokens, rapid interactions.

**Files/Folders**:
- `src/lib/api-client.ts` - Enhanced error handling
- `src/hooks/useTasks.ts` - Debouncing, retry logic
- All components - Edge case handling

**Dependencies**: Phase 2.8 complete (UX polished)

**Tasks**:
1. Implement network error handling: show "Network error, please try again"
2. Add retry mechanism for failed API calls (user-initiated)
3. Handle concurrent task deletion: if task not found on edit/toggle, show error
4. Implement debouncing for rapid toggle clicks (prevent race conditions)
5. Handle browser back button during form submission: cancel request
6. Test expired JWT token: automatic logout and redirect
7. Test invalid credentials: show clear error message
8. Test form validation errors: display inline
9. Test task not found (404): show error message
10. Document all edge cases in code comments

**Completion Criteria**:
- Network failures show clear error messages
- Users can retry failed operations
- Concurrent operations handled gracefully
- Rapid interactions debounced appropriately
- Browser navigation doesn't cause issues
- All edge cases from spec tested and handled

### Phase 2.10: Final Frontend Validation

**Objective**: End-to-end testing of all user stories, validate against spec success criteria, document any deviations.

**Files/Folders**:
- `specs/001-frontend-ui/validation-report.md` - Test results
- All implemented code - Final review

**Dependencies**: Phase 2.9 complete (all features and edge cases implemented)

**Tasks**:
1. Test User Story 1 (Authentication): signup, login, logout, session persistence
2. Test User Story 2 (Task List): view tasks, toggle completion, delete tasks, empty state
3. Test User Story 3 (Create Task): new task flow, validation, success, cancel
4. Test User Story 4 (Edit Task): edit flow, pre-fill, validation, success, cancel
5. Validate Success Criteria SC-001 to SC-010 from spec
6. Test all 40 Functional Requirements from spec
7. Test all 7 Edge Cases from spec
8. Document any deviations or limitations discovered
9. Create validation report with pass/fail for each criterion
10. Address any critical issues found

**Completion Criteria**:
- All user stories pass acceptance scenarios
- All success criteria validated
- All functional requirements met
- All edge cases handled
- Validation report complete
- Critical issues resolved or documented

---

## Phase 3: Documentation Updates

**Objective**: Update quickstart guide, document deployment steps, finalize all planning artifacts.

**Files/Folders**:
- `specs/001-frontend-ui/quickstart.md` - Updated with final setup
- `specs/001-frontend-ui/deployment.md` - Deployment guide
- `specs/001-frontend-ui/validation-report.md` - Testing results
- `README.md` (frontend root) - Project overview

**Dependencies**: Phase 2.10 complete (all implementation and validation done)

**Tasks**:
1. Update `quickstart.md` with any setup changes discovered during implementation
2. Create `deployment.md`: build steps, environment variables, Vercel deployment
3. Finalize `validation-report.md` with test results
4. Create frontend `README.md`: project overview, tech stack, folder structure
5. Document known limitations or future enhancements
6. Archive any temporary research notes

**Completion Criteria**:
- Quickstart guide accurate and complete
- Deployment instructions documented
- Validation report finalized
- README provides clear project overview
- All documentation up to date

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 0 (Research)**: No dependencies - start immediately after constitution check passes
- **Phase 1 (Design)**: Depends on Phase 0 completion
- **Phase 2.0 (Setup)**: Depends on Phase 1 completion
- **Phase 2.1 (Auth)**: Depends on Phase 2.0
- **Phase 2.2 (Protected Routes)**: Depends on Phase 2.1
- **Phase 2.3 (Layouts)**: Depends on Phase 2.2
- **Phase 2.4 (API Client)**: Depends on Phase 2.3
- **Phase 2.5 (Task List)**: Depends on Phase 2.4
- **Phase 2.6 (Task Create)**: Depends on Phase 2.5
- **Phase 2.7 (Task Edit)**: Depends on Phase 2.6
- **Phase 2.8 (UX)**: Depends on Phase 2.7
- **Phase 2.9 (Edge Cases)**: Depends on Phase 2.8
- **Phase 2.10 (Validation)**: Depends on Phase 2.9
- **Phase 3 (Docs)**: Depends on Phase 2.10

### Critical Path

1. **Foundation** (Phases 0, 1, 2.0): Cannot proceed without research, design, and project setup
2. **Authentication** (Phases 2.1, 2.2, 2.3): MUST be complete before any task features
3. **API Layer** (Phase 2.4): MUST be complete before task CRUD operations
4. **Task Features** (Phases 2.5, 2.6, 2.7): Sequential - list before create before edit
5. **Polish** (Phases 2.8, 2.9, 2.10): After all core features

### Parallel Opportunities

- Phase 0: All research tasks can be conducted in parallel
- Phase 2.5: TaskCard, TaskList, Loader components can be built in parallel
- Phase 2.8: Responsiveness testing for multiple pages can be done in parallel

---

## Success Criteria (Phase-Specific Validation)

### Phase 0 Success
- [ ] Better Auth integration pattern documented
- [ ] Protected route strategy defined
- [ ] API client architecture confirmed
- [ ] State management approach selected

### Phase 1 Success
- [ ] All TypeScript types defined
- [ ] API contracts documented
- [ ] Quickstart guide created

### Phase 2.1 Success (Auth)
- [ ] Users can signup and login
- [ ] JWT tokens stored securely
- [ ] Invalid credentials show errors

### Phase 2.2 Success (Protected Routes)
- [ ] Unauthenticated users redirected to /login
- [ ] 401 responses trigger logout

### Phase 2.3 Success (Layouts)
- [ ] Auth pages use public layout
- [ ] App pages use protected layout with navbar
- [ ] Logout button works

### Phase 2.4 Success (API Client)
- [ ] JWT automatically attached to requests
- [ ] Error handling user-friendly

### Phase 2.5 Success (Task List)
- [ ] Tasks display correctly
- [ ] Toggle completion works
- [ ] Delete with confirmation works
- [ ] Empty state shows

### Phase 2.6 Success (Task Create)
- [ ] New task form validates
- [ ] Task creation succeeds
- [ ] Redirects to task list after creation

### Phase 2.7 Success (Task Edit)
- [ ] Edit form pre-fills correctly
- [ ] Task update succeeds
- [ ] Redirects to task list after update

### Phase 2.8 Success (UX)
- [ ] Responsive on all screen sizes
- [ ] Keyboard accessible
- [ ] Aria-labels present

### Phase 2.9 Success (Edge Cases)
- [ ] Network errors handled
- [ ] Concurrent operations safe
- [ ] All edge cases from spec addressed

### Phase 2.10 Success (Validation)
- [ ] All user stories pass
- [ ] All success criteria met
- [ ] Validation report complete

---

## Notes

- **Frontend-Only Scope**: This plan covers ONLY frontend implementation. Backend API is assumed to exist and is explicitly out of scope.
- **Better Auth Configuration**: Specific Better Auth setup will be determined in Phase 0 research based on latest documentation.
- **No Code in Plan**: This document contains no code snippets per requirements. Implementation details will be in task breakdown.
- **Constitution Compliance**: All phases adhere to constitution principles, especially frontend-only scope and JWT authentication patterns.
- **Success Criteria Traceability**: Each phase has explicit success criteria that map to spec requirements (40 FRs, 10 SCs, 7 edge cases).
