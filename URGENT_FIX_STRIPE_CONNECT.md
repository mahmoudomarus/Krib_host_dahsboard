# URGENT: Fix Stripe Connect Setup

## Critical Issues Found

### Issue 1: Stripe Connect Not Enabled ⚠️

**Error from logs:**
```
Stripe error: Only Stripe Connect platforms can work with other accounts.
```

**Problem:** Your Stripe account is using **regular API keys**, NOT **Connect platform keys**.

**Impact:** All Stripe features (onboarding, payouts, account status) are failing with 500 errors.

---

### Issue 2: Mixed Content (HTTP vs HTTPS)

**Error from browser:**
```
Mixed Content: The page at 'https://host.krib.ae/dashboard/financials' was loaded over HTTPS, 
but requested an insecure resource 'http://api.host.krib.ae/api/bookings/'.
```

**Problem:** Frontend is requesting `http://` instead of `https://` (likely build cache issue).

**Impact:** API requests are blocked by browser security.

---

## Fix Issue 1: Enable Stripe Connect (CRITICAL!)

### Step 1: Go to Stripe Dashboard

1. Login to Stripe: https://dashboard.stripe.com
2. Go to: **Connect > Settings**
   - Or direct link: https://dashboard.stripe.com/account/applications/settings

### Step 2: Enable Connect Platform

1. Click **"Get Started with Connect"** or **"Enable Connect"**
2. Choose platform type: **"Platform or Marketplace"**
3. Fill in platform details:
   ```
   Platform Name: Krib Host Dashboard
   Platform URL: https://host.krib.ae
   ```

### Step 3: Configure Connect Settings

1. **Account Types**: Enable **"Express accounts"** (recommended for UAE)
2. **Redirect URIs**: Add:
   ```
   https://host.krib.ae/dashboard/financials
   ```
3. **Webhook Endpoints**: Add:
   ```
   https://api.krib.ae/api/billing/webhook
   ```

### Step 4: Get NEW API Keys

After enabling Connect, you'll get:

1. **Publishable Key** (starts with `pk_live_...` or `pk_test_...`)
2. **Secret Key** (starts with `sk_live_...` or `sk_test_...`)
3. **Client ID** (NEW - starts with `ca_...`) ← **This is Connect-specific!**

### Step 5: Update Render Environment Variables

Go to Render Dashboard → Backend Service → Environment:

```bash
# Replace with NEW Connect keys
STRIPE_PUBLISHABLE_KEY=pk_test_... # or pk_live_...
STRIPE_SECRET_KEY=sk_test_...      # or sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Add Connect-specific (if needed)
STRIPE_CLIENT_ID=ca_...
```

**Important:** Use **test keys** (`pk_test_...`, `sk_test_...`) initially to avoid real charges!

### Step 6: Verify Stripe Connect is Enabled

Run this test:
```bash
curl -X GET https://api.host.krib.ae/api/v1/stripe/host/account-status \
  -H "Authorization: Bearer YOUR_SUPABASE_TOKEN"
```

Should return account status, NOT a 500 error.

---

## Fix Issue 2: HTTPS Build Cache

### Step 1: Clear Frontend Build Cache

```bash
cd frontend

# Remove build cache
rm -rf dist node_modules/.vite

# Rebuild
npm run build
```

### Step 2: Force Redeploy on Render

Go to Render Dashboard → Frontend Service:
1. Click **"Manual Deploy"**
2. Choose **"Clear build cache & deploy"**
3. Wait for deployment to complete

### Step 3: Clear Browser Cache

In your browser:
1. Open DevTools (F12)
2. Right-click refresh button
3. Select **"Empty Cache and Hard Reload"**

Or use incognito/private mode to test without cache.

---

## Testing After Fixes

### Test 1: Verify HTTPS Requests

1. Go to https://host.krib.ae/dashboard/financials
2. Open DevTools → Network tab
3. Check all requests go to `https://api.host.krib.ae` (NOT http)
4. Should see no "Mixed Content" errors

### Test 2: Verify Stripe Connect

1. Go to Financials page
2. Click "Setup Stripe" or "Connect Stripe"
3. Should redirect to Stripe Connect onboarding
4. Should NOT see "Only Stripe Connect platforms can work with other accounts" error

### Test 3: Check Backend Logs

```bash
# Should NOT see Stripe Connect errors
# Should see successful Stripe API calls
```

---

## Why This Happened

### Stripe Connect Issue

You were using **standard Stripe keys** instead of **Connect platform keys**.

**Standard Stripe:**
- For single businesses
- Direct payments to your account
- No marketplace/platform features

**Stripe Connect:**
- For platforms/marketplaces
- Payments to multiple accounts (hosts)
- Platform takes fees
- Requires separate setup

### HTTPS Issue

Frontend was built with old cached config. After rebuild, should use HTTPS.

---

## Quick Summary

| Issue | Fix | Priority |
|-------|-----|----------|
| Stripe Connect not enabled | Enable in Stripe Dashboard → Get new keys | **CRITICAL** |
| HTTP instead of HTTPS | Clear cache → Rebuild → Redeploy | High |

---

## Estimated Time

- **Stripe Connect Setup**: 10-15 minutes
- **Frontend Rebuild**: 5 minutes
- **Testing**: 5 minutes
- **Total**: ~20-25 minutes

---

## Support Links

- Stripe Connect Setup: https://dashboard.stripe.com/account/applications/settings
- Stripe Connect Docs: https://stripe.com/docs/connect
- Render Dashboard: https://dashboard.render.com

---

## After Fixes Complete

Run this checklist:

```
✅ Stripe Connect enabled in dashboard
✅ New API keys updated in Render
✅ Frontend rebuilt and redeployed
✅ Browser cache cleared
✅ No "Mixed Content" errors in console
✅ No "Only Stripe Connect platforms" errors in logs
✅ Can access Financials page
✅ Can initiate Stripe onboarding
✅ API returns 200 (not 500)
```

---

**Once fixed, you can proceed with testing the complete flow!**

