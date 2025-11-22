import { test, expect } from '@playwright/test';
import { TEST_USERS, waitForNetworkIdle } from './helpers/test-data';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load login page', async ({ page }) => {
    await expect(page).toHaveTitle(/Krib/i);
    
    // Should see login elements
    await expect(page.getByRole('heading', { name: /sign in/i })).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Fill login form
    await page.getByLabel(/email/i).fill(TEST_USERS.host.email);
    await page.getByLabel(/password/i).fill(TEST_USERS.host.password);
    
    // Click sign in
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Wait for redirect to dashboard
    await waitForNetworkIdle(page);
    await expect(page).toHaveURL(/dashboard/);
    
    // Should see dashboard elements
    await expect(page.getByText(/properties/i)).toBeVisible();
    await expect(page.getByText(/bookings/i)).toBeVisible();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.getByLabel(/email/i).fill('invalid@test.com');
    await page.getByLabel(/password/i).fill('wrongpassword');
    
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Should show error message
    await expect(page.getByText(/invalid credentials|error/i)).toBeVisible();
  });

  test('should logout successfully', async ({ page, context }) => {
    // Login first
    await page.goto('/');
    await page.getByLabel(/email/i).fill(TEST_USERS.host.email);
    await page.getByLabel(/password/i).fill(TEST_USERS.host.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await waitForNetworkIdle(page);
    
    // Logout
    await page.getByRole('button', { name: /logout|sign out/i }).click();
    
    // Should redirect to login
    await waitForNetworkIdle(page);
    await expect(page).toHaveURL(/^\/$|\/login/);
  });
});

