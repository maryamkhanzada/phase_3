# Deployment Guide: Frontend UI for Todo Application

**Feature**: Frontend UI for Todo Application
**Date**: 2026-01-08
**Status**: Ready for Deployment

## Overview

This document provides step-by-step instructions for deploying the Next.js frontend application to production environments.

---

## Prerequisites

- Node.js 18+ installed
- Backend API deployed and accessible
- Git repository access
- Vercel account (recommended) or other hosting provider

---

## Environment Variables

Create a `.env.production` file (or configure in your hosting provider):

```env
# Backend API URL (production)
NEXT_PUBLIC_API_URL=https://your-backend-api.com

# Better Auth secret (generate a secure random string)
BETTER_AUTH_SECRET=your-production-secret-key-minimum-32-characters
```

**Security Notes**:
- Never commit `.env.production` to version control
- Generate a strong random string for `BETTER_AUTH_SECRET` (minimum 32 characters)
- Use `openssl rand -base64 32` to generate a secure secret

---

## Build Steps

### Local Build

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run production build:
   ```bash
   npm run build
   ```

3. Test production build locally:
   ```bash
   npm run start
   ```

4. Access at `http://localhost:3000`

### Build Output

- `.next/` directory contains the optimized production build
- Static assets in `.next/static/`
- Server-side rendered pages in `.next/server/`

---

## Deployment Options

### Option 1: Vercel (Recommended)

Vercel is the recommended platform for Next.js applications.

#### Steps:

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   cd frontend
   vercel
   ```

4. **Configure Environment Variables** in Vercel Dashboard:
   - Go to Project Settings → Environment Variables
   - Add `NEXT_PUBLIC_API_URL` with production backend URL
   - Add `BETTER_AUTH_SECRET` with secure random string
   - Mark `BETTER_AUTH_SECRET` as secret

5. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

#### Vercel Configuration

The project includes a `vercel.json` configuration (optional):

```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1"]
}
```

---

### Option 2: Docker Deployment

#### Dockerfile

Create a `Dockerfile` in the `frontend/` directory:

```dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000

CMD ["node", "server.js"]
```

#### Build and Run Docker Container:

```bash
# Build image
docker build -t todo-frontend .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://your-backend-api.com \
  -e BETTER_AUTH_SECRET=your-secret-key \
  todo-frontend
```

---

### Option 3: Traditional Node.js Server

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Start the production server**:
   ```bash
   npm run start
   ```

3. **Use PM2 for process management**:
   ```bash
   npm install -g pm2
   pm2 start npm --name "todo-frontend" -- start
   pm2 save
   pm2 startup
   ```

---

## Post-Deployment Checklist

- [ ] Verify environment variables are set correctly
- [ ] Test authentication flow (signup, login, logout)
- [ ] Test task CRUD operations (create, read, update, delete)
- [ ] Verify protected routes redirect to login
- [ ] Test on mobile devices (responsive design)
- [ ] Check browser console for errors
- [ ] Verify API calls reach backend correctly
- [ ] Test CORS configuration (frontend → backend communication)
- [ ] Verify JWT token storage and session persistence
- [ ] Test error handling (network failures, 401 unauthorized, etc.)

---

## Monitoring and Debugging

### Next.js Logs

- **Development**: Logs appear in terminal running `npm run dev`
- **Production**: Check hosting provider logs (Vercel Logs, Docker logs, etc.)

### Browser DevTools

- **Console**: Check for JavaScript errors and API call failures
- **Network Tab**: Verify API requests and responses
- **Application Tab**: Check localStorage for `todo_jwt_token`

### Common Issues

1. **CORS Errors**:
   - Ensure backend allows frontend origin
   - Check `Access-Control-Allow-Origin` header

2. **401 Unauthorized**:
   - Verify JWT token is being sent in `Authorization` header
   - Check token expiration on backend

3. **Environment Variables Not Working**:
   - Ensure variables start with `NEXT_PUBLIC_` for client-side access
   - Rebuild application after changing environment variables

4. **Build Failures**:
   - Check for TypeScript errors: `npm run build`
   - Verify all dependencies are installed: `npm install`

---

## Rollback Strategy

### Vercel

- Use Vercel Dashboard to revert to previous deployment
- Or redeploy specific commit: `vercel --prod --force`

### Docker

- Keep previous image tagged:
  ```bash
  docker tag todo-frontend:latest todo-frontend:v1.0.0
  ```
- Rollback:
  ```bash
  docker run -p 3000:3000 todo-frontend:v1.0.0
  ```

### PM2

- Revert code and rebuild:
  ```bash
  git checkout previous-commit
  npm run build
  pm2 restart todo-frontend
  ```

---

## Performance Optimization

### Next.js Built-in Optimizations

- Automatic code splitting
- Image optimization (use Next.js `<Image>` component)
- Font optimization (Geist fonts loaded via next/font)

### Additional Optimizations

1. **Enable Compression**:
   - Vercel enables gzip/brotli by default
   - For custom servers, use compression middleware

2. **Cache Static Assets**:
   - Set cache headers for `.next/static/` assets
   - Use CDN for static file delivery

3. **Minimize Bundle Size**:
   - Analyze bundle: `npm run build` shows bundle sizes
   - Use dynamic imports for large components:
     ```tsx
     const Modal = dynamic(() => import('@/components/ui/Modal'))
     ```

---

## Security Best Practices

- [ ] Use HTTPS in production (Vercel provides this automatically)
- [ ] Set secure environment variables (never expose secrets in client code)
- [ ] Enable Content Security Policy (CSP) headers
- [ ] Implement rate limiting on authentication endpoints (backend)
- [ ] Regularly update dependencies: `npm audit fix`
- [ ] Use strong `BETTER_AUTH_SECRET` (minimum 32 characters)

---

## Continuous Deployment

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Vercel

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

---

## Support

For deployment issues, check:
- Next.js deployment docs: https://nextjs.org/docs/deployment
- Vercel docs: https://vercel.com/docs
- Project issue tracker: (add your repository URL here)

---

**Last Updated**: 2026-01-08
**Deployment Status**: Ready for Production
