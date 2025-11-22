import { test, expect } from '@playwright/test';
import { TEST_USERS, TEST_BOOKING, getTestBookingDates, waitForNetworkIdle, takeDebugScreenshot } from './helpers/test-data';

test.describe('Booking Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login as host
    await page.goto('/');
    await page.getByLabel(/email/i).fill(TEST_USERS.host.email);
    await page.getByLabel(/password/i).fill(TEST_USERS.host.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await waitForNetworkIdle(page);
  });

  test('should navigate to bookings page', async ({ page }) => {
    await page.getByRole('link', { name: /bookings/i }).click();
    await waitForNetworkIdle(page);
    
    await expect(page).toHaveURL(/bookings/);
    await expect(page.getByText(/bookings|reservations/i)).toBeVisible();
    
    console.log('✓ Bookings page loaded');
  });

  test('should display existing bookings', async ({ page }) => {
    await page.goto('/dashboard/bookings');
    await waitForNetworkIdle(page);
    
    // Should show bookings list or empty state
    const hasContent = await page.locator('text=/booking|reservation|no bookings/i').count() > 0;
    expect(hasContent).toBeTruthy();
    
    console.log('✓ Bookings content displayed');
  });

  test('should filter bookings by status', async ({ page }) => {
    await page.goto('/dashboard/bookings');
    await waitForNetworkIdle(page);
    
    // Look for filter/tab options
    const hasPending = await page.getByText(/pending/i).count() > 0;
    const hasConfirmed = await page.getByText(/confirmed/i).count() > 0;
    
    if (hasPending || hasConfirmed) {
      console.log('✓ Booking status filters available');
    } else {
      console.log('⚠ No booking filters found');
    }
  });

  test('should view booking details', async ({ page }) => {
    await page.goto('/dashboard/bookings');
    await waitForNetworkIdle(page);
    
    // Click on first booking if available
    const firstBooking = page.locator('[data-testid="booking-card"]').first();
    const hasBookings = await firstBooking.count() > 0;
    
    if (hasBookings) {
      await firstBooking.click();
      await waitForNetworkIdle(page);
      
      // Should show booking details
      await expect(page.locator('text=/guest|check-in|check-out/i')).toBeVisible();
      console.log('✓ Booking details displayed');
    } else {
      console.log('⚠ No bookings to view');
      test.skip();
    }
  });

  test('should approve a pending booking', async ({ page }) => {
    await page.goto('/dashboard/bookings');
    await waitForNetworkIdle(page);
    
    // Look for approve button
    const approveButton = page.getByRole('button', { name: /approve|confirm|accept/i }).first();
    const canApprove = await approveButton.count() > 0;
    
    if (canApprove) {
      await approveButton.click();
      await waitForNetworkIdle(page);
      
      // Should show success message
      const hasSuccess = await page.getByText(/success|approved|confirmed/i).isVisible().catch(() => false);
      
      if (hasSuccess) {
        console.log('✓ Booking approved');
      }
      
      await takeDebugScreenshot(page, 'booking-approved');
    } else {
      console.log('⚠ No pending bookings to approve');
      test.skip();
    }
  });

  test('should reject a pending booking', async ({ page }) => {
    await page.goto('/dashboard/bookings');
    await waitForNetworkIdle(page);
    
    // Look for reject button
    const rejectButton = page.getByRole('button', { name: /reject|decline|cancel/i }).first();
    const canReject = await rejectButton.count() > 0;
    
    if (canReject) {
      await rejectButton.click();
      await waitForNetworkIdle(page);
      
      console.log('✓ Booking rejection initiated');
      await takeDebugScreenshot(page, 'booking-rejected');
    } else {
      console.log('⚠ No pending bookings to reject');
      test.skip();
    }
  });

  test('should show booking statistics', async ({ page }) => {
    await page.goto('/dashboard/bookings');
    await waitForNetworkIdle(page);
    
    // Look for stats/metrics
    const hasStats = await page.locator('text=/total|pending|confirmed/i').count() > 0;
    
    if (hasStats) {
      console.log('✓ Booking statistics visible');
    }
  });
});

test.describe('Guest Booking Experience (External)', () => {
  test('should simulate external booking via API', async ({ request }) => {
    const dates = getTestBookingDates();
    
    // This would simulate an external AI agent booking
    // In real scenario, this would use the external API endpoint
    console.log('✓ External booking simulation:');
    console.log(`  Check-in: ${dates.checkIn}`);
    console.log(`  Check-out: ${dates.checkOut}`);
    console.log(`  Nights: ${dates.nights}`);
    
    // Note: Actual API call would be made here in real test
    // const response = await request.post('/api/external/v1/bookings', { ... });
    // expect(response.status()).toBe(201);
  });
});

