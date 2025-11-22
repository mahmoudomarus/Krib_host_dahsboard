# Security Fixes Required

## Critical Issues (ERROR Level)

### 1. Row Level Security Not Enabled

**Problem:** Three reference tables do not have RLS enabled, exposing them to unauthorized access.

**Affected Tables:**
- `amenity_suggestions`
- `property_type_info`
- `booking_status_types`

**Fix:** Apply migration `supabase/migrations/20251123000001_security_fixes.sql`

**Steps:**
1. Go to Supabase Dashboard → SQL Editor
2. Copy content from `supabase/migrations/20251123000001_security_fixes.sql`
3. Run the migration
4. Verify RLS is enabled

**Verification:**
```sql
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('amenity_suggestions', 'property_type_info', 'booking_status_types');
```

All three should show `rowsecurity = true`.

---

## High Priority Warnings

### 2. Function Search Path Vulnerabilities

**Problem:** 10 database functions do not have fixed search_path, making them vulnerable to search_path injection attacks.

**Affected Functions:**
- `update_payouts_updated_at`
- `calculate_platform_fee`
- `cleanup_expired_notifications`
- `calculate_host_payout`
- `get_unread_notification_count`
- `disable_failed_webhook_subscriptions`
- `update_updated_at_column`
- `get_pending_earnings`
- `create_financial_transaction_on_booking`
- `calculate_host_balance`

**Fix:** Included in migration `supabase/migrations/20251123000001_security_fixes.sql`

All functions now have:
- `SECURITY DEFINER` clause
- `SET search_path = public` to prevent injection

---

## Medium Priority Warnings

### 3. Auth OTP Expiry Too Long

**Problem:** Email OTP expiry is set to more than 1 hour, increasing security risk.

**Current Setting:** > 1 hour  
**Recommended:** < 1 hour (ideally 10-15 minutes)

**Fix:**
1. Go to Supabase Dashboard → Authentication → Settings
2. Under "Email" provider settings
3. Set "OTP Expiry" to `600` seconds (10 minutes) or `900` seconds (15 minutes)
4. Save changes

---

### 4. Leaked Password Protection Disabled

**Problem:** Password leak detection against HaveIBeenPwned.org is disabled.

**Fix:**
1. Go to Supabase Dashboard → Authentication → Policies
2. Under "Password" section
3. Enable "Check password against HaveIBeenPwned"
4. Save changes

This prevents users from using compromised passwords discovered in data breaches.

---

### 5. Postgres Version Outdated

**Problem:** Current version `supabase-postgres-17.4.1.074` has security patches available.

**Fix:**
1. Go to Supabase Dashboard → Settings → Infrastructure
2. Click "Upgrade" button if available
3. Follow upgrade wizard

**Note:** Schedule during low-traffic period. Database will be briefly unavailable during upgrade (typically < 5 minutes).

---

## Migration Instructions

### Apply the Security Migration

**Option 1: Supabase Dashboard (Recommended)**
```bash
1. Open Supabase Dashboard
2. Go to SQL Editor
3. Open file: supabase/migrations/20251123000001_security_fixes.sql
4. Copy entire contents
5. Paste into SQL Editor
6. Click "Run"
7. Verify success message
```

**Option 2: Supabase CLI**
```bash
supabase db push
```

### Verification After Migration

Run this query to verify all fixes:
```sql
-- Check RLS enabled
SELECT 
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('amenity_suggestions', 'property_type_info', 'booking_status_types');

-- Check function search_path fixed
SELECT 
    routine_name,
    routine_definition
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN (
    'update_payouts_updated_at',
    'calculate_platform_fee',
    'cleanup_expired_notifications',
    'calculate_host_payout',
    'get_unread_notification_count',
    'disable_failed_webhook_subscriptions',
    'update_updated_at_column',
    'get_pending_earnings',
    'create_financial_transaction_on_booking',
    'calculate_host_balance'
)
AND routine_definition LIKE '%search_path%';
```

Expected: All 3 tables show `rls_enabled = true`, all 10 functions contain `search_path` in definition.

---

## Impact Assessment

### Reference Tables RLS
- **Risk:** Medium
- **Impact:** Low (read-only reference data)
- **Urgency:** High (fix immediately)
- **Downtime:** None

### Function Search Path
- **Risk:** Low to Medium
- **Impact:** Low (requires specific attack vector)
- **Urgency:** High (fix immediately)
- **Downtime:** None

### Auth Settings
- **Risk:** Low
- **Impact:** None (improves security)
- **Urgency:** Medium (fix within 1 week)
- **Downtime:** None

### Postgres Upgrade
- **Risk:** Low
- **Impact:** Brief downtime (2-5 minutes)
- **Urgency:** Medium (fix within 2 weeks)
- **Downtime:** Yes (2-5 minutes)

---

## Post-Fix Checklist

- [ ] Applied security migration
- [ ] Verified RLS enabled on all 3 reference tables
- [ ] Verified all 10 functions have search_path set
- [ ] Updated Auth OTP expiry to < 1 hour
- [ ] Enabled leaked password protection
- [ ] Scheduled Postgres upgrade
- [ ] Re-run Supabase linter to confirm fixes
- [ ] Document changes in PROJECT_HANDOVER.md

---

## Re-run Linter

After applying fixes, verify in Supabase Dashboard:
1. Go to Database → Linter
2. Click "Run Linter"
3. Confirm all ERROR level issues resolved
4. Review remaining warnings

Expected: 0 ERROR level issues, reduced WARNING count.

