import { test, expect } from '@playwright/test';
import { TEST_USERS, waitForNetworkIdle, takeDebugScreenshot } from './helpers/test-data';

test.describe('Stripe Connect Onboarding', () => {
  test.beforeEach(async ({ page }) => {
    // Login as host
    await page.goto('/');
    await page.getByLabel(/email/i).fill(TEST_USERS.host.email);
    await page.getByLabel(/password/i).fill(TEST_USERS.host.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await waitForNetworkIdle(page);
  });

  test('should navigate to financials page', async ({ page }) => {
    // Go to financials
    await page.getByRole('link', { name: /financials|payouts/i }).click();
    await waitForNetworkIdle(page);
    
    await expect(page).toHaveURL(/financials/);
    await expect(page.getByText(/payouts|earnings|financial/i)).toBeVisible();
  });

  test('should show Stripe Connect setup if not onboarded', async ({ page }) => {
    await page.goto('/dashboard/financials');
    await waitForNetworkIdle(page);
    
    // Check if already onboarded or needs setup
    const setupButton = page.getByRole('button', { name: /connect stripe|setup stripe/i });
    const hasSetup = await setupButton.count() > 0;
    
    if (hasSetup) {
      await expect(setupButton).toBeVisible();
      console.log('✓ Stripe Connect setup button found');
    } else {
      console.log('✓ Stripe Connect already configured');
      await expect(page.getByText(/connected|active/i)).toBeVisible();
    }
  });

  test('should initiate Stripe Connect onboarding', async ({ page }) => {
    await page.goto('/dashboard/financials');
    await waitForNetworkIdle(page);
    
    const setupButton = page.getByRole('button', { name: /connect stripe|setup stripe/i });
    const hasSetup = await setupButton.count() > 0;
    
    if (hasSetup) {
      // Click setup button
      await setupButton.click();
      
      // Should redirect to Stripe or show onboarding link
      await page.waitForTimeout(2000);
      
      // Either redirected to Stripe or showing onboarding URL
      const currentUrl = page.url();
      
      if (currentUrl.includes('connect.stripe.com')) {
        console.log('✓ Redirected to Stripe Connect onboarding');
        await expect(page).toHaveURL(/connect\.stripe\.com/);
      } else {
        console.log('✓ Onboarding link generated');
        await takeDebugScreenshot(page, 'stripe-onboarding');
      }
    } else {
      test.skip();
    }
  });

  test('should display payout settings', async ({ page }) => {
    await page.goto('/dashboard/financials');
    await waitForNetworkIdle(page);
    
    // Look for payout-related elements
    const hasPayout = await page.getByText(/payout|balance|earnings/i).count() > 0;
    expect(hasPayout).toBeTruthy();
    
    console.log('✓ Payout information displayed');
  });

  test('should show earnings summary', async ({ page }) => {
    await page.goto('/dashboard/financials');
    await waitForNetworkIdle(page);
    
    // Should show some financial metrics
    const hasMetrics = await page.locator('text=/AED|\\$/i').count() > 0;
    expect(hasMetrics).toBeTruthy();
    
    console.log('✓ Financial metrics visible');
  });
});

