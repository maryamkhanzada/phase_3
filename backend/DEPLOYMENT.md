# Backend Deployment Checklist

## Pre-Deployment Checklist

### Environment Configuration

- [ ] **DATABASE_URL** configured in production environment
  - Format: `postgresql://user:password@host:5432/dbname`
  - Neon connection string with SSL enabled
  - Test connection before deployment

- [ ] **BETTER_AUTH_SECRET** set (minimum 32 characters)
  - MUST match frontend configuration exactly
  - Use strong random value: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
  - NEVER commit to version control

- [ ] **FRONTEND_URL** set to production frontend origin
  - Development: `http://localhost:3000`
  - Production: `https://app.yourdomain.com`
  - Required for CORS configuration

- [ ] **JWT_EXPIRATION_HOURS** configured (default: 24)
- [ ] **APP_ENV** set to `production`
- [ ] **LOG_LEVEL** set appropriately (`INFO` or `WARNING`)

### Database Setup

- [ ] Neon PostgreSQL database created
- [ ] Database connection tested
- [ ] Tables created (run `init_db()` on first startup)
- [ ] Database credentials secured

### Application Validation

- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Application starts without errors: `uvicorn src.main:app`
- [ ] Health check endpoint responds: `GET /health` returns `{"status": "healthy"}`
- [ ] Swagger docs accessible: `GET /docs`
- [ ] CORS headers present in responses

### Security Checklist

- [ ] `.env` file NOT committed to git (.gitignore configured)
- [ ] No hardcoded secrets in code
- [ ] Password hashing enabled (bcrypt with cost factor 12)
- [ ] JWT tokens signed with HS256
- [ ] User isolation enforced in all task queries
- [ ] Authorization header validation implemented
- [ ] Error messages don't leak sensitive information

### Testing

- [ ] Signup flow tested: `POST /api/auth/signup`
- [ ] Login flow tested: `POST /api/auth/login`
- [ ] Task CRUD tested with authentication
- [ ] User isolation verified (User A cannot access User B's data)
- [ ] Error responses tested (401, 400, 404, 409, 500)
- [ ] Token expiration handling tested

## Deployment Steps

### 1. Containerization (Docker)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t todo-backend .
docker run -p 8000:8000 --env-file .env todo-backend
```

### 2. Cloud Deployment

**AWS (Elastic Beanstalk / ECS)**:
- Configure environment variables in console
- Set up database security group for Neon access
- Configure health check: `/health`
- Enable HTTPS with ALB/CloudFront

**Google Cloud (Cloud Run)**:
```bash
gcloud run deploy todo-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=...,BETTER_AUTH_SECRET=...,FRONTEND_URL=..."
```

**Heroku**:
```bash
heroku create todo-backend
heroku config:set DATABASE_URL=...
heroku config:set BETTER_AUTH_SECRET=...
heroku config:set FRONTEND_URL=...
git push heroku main
```

### 3. Post-Deployment Validation

- [ ] Health check returns 200: `curl https://api.yourdomain.com/health`
- [ ] Signup creates user: `POST /api/auth/signup`
- [ ] Login returns token: `POST /api/auth/login`
- [ ] Protected endpoints require authentication
- [ ] CORS allows frontend origin
- [ ] Database tables created successfully
- [ ] Logs show no errors

## Monitoring & Maintenance

### Health Checks

Configure container orchestration health checks:
- **Liveness probe**: `GET /health` (every 30s)
- **Readiness probe**: `GET /health` (before traffic routing)
- **Startup probe**: `GET /health` (initial startup, timeout 60s)

### Logging

Monitor application logs for:
- Authentication failures (potential attacks)
- Database connection errors
- Unhandled exceptions (500 errors)
- Performance issues (slow queries)

### Metrics to Track

- Request latency (p50, p95, p99)
- Error rates by endpoint
- Authentication success/failure rates
- Database query performance
- Active user count

### Backup & Recovery

- **Database**: Neon provides automatic backups
- **Secrets**: Store BETTER_AUTH_SECRET in secure vault (AWS Secrets Manager, GCP Secret Manager)
- **Code**: Ensure git repository is backed up

## Rollback Plan

If deployment fails:

1. **Check logs**: `docker logs <container_id>` or cloud platform logs
2. **Verify environment variables**: Ensure all required vars are set
3. **Test database connection**: Check DATABASE_URL and network access
4. **Rollback code**: Deploy previous stable version
5. **Notify team**: Update status page if user-facing

## Security Incident Response

If security breach detected:

1. **Rotate BETTER_AUTH_SECRET immediately** (invalidates all tokens)
2. **Check database for unauthorized access**
3. **Review access logs for suspicious activity**
4. **Notify affected users**
5. **Update credentials and redeploy**

## Performance Optimization

For production load:

- [ ] Enable database connection pooling (SQLAlchemy pool_size)
- [ ] Add Redis for JWT token caching (optional)
- [ ] Configure reverse proxy (Nginx) for static assets
- [ ] Enable gzip compression
- [ ] Set up CDN for API responses (if needed)

## Troubleshooting

### Common Issues

**Database connection fails**:
- Check DATABASE_URL format
- Verify Neon database is running
- Check network/firewall rules

**JWT verification fails**:
- Ensure BETTER_AUTH_SECRET matches frontend
- Check token expiration time
- Verify HS256 algorithm

**CORS errors**:
- Verify FRONTEND_URL matches actual frontend origin
- Check Access-Control-Allow-Origin header in response
- Ensure preflight requests return 200

**500 Internal Server Error**:
- Check application logs
- Verify all dependencies installed
- Test database connectivity

## Support Contacts

- **Database**: Neon support (https://neon.tech/docs)
- **Hosting**: Your cloud provider support
- **Application**: Development team

---

**Last Updated**: 2026-01-09
**Backend Version**: 1.0.0
**Deployment Environment**: Production
