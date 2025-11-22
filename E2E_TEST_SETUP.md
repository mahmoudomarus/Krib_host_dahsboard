# E2E Testing Setup Guide

## Overview

This guide explains how to set up and run End-to-End (E2E) tests for the Krib Host Dashboard using Playwright.

## Prerequisites

- Node.js 18+
- Your host account credentials (mahmoudomarus@gmail.com)
- Backend and frontend running locally OR access to staging/production

## Installation

```bash
cd frontend
npm install
npx playwright install
```

## Test User Setup

### Option 1: Use Your Existing Account (Recommended for Manual Testing)

1. Update `.env.test` with your credentials:
```env
TEST_USER_EMAIL=mahmoudomarus@gmail.com
TEST_USER_PASSWORD=your-actual-password
BASE_URL=https://host.krib.ae  # Or http://localhost:5173 for local
```

2. **Important**: Never commit your real password! Use environment variables.

### Option 2: Create Test User (Recommended for CI/CD)

1. Create a dedicated test account:
   - Email: `test-host@krib-test.com`
   - Password: Strong password (store in GitHub Secrets)

2. Set up the test user:
   - Create at least 1 property
   - Complete Stripe Connect onboarding (use Stripe test mode)
   - Create at least 1 booking

## Running Tests

### Run All E2E Tests

```bash
cd frontend
npm run test:e2e
```

### Run Specific Test File

```bash
# Auth tests
npx playwright test e2e/01-auth.spec.ts

# Stripe Connect tests
npx playwright test e2e/02-stripe-connect.spec.ts

# Property tests
npx playwright test e2e/03-property-creation.spec.ts

# Booking tests
npx playwright test e2e/04-booking-flow.spec.ts

# Payment tests
npx playwright test e2e/05-payment-flow.spec.ts
```

### Run in UI Mode (Interactive)

```bash
npx playwright test --ui
```

### Run in Headed Mode (See Browser)

```bash
npx playwright test --headed
```

### Run Specific Browser

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Test Environments

### Local Testing

```bash
# Terminal 1: Start backend
cd backend
uvicorn main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Run tests
cd frontend
npm run test:e2e:local
```

### Staging Testing

```bash
BASE_URL=https://staging.host.krib.ae npx playwright test
```

### Production Testing

```bash
BASE_URL=https://host.krib.ae npx playwright test
```

## Test Structure

```
frontend/e2e/
├── helpers/
│   └── test-data.ts          # Test data and utilities
├── 01-auth.spec.ts           # Authentication tests
├── 02-stripe-connect.spec.ts # Stripe Connect onboarding
├── 03-property-creation.spec.ts # Property CRUD
├── 04-booking-flow.spec.ts   # Booking management
└── 05-payment-flow.spec.ts   # Payments and payouts
```

## What Each Test Does

### 1. Authentication Tests (01-auth.spec.ts)
- ✓ Login with valid credentials
- ✓ Error handling for invalid credentials
- ✓ Logout functionality
- ✓ Session persistence

### 2. Stripe Connect Tests (02-stripe-connect.spec.ts)
- ✓ Navigate to financials page
- ✓ Check Stripe Connect status
- ✓ Initiate onboarding (if needed)
- ✓ View payout settings
- ✓ Display earnings summary

### 3. Property Tests (03-property-creation.spec.ts)
- ✓ View properties list
- ✓ Create new property
- ✓ Edit existing property
- ✓ View property details
- ✓ Property validation

### 4. Booking Tests (04-booking-flow.spec.ts)
- ✓ View bookings list
- ✓ Filter by status (pending/confirmed)
- ✓ Approve booking
- ✓ Reject booking
- ✓ View booking details

### 5. Payment Tests (05-payment-flow.spec.ts)
- ✓ View earnings summary
- ✓ Display revenue breakdown
- ✓ Show payout history
- ✓ Stripe account status
- ✓ Financial analytics

## Testing Your Complete User Flow

### Scenario 1: New Host Onboarding

```bash
# Run in sequence
npx playwright test e2e/01-auth.spec.ts
npx playwright test e2e/02-stripe-connect.spec.ts
npx playwright test e2e/03-property-creation.spec.ts
```

**What happens:**
1. Login as host
2. Connect Stripe account
3. Create first property

### Scenario 2: Booking Management

```bash
npx playwright test e2e/04-booking-flow.spec.ts
```

**What happens:**
1. View pending bookings
2. Approve or reject bookings
3. View booking details

### Scenario 3: Payment Processing

```bash
npx playwright test e2e/05-payment-flow.spec.ts
```

**What happens:**
1. View earnings
2. Check payout status
3. Review transaction history

## Manual Testing Checklist

Use this checklist to manually test the complete flow:

### ☐ Initial Setup
- [ ] Login with your account (mahmoudomarus@gmail.com)
- [ ] Verify dashboard loads correctly

### ☐ Stripe Connect
- [ ] Go to Financials page
- [ ] Check Stripe Connect status
- [ ] If not connected: Complete Stripe onboarding
- [ ] Verify account shows as "Connected" or "Active"

### ☐ Property Management
- [ ] View your existing properties
- [ ] Create a new test property
- [ ] Edit property details
- [ ] Publish property

### ☐ Booking Simulation
- [ ] Use external API to create test booking
- [ ] View booking in dashboard
- [ ] Approve booking
- [ ] Check booking status changes

### ☐ Payment Verification
- [ ] Check earnings summary
- [ ] Verify platform fee calculation
- [ ] View payout history
- [ ] Check available balance

## Debugging Tests

### View Test Results

```bash
npx playwright show-report
```

### Screenshots and Videos

Tests automatically capture:
- Screenshots on failure: `test-results/*.png`
- Videos on failure: `test-results/*.webm`
- Traces: `test-results/*.zip`

### View Trace

```bash
npx playwright show-trace test-results/trace.zip
```

### Debug Specific Test

```bash
# Add --debug flag
npx playwright test e2e/02-stripe-connect.spec.ts --debug
```

## CI/CD Integration

Tests run automatically on:
- Every push to `main` branch
- Every pull request
- Scheduled daily at 2 AM UTC

### GitHub Secrets Required

```
TEST_USER_EMAIL=test-host@krib-test.com
TEST_USER_PASSWORD=<secure-password>
```

## Troubleshooting

### Test Timeout

```bash
# Increase timeout
npx playwright test --timeout=60000
```

### Element Not Found

- Check if selector is correct
- Verify element is visible
- Add wait for network idle

### Stripe Redirect Issues

- Ensure Stripe test keys are used
- Check redirect URLs are correct
- Verify webhook endpoint is accessible

## Best Practices

1. **Data Isolation**: Tests should not depend on specific data
2. **Cleanup**: Clean up test data after each run
3. **Assertions**: Always assert expected outcomes
4. **Screenshots**: Take screenshots for debugging
5. **Retries**: Configure retries for flaky tests

## Support

If tests fail:
1. Check screenshots in `test-results/`
2. Review trace files
3. Run test in headed mode to see what's happening
4. Check console logs in browser DevTools

## Next Steps

1. Run tests locally to verify setup
2. Create test data (properties, bookings)
3. Complete Stripe onboarding in test mode
4. Run full test suite
5. Review results and fix any failures

---

**Happy Testing!** 🎭🚀

