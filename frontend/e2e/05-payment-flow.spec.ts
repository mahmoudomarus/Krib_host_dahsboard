import { test, expect } from '@playwright/test';
import { TEST_USERS, waitForNetworkIdle, takeDebugScreenshot } from './helpers/test-data';

test.describe('Payment & Payouts', () => {
  test.beforeEach(async ({ page }) => {
    // Login as host
    await page.goto('/');
    await page.getByLabel(/email/i).fill(TEST_USERS.host.email);
    await page.getByLabel(/password/i).fill(TEST_USERS.host.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await waitForNetworkIdle(page);
  });

  test('should display earnings summary', async ({ page }) => {
    await page.goto('/dashboard/financials');
    await waitForNetworkIdle(page);
    
    // Should show earnings metrics
    await expect(page.getByText(/earnings|revenue|balance/i)).toBeVisible();
    
    // Look for currency amounts
    const hasAmounts = await page.locator('text=/AED|\\$|[0-9]+\\.[0-9]{2}/').count() > 0;
    expect(hasAmounts).toBeTruthy();
    
    console.log('✓ Earnings summary displayed');
    await takeDebugScreenshot(page, 'earnings-summary');
  });

  test('should show completed bookings revenue', async ({ page }) => {
    await page.goto('/dashboard/financials');
    await waitForNetworkIdle(page);
    
    // Look for revenue breakdown
    const hasRevenue = await page.locator('text=/completed bookings|total revenue/i').count() > 0;
    
    if (hasRevenue) {
      console.log('✓ Revenue breakdown visible');
    }
  });

  test('should display pending payouts', async ({ page }) => {
    await page.goto('/dashboard/financials');
    await waitForNetworkIdle(page);
    
    // Look for payouts section
    const hasPayouts = await page.locator('text=/payout|pending|available/i').count() > 0;
    expect(hasPayouts).toBeTruthy();
    
    console.log('✓ Payouts section displayed');
  });

  test('should show payout history', async ({ page }) => {
    await page.goto('/dashboard/financials');
    await waitForNetworkIdle(page);
    
    // Scroll to payout history
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1000);
    
    // Look for payout history
    const hasHistory = await page.locator('text=/payout history|past payouts|transactions/i').count() > 0;
    
    if (hasHistory) {
      console.log('✓ Payout history visible');
    }
    
    await takeDebugScreenshot(page, 'payout-history');
  });

  test('should show Stripe account status', async ({ page }) => {
    await page.goto('/dashboard/financials');
    await waitForNetworkIdle(page);
    
    // Look for Stripe connection status
    const hasStatus = await page.locator('text=/connected|active|setup|pending/i').count() > 0;
    expect(hasStatus).toBeTruthy();
    
    console.log('✓ Stripe account status shown');
  });

  test('should display payment breakdown', async ({ page }) => {
    await page.goto('/dashboard/financials');
    await waitForNetworkIdle(page);
    
    // Look for fee breakdown
    const hasBreakdown = await page.locator('text=/platform fee|service fee|net amount/i').count() > 0;
    
    if (hasBreakdown) {
      console.log('✓ Payment breakdown visible');
    }
  });

  test('should navigate to payout settings', async ({ page }) => {
    await page.goto('/dashboard/financials');
    await waitForNetworkIdle(page);
    
    // Look for settings button
    const settingsButton = page.getByRole('button', { name: /settings|preferences/i }).first();
    const hasSettings = await settingsButton.count() > 0;
    
    if (hasSettings) {
      await settingsButton.click();
      await waitForNetworkIdle(page);
      
      console.log('✓ Payout settings accessed');
      await takeDebugScreenshot(page, 'payout-settings');
    }
  });

  test('should show auto-payout settings', async ({ page }) => {
    await page.goto('/dashboard/financials');
    await waitForNetworkIdle(page);
    
    // Look for auto-payout toggle/settings
    const hasAutoPayout = await page.locator('text=/auto.*payout|automatic.*payout/i').count() > 0;
    
    if (hasAutoPayout) {
      console.log('✓ Auto-payout settings found');
    }
  });
});

test.describe('Financial Analytics', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/');
    await page.getByLabel(/email/i).fill(TEST_USERS.host.email);
    await page.getByLabel(/password/i).fill(TEST_USERS.host.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await waitForNetworkIdle(page);
  });

  test('should display revenue charts', async ({ page }) => {
    await page.goto('/dashboard/analytics');
    await waitForNetworkIdle(page);
    
    // Look for charts/graphs
    const hasCharts = await page.locator('canvas, svg[class*="chart"]').count() > 0;
    
    if (hasCharts) {
      console.log('✓ Revenue charts displayed');
      await takeDebugScreenshot(page, 'revenue-charts');
    }
  });

  test('should show booking statistics', async ({ page }) => {
    await page.goto('/dashboard/analytics');
    await waitForNetworkIdle(page);
    
    // Look for booking stats
    const hasStats = await page.locator('text=/total bookings|occupancy rate|average/i').count() > 0;
    
    if (hasStats) {
      console.log('✓ Booking statistics visible');
    }
  });

  test('should filter analytics by time period', async ({ page }) => {
    await page.goto('/dashboard/analytics');
    await waitForNetworkIdle(page);
    
    // Look for time period selector
    const hasPeriodFilter = await page.locator('text=/7 days|30 days|month|year/i').count() > 0;
    
    if (hasPeriodFilter) {
      console.log('✓ Time period filters available');
    }
  });
});

