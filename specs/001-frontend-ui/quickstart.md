# Quickstart Guide: Frontend Todo Application

**Feature**: Frontend UI for Todo Application
**Date**: 2026-01-07
**Status**: Ready for implementation

## Overview

This guide provides step-by-step instructions to set up the frontend Todo application locally for development and testing.

---

## Prerequisites

Before you begin, ensure you have the following installed and configured:

### Required Software

- **Node.js 18+**: Download from [nodejs.org](https://nodejs.org/)
  - Verify installation: `node --version` (should show v18.x.x or higher)
  - npm comes bundled with Node.js

- **Git**: For version control
  - Verify installation: `git --version`

### Required Services

- **Backend REST API**: The backend API must be running and accessible
  - Default backend URL: `http://localhost:8000`
  - Backend provides authentication and task management endpoints
  - See `contracts/api-endpoints.md` for API contract details
  - **Note**: Backend implementation is out of scope for this frontend project

### Optional Tools

- **VS Code**: Recommended editor with TypeScript and Tailwind CSS extensions
- **Postman** or **curl**: For testing API endpoints independently

---

## Setup Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd frontend_todo_app
```

### 2. Navigate to Frontend Directory

```bash
cd frontend
```

If the frontend directory doesn't exist yet, it will be created during implementation Phase 2.0.

### 3. Install Dependencies

```bash
npm install
```

This installs:
- Next.js 15+
- React 18+
- TypeScript
- Tailwind CSS
- Better Auth
- Zod
- Additional utilities (clsx, tailwind-merge)

### 4. Configure Environment Variables

Create a `.env.local` file in the frontend root directory:

```bash
cp .env.example .env.local
```

If `.env.example` doesn't exist, create `.env.local` manually with:

```env
# Backend API base URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth configuration
BETTER_AUTH_SECRET=your-secret-key-here-change-in-production
```

**Important**:
- `NEXT_PUBLIC_API_URL`: URL where your backend API is running
  - Development: `http://localhost:8000`
  - Production: Your deployed backend URL
- `BETTER_AUTH_SECRET`: Shared secret for JWT verification (must match backend)
  - Use a strong random string in production
  - Never commit real secrets to version control

### 5. Start Development Server

```bash
npm run dev
```

The application will be available at: **http://localhost:3000**

---

## Development Workflow

### First Time User Flow

1. **Access the application**: Navigate to `http://localhost:3000`

2. **Sign up for an account**:
   - Click "Sign up" or navigate to `/signup`
   - Enter email and password (min 8 characters)
   - Click "Create Account"
   - You'll be redirected to `/app/tasks` after successful signup

3. **Log in (returning users)**:
   - Navigate to `/login`
   - Enter your email and password
   - Click "Log In"
   - You'll be redirected to `/app/tasks`

4. **Manage tasks**:
   - **View tasks**: Automatically shown on `/app/tasks`
   - **Create task**: Click "New Task" button → fill form → submit
   - **Edit task**: Click "Edit" button on a task → modify → save
   - **Complete task**: Click toggle button to mark complete/incomplete
   - **Delete task**: Click "Delete" button → confirm in modal

5. **Log out**:
   - Click "Logout" button in the navbar
   - You'll be redirected to `/login`

### Protected Routes

- `/app/*` routes require authentication
- Unauthenticated access redirects to `/login`
- JWT token stored in localStorage (or cookies per Better Auth config)
- Token automatically attached to all API requests

### Development URLs

- **Home/Landing**: `http://localhost:3000/`
- **Login**: `http://localhost:3000/login`
- **Signup**: `http://localhost:3000/signup`
- **Task List**: `http://localhost:3000/app/tasks` (protected)
- **New Task**: `http://localhost:3000/app/tasks/new` (protected)
- **Edit Task**: `http://localhost:3000/app/tasks/[id]/edit` (protected)

---

## Troubleshooting

### Issue: Backend API not responding

**Symptoms**: Network errors, 500 errors, or "Failed to fetch" messages

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/api/tasks`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local` matches backend URL
3. Ensure backend is configured to allow CORS from `http://localhost:3000`
4. Check backend logs for errors

### Issue: 401 Unauthorized on all requests

**Symptoms**: Redirected to login immediately after login, "Unauthorized" errors

**Solutions**:
1. Check JWT token is being stored: Open browser DevTools → Application → Local Storage → verify `todo_jwt_token` exists
2. Verify `BETTER_AUTH_SECRET` matches between frontend and backend
3. Clear localStorage and try logging in again
4. Check backend JWT verification logic

### Issue: CORS errors in browser console

**Symptoms**: "Access-Control-Allow-Origin" errors in browser console

**Solutions**:
1. Ensure backend has CORS middleware configured
2. Backend must allow origin: `http://localhost:3000`
3. Backend must allow headers: `Authorization`, `Content-Type`
4. Backend must allow methods: `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`

### Issue: Redirect loops between login and dashboard

**Symptoms**: Browser rapidly switches between `/login` and `/app/tasks`

**Solutions**:
1. Check middleware logic in `frontend/src/middleware.ts`
2. Verify JWT token format is correct
3. Clear localStorage and cookies, restart browser
4. Check for conflicting auth state in React components

### Issue: TypeScript errors on startup

**Symptoms**: Type errors preventing compilation

**Solutions**:
1. Ensure all dependencies installed: `npm install`
2. Check TypeScript version: `npx tsc --version` (should be 5.x)
3. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
4. Clear Next.js cache: `rm -rf .next`

### Issue: Tailwind styles not applying

**Symptoms**: Components appear unstyled or default HTML styling

**Solutions**:
1. Verify `tailwind.config.js` has correct content paths
2. Check `globals.css` imports Tailwind directives
3. Restart dev server: Stop and run `npm run dev` again
4. Clear browser cache

### Issue: Session not persisting after page refresh

**Symptoms**: User logged out on every page refresh

**Solutions**:
1. Check Better Auth storage configuration (localStorage vs cookies)
2. Verify token is being stored correctly in DevTools
3. Check if token has immediate expiration
4. Ensure middleware isn't clearing token on protected routes

---

## Running Tests (Optional)

### Unit Tests

```bash
npm run test
```

Runs Jest test suite for component and utility tests.

### End-to-End Tests

```bash
npm run test:e2e
```

Runs Playwright tests for full user flows (requires backend running).

---

## Building for Production

### Create Production Build

```bash
npm run build
```

This creates an optimized production build in the `.next` directory.

### Start Production Server Locally

```bash
npm run start
```

Serves the production build at `http://localhost:3000`.

### Environment Variables for Production

Update `.env.production` or deploy platform environment variables:

```env
NEXT_PUBLIC_API_URL=https://your-backend-api.com
BETTER_AUTH_SECRET=strong-random-secret-for-production
```

**Important**: Never commit `.env.production` with real secrets to version control.

---

## Deployment

### Vercel (Recommended for Next.js)

1. Push code to GitHub repository
2. Connect repository to Vercel
3. Configure environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL`
   - `BETTER_AUTH_SECRET`
4. Deploy automatically on push to main branch

### Docker Deployment

```dockerfile
# Dockerfile example (create in frontend root)
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t todo-frontend .
docker run -p 3000:3000 --env-file .env.production todo-frontend
```

---

## Common Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server (hot reload) |
| `npm run build` | Create production build |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint for code quality |
| `npm run test` | Run unit tests |
| `npm run test:e2e` | Run end-to-end tests |
| `npm run type-check` | Run TypeScript compiler check without emitting files |

---

## Project Structure Overview

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # Reusable UI components
│   ├── lib/              # Utilities and API client
│   ├── types/            # TypeScript type definitions
│   ├── hooks/            # Custom React hooks
│   └── middleware.ts     # Route protection middleware
├── public/               # Static assets
├── .env.local            # Local environment variables (not committed)
├── next.config.js        # Next.js configuration
├── tailwind.config.js    # Tailwind CSS configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies and scripts
```

---

## Additional Resources

- **Next.js Documentation**: https://nextjs.org/docs
- **Better Auth Documentation**: https://better-auth.com/docs
- **Tailwind CSS Documentation**: https://tailwindcss.com/docs
- **TypeScript Handbook**: https://www.typescriptlang.org/docs/handbook/intro.html
- **React Documentation**: https://react.dev/

---

## Getting Help

- Check `specs/001-frontend-ui/` for detailed specifications and contracts
- Review `research.md` for technology decisions and patterns
- Consult `plan.md` for implementation phases and structure
- Open an issue in the repository for bugs or feature requests

---

**Ready to start development!** Follow the setup steps above and begin with Phase 2.0 implementation.
