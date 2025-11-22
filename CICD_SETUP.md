# CI/CD Setup Guide

## Overview

Automated testing and deployment pipeline using GitHub Actions. Tests run on every push/PR, deploys automatically to staging and production.

## Architecture

```
Code Push → GitHub Actions → Tests → Security Audit → Deploy
                                ↓
                         Staging/Production
                                ↓
                          Smoke Tests
                                ↓
                        Rollback (if needed)
```

## Setup Instructions

### 1. GitHub Secrets Configuration

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

**Supabase (Test Environment):**
```
TEST_SUPABASE_URL=https://your-test-project.supabase.co
TEST_SUPABASE_ANON_KEY=your_test_anon_key
TEST_SUPABASE_SERVICE_ROLE_KEY=your_test_service_role_key
```

**Render API:**
```
RENDER_API_KEY=your_render_api_key
RENDER_SERVICE_ID_BACKEND=srv_xxxxxxxxxxxxx
RENDER_SERVICE_ID_FRONTEND=srv_xxxxxxxxxxxxx
RENDER_SERVICE_ID_STAGING=srv_xxxxxxxxxxxxx
```

To get Render API key:
1. Go to Render Dashboard → Account Settings
2. Click "API Keys"
3. Create new key with name "GitHub Actions"

To get Service IDs:
1. Go to your service in Render
2. URL contains service ID: `dashboard.render.com/web/srv_xxxxxxxxxxxxx`

### 2. Create Staging Environment

**In Render:**
1. Duplicate your production backend service
2. Name it "krib-backend-staging"
3. Use branch: `staging`
4. Set environment: `ENVIRONMENT=staging`
5. Custom domain: `staging-api.host.krib.ae`

**In GitHub:**
1. Create `staging` branch: `git checkout -b staging`
2. Push to GitHub: `git push origin staging`

### 3. Enable GitHub Environments

1. Go to Settings → Environments
2. Create `production` environment
3. Add protection rules:
   - Required reviewers (optional)
   - Wait timer: 0 minutes
   - Deployment branches: only `main`

### 4. Test the Pipeline

**Run tests locally:**
```bash
cd backend
pip install pytest pytest-asyncio pytest-cov httpx
pytest tests/ -v
```

**Trigger CI/CD:**
```bash
git add .
git commit -m "test: trigger CI/CD pipeline"
git push origin main
```

Watch the workflow in GitHub Actions tab.

## Workflow Details

### CI Pipeline (Runs on every push/PR)

**1. Backend Tests**
- Python 3.11, Ubuntu
- PostgreSQL 15 + Redis 7 services
- Linting with flake8 + black
- Unit tests with pytest
- Code coverage report
- Uploads coverage to Codecov

**2. Frontend Tests**
- Node.js 18, Ubuntu
- Linting
- Type checking (TypeScript)
- Build verification

**3. Security Audit**
- Python: safety check
- Node: npm audit
- Secret scanning with TruffleHog

### CD Pipeline (Runs on push to main/staging)

**Staging Deploy (on `staging` branch):**
1. Runs all tests
2. Deploys to staging environment
3. Waits 60 seconds
4. Runs smoke tests

**Production Deploy (on `main` branch):**
1. Runs all tests + security audit
2. Requires manual approval (if configured)
3. Deploys backend + frontend
4. Waits 90 seconds
5. Runs production smoke tests
6. Creates deployment record
7. Auto-rollback on failure

### Rollback Procedure

**Manual Rollback:**
1. Go to Actions → Rollback Production
2. Click "Run workflow"
3. Enter commit SHA to rollback to
4. Confirm

**Find commit SHA:**
```bash
git log --oneline -10
```

**Emergency Rollback (Render Dashboard):**
1. Go to service → Deploys
2. Click "Redeploy" on previous working version

## Test Coverage

**Current Tests:**
- Health checks (3 tests)
- Query service (5 tests)
- Configuration (4 tests)

**Total: 12 tests**

**Add more tests:**
```bash
cd backend/tests
# Create test_properties.py
# Create test_bookings.py
# Create test_auth.py
```

## Monitoring Deployments

**GitHub Actions:**
- https://github.com/your-org/host-dashboard/actions

**Render Logs:**
- https://dashboard.render.com

**Deployment Status:**
```bash
# Check if services are running
curl https://api.host.krib.ae/health
curl https://host.krib.ae
```

## Troubleshooting

### Tests Failing

**Check logs:**
```bash
# In GitHub Actions, click on failed job
# View logs for specific step
```

**Run locally:**
```bash
cd backend
DEBUG=true pytest tests/ -v -s
```

### Deployment Failing

**Check Render logs:**
1. Go to service in Render
2. Click "Logs" tab
3. Look for errors

**Common issues:**
- Environment variables not set
- Database migration needed
- Dependency conflict

### Rollback Not Working

**Manual fix:**
1. SSH to Render or use dashboard
2. Revert to previous deploy
3. Check logs for errors

## Best Practices

**1. Branch Strategy:**
- `main` → production
- `staging` → staging environment
- Feature branches → create PR to staging first

**2. Testing:**
- Write tests for new features
- Maintain >80% code coverage
- Run tests locally before pushing

**3. Deployment:**
- Test in staging first
- Monitor logs after deploy
- Keep commit messages clear

**4. Rollback:**
- Document working commit SHAs
- Test rollback procedure monthly
- Keep last 3 versions deployable

## Performance Metrics

**CI/CD Speed:**
- Tests: ~3-5 minutes
- Deploy: ~2-3 minutes
- Total: ~5-8 minutes per deploy

**Success Rate Target:** >95%

## Security

**Secret Management:**
- All secrets in GitHub Secrets
- Never commit secrets to repo
- Rotate keys quarterly

**Access Control:**
- Production requires approval
- API keys have minimal permissions
- Audit deploy logs

## Next Steps

1. Add integration tests for Stripe
2. Add E2E tests with Playwright
3. Add performance tests with Locust
4. Set up Sentry for error tracking
5. Add Slack notifications

