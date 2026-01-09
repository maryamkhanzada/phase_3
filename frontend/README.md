# Todo Application - Frontend

A modern, responsive todo application built with Next.js 15, TypeScript, and Tailwind CSS.

## Features

- 🔐 **Authentication**: JWT-based signup, login, and session management
- ✅ **Task Management**: Create, read, update, delete, and toggle completion
- 📱 **Responsive Design**: Mobile-first design (320px+)
- ⚡ **Performance**: Optimistic UI updates for instant feedback
- 🎨 **Modern UI**: Clean interface with Tailwind CSS v4
- ♿ **Accessible**: Keyboard navigation and ARIA labels

## Quick Start

### Prerequisites

- Node.js 18+
- Backend API running (default: http://localhost:8000)

### Installation

```bash
# Install dependencies
npm install

# Configure environment variables
# Create .env.local file with:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# BETTER_AUTH_SECRET=your-secret-key-here

# Start development server
npm run dev
```

Visit `http://localhost:3000` to see the application.

## Technology Stack

- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript 5.x with strict mode
- **Styling**: Tailwind CSS v4
- **State Management**: React Hooks
- **Authentication**: localStorage JWT tokens
- **API Client**: Custom fetch wrapper

## Documentation

For detailed documentation, see `../specs/001-frontend-ui/`:

- **Quick Start Guide**: `quickstart.md`
- **Implementation Plan**: `plan.md`
- **API Contracts**: `contracts/api-endpoints.md`
- **Deployment Guide**: `deployment.md`
- **Validation Report**: `validation-report.md`

## Features Implemented

✅ User Authentication (signup, login, logout)
✅ Protected Routes (middleware-based)
✅ Task List View (with loading and empty states)
✅ Task Creation (with validation)
✅ Task Editing (with pre-fill)
✅ Task Deletion (with confirmation)
✅ Task Completion Toggle (optimistic UI)
✅ Responsive Design (mobile-first)
✅ Error Handling (network errors, 401, 404)
✅ Accessibility (keyboard navigation, ARIA labels)

## License

MIT
