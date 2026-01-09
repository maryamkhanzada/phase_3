# Research: Frontend UI Technology Validation

**Feature**: Frontend UI for Todo Application
**Date**: 2026-01-07
**Status**: Complete

## Overview

This document consolidates research findings for frontend technology choices, resolving all NEEDS CLARIFICATION items from the Technical Context and establishing implementation patterns for Next.js 15+ App Router, Better Auth, API client architecture, state management, and Tailwind CSS configuration.

---

## 1. Better Auth Integration Research

### Decision: Use localStorage for JWT token storage with Better Auth

**Rationale**:
- Better Auth provides flexible token storage options (localStorage, cookies, session storage)
- localStorage chosen for simplicity in Phase II (httpOnly cookies require additional backend coordination out of scope)
- Tokens automatically included in Better Auth context, accessible via hooks
- Session persistence across page refreshes handled automatically by Better Auth

**Alternatives Considered**:
- **httpOnly cookies**: More secure but requires backend cookie management (out of frontend scope)
- **sessionStorage**: Less persistent (cleared on tab close), worse UX for users
- **localStorage**: Best balance of persistence, simplicity, and frontend-only control

**Implementation Pattern**:
```
// lib/auth.ts - Better Auth initialization
import { createAuth } from 'better-auth'

export const auth = createAuth({
  storage: 'localStorage',
  tokenKey: 'todo_jwt_token',
  baseURL: process.env.NEXT_PUBLIC_API_URL
})

// hooks/useAuth.ts - Auth hook
export function useAuth() {
  const { token, user, login, signup, logout } = auth.useSession()
  return { token, user, login, signup, logout }
}
```

**JWT Token Extraction**: Token retrieved via `auth.getToken()` or from `useSession()` hook, automatically managed by Better Auth.

**Session Persistence Strategy**: Better Auth checks localStorage on mount, restores session if valid token exists. Expired tokens auto-refresh if backend supports refresh tokens (assumed).

---

## 2. Next.js App Router Protected Routes

### Decision: Use Next.js middleware for route protection with JWT validation

**Rationale**:
- Next.js 13+ middleware runs before page rendering, ideal for auth checks
- Middleware can access request context and redirect before component render
- Better performance than client-side redirect (no flash of protected content)
- Centralized auth logic in single middleware file

**Alternatives Considered**:
- **Client-side protection in layouts**: Slower, shows protected content before redirect
- **Server Component checks**: More granular but requires per-page implementation
- **Middleware**: Best for global route protection with centralized logic (chosen)

**Implementation Pattern**:
```
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('todo_jwt_token') ||
                request.headers.get('authorization')?.replace('Bearer ', '')

  if (request.nextUrl.pathname.startsWith('/app')) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/app/:path*']
}
```

**Redirect Patterns**: Middleware redirects to `/login` for unauthenticated users. After successful auth, redirect to `/app/tasks` (stored in login handler).

**Loading States**: Middleware runs synchronously, no loading state needed. Client components show loading during auth operations.

**Server Component vs Client Component**:
- **Server Components**: Default for pages, layouts. Use for static content, non-interactive UI.
- **Client Components**: Use for forms, auth state access, task interactions. Mark with `'use client'`.

---

## 3. API Client Architecture

### Decision: Custom fetch wrapper with JWT injection and centralized error handling

**Rationale**:
- fetch API native to browsers, no additional dependencies
- Wrapper pattern allows JWT auto-injection and global error handling
- Environment variable for API base URL enables flexibility across environments
- Retry logic and network error handling centralized in one place

**Alternatives Considered**:
- **Axios**: Additional dependency, unnecessary for simple REST API
- **React Query / SWR**: Adds caching/state management complexity beyond Phase II needs
- **fetch wrapper**: Simple, flexible, sufficient for current requirements (chosen)

**Implementation Pattern**:
```
// lib/api-client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function apiClient(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('todo_jwt_token')

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  })

  if (response.status === 401) {
    localStorage.removeItem('todo_jwt_token')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Request failed')
  }

  return response.status === 204 ? null : response.json()
}
```

**Error Handling**:
- **401 Unauthorized**: Clear token, redirect to /login
- **403 Forbidden**: Show "Access denied" message
- **404 Not Found**: Show "Resource not found" message
- **500 Server Error**: Show "Server error, please try again"
- **Network errors**: Show "Network error, check connection"

**Retry Logic**: User-initiated retry only (button in error state), no automatic retries to avoid overwhelming backend.

**Environment Variable**: `NEXT_PUBLIC_API_URL` set in `.env.local`, defaults to `http://localhost:8000` for development.

---

## 4. State Management Strategy

### Decision: React hooks with component state (no global state library)

**Rationale**:
- Todo app has simple state needs: auth session, task list
- React hooks (useState, useEffect) sufficient for local component state
- Custom hooks (useAuth, useTasks) encapsulate logic without global state complexity
- Server Components handle data fetching, Client Components manage interactions
- Avoids over-engineering for Phase II scope

**Alternatives Considered**:
- **React Context**: Adds complexity, unnecessary for non-deeply-nested components
- **Zustand**: Lightweight state library, but overkill for current needs
- **Redux**: Too heavy, unnecessary complexity for simple CRUD app
- **Component state + hooks**: Simplest, sufficient for current scope (chosen)

**Data Fetching Patterns**:
- **Server Components**: Fetch task data server-side where possible (initial render)
- **Client hooks**: Fetch on client for dynamic updates (create, update, delete, toggle)
- **useEffect** with dependency arrays for re-fetching on state changes

**Cache Invalidation Strategy**:
- **Optimistic updates**: Toggle completion updates UI immediately, reverts on error
- **Refetch after mutations**: Create/update/delete triggers task list refetch
- **No persistent cache**: Fresh fetch on page navigation (simple, correct)

**Form State Management**:
- Controlled inputs with useState for form fields (title, description)
- Validation state tracked separately (errors object)
- Submit disabled during loading (prevents double-submit)

---

## 5. Tailwind CSS Setup

### Decision: Tailwind CSS 3+ with mobile-first responsive design and custom theme

**Rationale**:
- Tailwind comes pre-configured with create-next-app
- Utility-first approach speeds development, reduces custom CSS
- Mobile-first responsive design aligns with spec requirements (320px+)
- Custom theme for brand colors, spacing ensures consistency

**Alternatives Considered**:
- **CSS Modules**: More verbose, slower development
- **Styled Components / Emotion**: Runtime overhead, unnecessary for static styles
- **Tailwind CSS**: Fastest development, best DX, zero runtime cost (chosen)

**Implementation Pattern**:
```
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981',
        danger: '#EF4444',
      },
      spacing: {
        '128': '32rem',
      },
    },
  },
  plugins: [],
}
```

**Component Styling Patterns**:
- Use `clsx` utility for conditional classes: `clsx('btn', isLoading && 'btn-loading')`
- Use `tailwind-merge` to avoid class conflicts: `twMerge('px-4 px-2')` → `px-2`
- Combined utility: `cn(...classes)` = `twMerge(clsx(...classes))`

**Accessibility Utilities**:
- Focus states: `focus:ring-2 focus:ring-primary focus:outline-none`
- Aria attributes: Use native HTML attributes, not Tailwind classes
- Screen reader only: `sr-only` class for visually hidden but accessible text

**Color Scheme**:
- **Primary**: Blue (#3B82F6) - buttons, links, active states
- **Secondary**: Green (#10B981) - success messages, completed tasks
- **Danger**: Red (#EF4444) - delete buttons, error messages
- **Gray scale**: Tailwind default grays for text, backgrounds, borders

**Spacing Conventions**:
- Use Tailwind's default spacing scale (4px increments)
- Consistent padding: `p-4` for cards, `p-6` for sections
- Consistent margins: `mb-4` between elements, `mb-6` between sections

---

## Summary of Decisions

| Topic | Decision | Rationale |
|-------|----------|-----------|
| JWT Storage | localStorage with Better Auth | Simple, persistent, frontend-controlled |
| Protected Routes | Next.js middleware | Centralized, performant, before render |
| API Client | Custom fetch wrapper | Native, simple, sufficient |
| State Management | React hooks + component state | Simple, sufficient for Phase II scope |
| Styling | Tailwind CSS 3+ | Fast development, mobile-first, zero runtime |
| Auth Library | Better Auth | JWT-focused, Next.js compatible |
| Validation | Zod schemas | Type-safe, Next.js ecosystem standard |

---

## Implementation Readiness

All NEEDS CLARIFICATION items from Technical Context resolved:
- ✅ Language/Version: TypeScript 5.x with Next.js 15+
- ✅ Primary Dependencies: Next.js, React 18+, Better Auth, Tailwind CSS, Zod
- ✅ Storage: localStorage for JWT tokens
- ✅ Testing: Jest + React Testing Library (optional), Playwright for E2E (optional)
- ✅ Target Platform: Web browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
- ✅ Performance Goals: FCP < 1.5s, task operations < 300ms, 100 tasks render < 2s
- ✅ Constraints: Mobile-first (320px+), keyboard accessible, JWT auth only
- ✅ Scale/Scope: 5 routes, ~10 components, <100 tasks per user

**Ready to proceed to Phase 1: Design Artifacts**
