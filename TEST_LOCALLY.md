# How to Test Locally Before Pushing

Always test your changes locally before pushing to avoid CI/CD failures.

## Backend Tests

### Setup
```bash
cd backend
pip install pytest pytest-asyncio pytest-cov httpx
```

### Run All Tests
```bash
DEBUG=true python -m pytest tests/ -v
```

### Run Specific Test File
```bash
DEBUG=true python -m pytest tests/test_config.py -v
```

### Run with Coverage
```bash
DEBUG=true python -m pytest tests/ -v --cov=app --cov-report=term
```

### Expected Output
```
tests/test_config.py::test_config_defaults PASSED
tests/test_config.py::test_config_from_env PASSED
tests/test_config.py::test_production_config_validation PASSED
tests/test_config.py::test_secure_secret_generation PASSED
tests/test_health.py::test_health_response_structure PASSED
tests/test_health.py::test_root_endpoint_structure PASSED
tests/test_health.py::test_simple_health_structure PASSED
tests/test_query_service.py::test_calculate_booking_total PASSED
tests/test_query_service.py::test_calculate_booking_total_invalid_dates PASSED
tests/test_query_service.py::test_validate_guest_count PASSED
tests/test_query_service.py::test_validate_guest_count_edge_case PASSED

======================== 11 passed in 0.02s ========================
```

## Frontend Tests

### Setup
```bash
cd frontend
npm install
```

### Run Type Checking
```bash
npx tsc --noEmit
```

### Run Build
```bash
npm run build
```

### Run Tests (when configured)
```bash
npm test
```

## Security Audit

### Python Dependencies
```bash
cd backend
pip install safety
safety check
```

### Node Dependencies
```bash
cd frontend
npm audit
```

## Full CI/CD Simulation

Run everything that CI/CD runs:

```bash
# Backend
cd backend
DEBUG=true python -m pytest tests/ -v --cov=app
pip install flake8 black
flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics
black --check app

# Frontend
cd ../frontend
npx tsc --noEmit
npm run build
npm audit --audit-level=moderate

# Security
cd ../backend
safety check
```

## Quick Pre-Push Checklist

Before `git push`, run:

```bash
# 1. Backend tests
cd backend && DEBUG=true python -m pytest tests/ -v

# 2. Frontend build
cd ../frontend && npm run build

# 3. Git commit
cd ..
git add -A
git commit -m "your message"
git push origin main
```

## Troubleshooting

### "Invalid API key" Error
**Problem:** Tests trying to connect to real Supabase
**Solution:** Ensure `DEBUG=true` is set

### "ModuleNotFoundError"
**Problem:** Missing dependencies
**Solution:** `pip install -r backend/requirements.txt`

### "Cannot find module"
**Problem:** Frontend deps not installed
**Solution:** `cd frontend && npm install`

### "Black would reformat X files"
**Problem:** Code not formatted according to Black standards
**Solution:** Run `cd backend && black app` before committing

### "F821 undefined name"
**Problem:** Missing imports in Python files
**Solution:** Add missing imports (e.g., `from datetime import timedelta`)

### "error TS2304: Cannot find name"
**Problem:** Variable not defined in TypeScript
**Solution:** Define variable or use correct reference

### "Option 'X' has been removed"
**Problem:** Deprecated TypeScript config option
**Solution:** Remove the option from `tsconfig.json`

### Tests Pass Locally But Fail in CI/CD
**Problem:** Environment differences
**Solution:** Check `.github/workflows/ci-cd.yml` for exact commands used

## Adding New Tests

### Backend Test Template
```python
# backend/tests/test_my_feature.py
import pytest

def test_my_feature():
    """Test description"""
    # Arrange
    input_data = "test"
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result == expected_output
```

### Run New Test
```bash
cd backend
DEBUG=true python -m pytest tests/test_my_feature.py -v
```

## Test Coverage Goals

- **Minimum:** 70% coverage
- **Target:** 80% coverage
- **Ideal:** 90% coverage

Check coverage:
```bash
cd backend
DEBUG=true python -m pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

## CI/CD Pipeline Order

1. **Backend Tests** (55s)
   - Install Python 3.11
   - Install dependencies
   - Run linting
   - Run tests with coverage
   
2. **Frontend Tests** (27s)
   - Install Node.js 18
   - Install dependencies
   - Run type checking
   - Run build

3. **Security Audit** (20s)
   - Safety check (Python)
   - NPM audit (Node)

4. **Deploy** (only if all tests pass)
   - Staging (on `staging` branch)
   - Production (on `main` branch)

Total CI/CD time: ~3-5 minutes

## Performance Tips

**Faster tests:**
```bash
# Run in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest tests/ -n auto
```

**Skip slow tests:**
```bash
pytest tests/ -m "not slow"
```

**Run only failed tests:**
```bash
pytest --lf  # last failed
pytest --ff  # failed first
```

