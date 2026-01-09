---
description: "Task list for Frontend UI implementation"
---

# Tasks: Frontend UI for Todo Application

**Input**: Design documents from `/specs/001-frontend-ui/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/api-endpoints.md, research.md

**Tests**: Tests are NOT requested in the specification. Implementation follows production code pattern without TDD.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend root**: `frontend/` (new directory to be created)
- All source files under `frontend/src/`
- Next.js App Router pages in `frontend/src/app/`
- Components in `frontend/src/components/`
- Utilities in `frontend/src/lib/`, `frontend/src/hooks/`, `frontend/src/types/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create Next.js application with TypeScript in frontend/ directory using create-next-app --typescript --tailwind --app
- [ ] T002 Install Better Auth dependency in frontend/: npm install better-auth
- [ ] T003 [P] Install additional dependencies in frontend/: npm install zod clsx tailwind-merge
- [ ] T004 [P] Configure environment variables in frontend/.env.local (NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET)
- [ ] T005 [P] Configure Tailwind CSS custom theme in frontend/tailwind.config.js (colors, spacing)
- [ ] T006 [P] Set up TypeScript strict mode in frontend/tsconfig.json
- [ ] T007 Create base folder structure: frontend/src/components/, frontend/src/lib/, frontend/src/hooks/, frontend/src/types/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Define User type in frontend/src/types/user.ts
- [ ] T009 [P] Define Task type in frontend/src/types/task.ts
- [ ] T010 [P] Define API response types in frontend/src/types/api.ts (AuthResponse, TaskResponse, ErrorResponse, LoadingState)
- [ ] T011 Create base API client in frontend/src/lib/api-client.ts with fetch wrapper and error handling
- [ ] T012 Initialize Better Auth configuration in frontend/src/lib/auth.ts with localStorage storage
- [ ] T013 Create utility functions in frontend/src/lib/utils.ts (cn for className merging, formatDate)
- [ ] T014 [P] Create Button component in frontend/src/components/ui/Button.tsx with Tailwind styling and accessibility
- [ ] T015 [P] Create Input component in frontend/src/components/ui/Input.tsx with label and error state support
- [ ] T016 [P] Create Loader skeleton component in frontend/src/components/ui/Loader.tsx for loading states
- [ ] T017 [P] Create Modal component in frontend/src/components/ui/Modal.tsx for confirmation dialogs
- [ ] T018 Create root layout in frontend/src/app/layout.tsx with Tailwind CSS globals import
- [ ] T019 Create landing page in frontend/src/app/page.tsx with redirect logic to /login or /app/tasks

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication and Session Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to sign up, log in, maintain session, and log out with JWT-based authentication

**Independent Test**: Complete signup flow, login with credentials, verify session persists on refresh, logout and verify redirect, attempt to access /app/tasks without auth and verify redirect to /login

### Implementation for User Story 1

- [ ] T020 [P] [US1] Create useAuth hook in frontend/src/hooks/useAuth.ts for login, signup, logout, token management
- [ ] T021 [P] [US1] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx with email/password fields, validation, loading state
- [ ] T022 [P] [US1] Create SignupForm component in frontend/src/components/auth/SignupForm.tsx with email/password fields, validation, loading state
- [ ] T023 [US1] Create login page in frontend/src/app/login/page.tsx using LoginForm component
- [ ] T024 [US1] Create signup page in frontend/src/app/signup/page.tsx using SignupForm component
- [ ] T025 [US1] Update API client in frontend/src/lib/api-client.ts to automatically attach JWT token from localStorage to authenticated requests
- [ ] T026 [US1] Create Next.js middleware in frontend/src/middleware.ts to protect /app/* routes and redirect unauthenticated users to /login
- [ ] T027 [US1] Update API client in frontend/src/lib/api-client.ts to handle 401 responses by clearing token and redirecting to /login
- [ ] T028 [P] [US1] Create AuthLayout component in frontend/src/components/layouts/AuthLayout.tsx for centered form layout without navbar
- [ ] T029 [P] [US1] Create Navbar component in frontend/src/components/layouts/Navbar.tsx with user email display and logout button
- [ ] T030 [P] [US1] Create AppLayout component in frontend/src/components/layouts/AppLayout.tsx with Navbar and main content area
- [ ] T031 [US1] Apply AuthLayout to login and signup pages
- [ ] T032 [US1] Create app-specific layout in frontend/src/app/app/layout.tsx using AppLayout component for protected routes
- [ ] T033 [US1] Implement logout functionality in Navbar component calling useAuth().logout() and redirecting to /login

**Checkpoint**: At this point, User Story 1 should be fully functional - users can signup, login, stay logged in across refreshes, and logout

---

## Phase 4: User Story 2 - View and Manage Personal Task List (Priority: P2)

**Goal**: Display all user tasks, allow toggle completion, delete tasks, show loading/empty states

**Independent Test**: Login, view task list, toggle task completion and verify it persists, delete task with confirmation modal, verify empty state shows for users with no tasks, verify loading skeleton displays during fetch

### Implementation for User Story 2

- [ ] T034 [P] [US2] Create useApi hook in frontend/src/hooks/useApi.ts for generic API calls with loading/error state tracking
- [ ] T035 [US2] Create useTasks hook in frontend/src/hooks/useTasks.ts with fetchTasks, createTask, updateTask, deleteTask, toggleCompletion functions
- [ ] T036 [P] [US2] Create TaskCard component in frontend/src/components/tasks/TaskCard.tsx displaying title, description, completed status, edit/delete buttons, toggle control
- [ ] T037 [P] [US2] Create TaskList component in frontend/src/components/tasks/TaskList.tsx mapping tasks to TaskCard components and handling empty state
- [ ] T038 [US2] Implement toggle completion in TaskCard using useTasks hook with optimistic UI update
- [ ] T039 [US2] Implement delete functionality in TaskCard with Modal confirmation using useTasks hook
- [ ] T040 [US2] Create task list page in frontend/src/app/app/tasks/page.tsx using TaskList component and Loader for fetching state
- [ ] T041 [US2] Style TaskCard component with Tailwind: completed tasks with strikethrough and color change, truncate long descriptions with ellipsis
- [ ] T042 [US2] Add error handling to task list page for failed fetch with user-friendly error message

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can view, toggle, and delete tasks

---

## Phase 5: User Story 3 - Create New Tasks (Priority: P3)

**Goal**: Enable users to create new tasks with title and optional description

**Independent Test**: Navigate to /app/tasks/new, fill form with title and description, submit and verify redirect to /app/tasks with new task visible, test validation error when title is empty, test cancel button returns to task list

### Implementation for User Story 3

- [ ] T043 [US3] Create TaskForm component in frontend/src/components/tasks/TaskForm.tsx with title input, description textarea, submit/cancel buttons, validation
- [ ] T044 [US3] Implement client-side validation in TaskForm: title required, inline error display
- [ ] T045 [US3] Connect TaskForm to useTasks hook for task creation with loading state on submit button
- [ ] T046 [US3] Add redirect to /app/tasks after successful task creation in TaskForm
- [ ] T047 [US3] Implement cancel button in TaskForm to navigate back to /app/tasks without saving
- [ ] T048 [US3] Create new task page in frontend/src/app/app/tasks/new/page.tsx using TaskForm component
- [ ] T049 [US3] Add "New Task" button to task list page (frontend/src/app/app/tasks/page.tsx) navigating to /app/tasks/new
- [ ] T050 [US3] Add API error handling in TaskForm with inline error message display

**Checkpoint**: All user stories 1, 2, AND 3 should now be independently functional - users can create tasks

---

## Phase 6: User Story 4 - Edit Existing Tasks (Priority: P4)

**Goal**: Enable users to update task title and description

**Independent Test**: Click Edit on a task, verify form pre-fills with existing data, modify title/description, save and verify changes persist, test validation error when clearing title, test cancel returns to task list without saving

### Implementation for User Story 4

- [ ] T051 [US4] Update useTasks hook in frontend/src/hooks/useTasks.ts to add fetchTaskById function
- [ ] T052 [US4] Create edit task page in frontend/src/app/app/tasks/[id]/edit/page.tsx using TaskForm component
- [ ] T053 [US4] Fetch task by ID in edit page and pre-fill TaskForm with existing title and description
- [ ] T054 [US4] Show loading state in edit page while fetching task data
- [ ] T055 [US4] Handle task not found error (404) in edit page with user-friendly message
- [ ] T056 [US4] Implement update logic in TaskForm when in edit mode using useTasks hook
- [ ] T057 [US4] Redirect to /app/tasks after successful task update in TaskForm
- [ ] T058 [US4] Add "Edit" button to TaskCard component (frontend/src/components/tasks/TaskCard.tsx) navigating to /app/tasks/[id]/edit
- [ ] T059 [US4] Ensure TaskForm validation works in edit mode (title required)

**Checkpoint**: All user stories should now be independently functional - complete CRUD operations available

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T060 [P] Test all pages on mobile (320px), tablet (768px), desktop (1024px+) and refine responsive Tailwind classes
- [ ] T061 [P] Add keyboard navigation support: tab order correct, enter to submit forms
- [ ] T062 [P] Add aria-labels to icon buttons (edit, delete, toggle) for accessibility
- [ ] T063 [P] Ensure form inputs have associated labels for screen reader accessibility
- [ ] T064 [P] Add focus states to all interactive elements using Tailwind focus utilities
- [ ] T065 Improve loading skeleton animations in Loader component
- [ ] T066 Refine empty state in TaskList with helpful message and "Create Task" call-to-action
- [ ] T067 Truncate long task descriptions in TaskCard with "..." and show full text on hover or expand
- [ ] T068 Implement debouncing for rapid toggle clicks in TaskCard to prevent race conditions
- [ ] T069 Handle network errors in API client with user-friendly "Network error, please try again" messages
- [ ] T070 Add retry mechanism for failed API calls (user-initiated retry button in error states)
- [ ] T071 Handle concurrent task deletion: show error if task not found on edit/toggle operations
- [ ] T072 Handle browser back button during form submission: cancel pending requests
- [ ] T073 Test expired JWT token scenario: verify automatic logout and redirect to /login
- [ ] T074 Test all edge cases from spec: invalid JWT, network failures, concurrent operations, empty list, long text, rapid toggling, browser navigation
- [ ] T075 Validate all 40 Functional Requirements from spec are met
- [ ] T076 Validate all 10 Success Criteria from spec are met
- [ ] T077 Test all User Story acceptance scenarios end-to-end
- [ ] T078 Create validation report documenting test results in specs/001-frontend-ui/validation-report.md
- [ ] T079 [P] Update quickstart.md in specs/001-frontend-ui/ with any setup changes discovered during implementation
- [ ] T080 [P] Create deployment guide in specs/001-frontend-ui/deployment.md with build steps and Vercel instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion - BLOCKS all user stories
- **Phase 3 (User Story 1 - Auth)**: Depends on Phase 2 completion - Can start immediately after foundation
- **Phase 4 (User Story 2 - View/Manage Tasks)**: Depends on Phase 2 AND Phase 3 completion (needs auth)
- **Phase 5 (User Story 3 - Create Tasks)**: Depends on Phase 2 AND Phase 3 completion (needs auth, can run parallel with Phase 4)
- **Phase 6 (User Story 4 - Edit Tasks)**: Depends on Phase 2, 3, AND 5 completion (reuses TaskForm from Phase 5)
- **Phase 7 (Polish)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Auth)**: No dependencies on other stories, depends only on Foundational phase
- **User Story 2 (P2 - View/Manage)**: Depends on US1 (auth required), independent of US3/US4
- **User Story 3 (P3 - Create)**: Depends on US1 (auth required), independent of US2/US4
- **User Story 4 (P4 - Edit)**: Depends on US1 (auth required) and US3 (reuses TaskForm), independent of US2

### Within Each User Story

- Foundation tasks (types, hooks, components) can run in parallel
- Pages depend on their components
- Integration tasks depend on both components and hooks

### Parallel Opportunities

**Phase 1 - Setup (all can run in parallel after T001)**:
- T002, T003, T004, T005, T006 can all run in parallel

**Phase 2 - Foundational (groups can run in parallel)**:
- Types: T008, T009, T010 can run in parallel
- UI Components: T014, T015, T016, T017 can run in parallel

**Phase 3 - User Story 1 (groups can run in parallel)**:
- T020 (useAuth hook), T021 (LoginForm), T022 (SignupForm) can run in parallel
- T028 (AuthLayout), T029 (Navbar), T030 (AppLayout) can run in parallel

**Phase 4 - User Story 2 (components can build in parallel)**:
- T034 (useApi hook), T036 (TaskCard), T037 (TaskList) can run in parallel

**Phase 5 - User Story 3**:
- Mostly sequential due to TaskForm reuse

**Phase 6 - User Story 4**:
- Mostly sequential, builds on TaskForm from US3

**Phase 7 - Polish (many can run in parallel)**:
- T060, T061, T062, T063, T064 (accessibility and responsive) can run in parallel
- T079, T080 (documentation) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch foundational components in parallel:
Task T020: "Create useAuth hook in frontend/src/hooks/useAuth.ts"
Task T021: "Create LoginForm in frontend/src/components/auth/LoginForm.tsx"
Task T022: "Create SignupForm in frontend/src/components/auth/SignupForm.tsx"

# Then launch layout components in parallel:
Task T028: "Create AuthLayout in frontend/src/components/layouts/AuthLayout.tsx"
Task T029: "Create Navbar in frontend/src/components/layouts/Navbar.tsx"
Task T030: "Create AppLayout in frontend/src/components/layouts/AppLayout.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. **STOP and VALIDATE**: Test authentication flow end-to-end
5. Deploy/demo authentication if ready

**At this point you have a working authentication system - this is the minimum viable product.**

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Auth) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (View/Manage) → Test independently → Deploy/Demo (Core value!)
4. Add User Story 3 (Create) → Test independently → Deploy/Demo
5. Add User Story 4 (Edit) → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Auth) - **CRITICAL PATH**
3. After US1 complete:
   - Developer A: User Story 2 (View/Manage)
   - Developer B: User Story 3 (Create) - can run parallel with US2
4. After US3 complete:
   - Developer C: User Story 4 (Edit) - depends on US3's TaskForm
5. Stories complete and integrate independently

**Note**: US1 (Auth) is on the critical path and must complete before any other user stories.

---

## Notes

- **Frontend-Only Scope**: All tasks are frontend implementation only. Backend API assumed to exist.
- **No Tests Requested**: Spec does not request TDD or test implementation. Tasks focus on production code.
- **[P] tasks**: Different files, no dependencies on incomplete tasks
- **[Story] label**: Maps task to specific user story for traceability (US1, US2, US3, US4)
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Task IDs**: Sequential T001-T080 in execution dependency order
- **File paths**: All paths are absolute from frontend/ root directory
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

**Total Tasks**: 80
- **Phase 1 (Setup)**: 7 tasks
- **Phase 2 (Foundational)**: 12 tasks (BLOCKS all user stories)
- **Phase 3 (US1 - Auth)**: 14 tasks
- **Phase 4 (US2 - View/Manage)**: 9 tasks
- **Phase 5 (US3 - Create)**: 8 tasks
- **Phase 6 (US4 - Edit)**: 9 tasks
- **Phase 7 (Polish)**: 21 tasks

**Parallel Opportunities**: 25 tasks marked [P] for parallel execution

**Independent Test Criteria**:
- **US1**: Signup, login, session persistence, logout, protected route redirect
- **US2**: View tasks, toggle completion, delete with confirmation, empty state, loading state
- **US3**: Create task form, validation, submit with redirect, cancel
- **US4**: Edit form pre-fill, update with redirect, validation, cancel, 404 handling

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (US1 Auth) = 33 tasks
