/**
 * Test data and utilities for E2E tests
 */

export const TEST_USERS = {
  host: {
    email: 'mahmoudomarus@gmail.com',
    password: process.env.TEST_USER_PASSWORD || 'test-password-change-me',
    name: 'Test Host',
  },
  guest: {
    email: 'guest@test.com',
    password: 'test-guest-password',
    name: 'Test Guest',
  },
};

export const TEST_PROPERTY = {
  title: `E2E Test Property ${Date.now()}`,
  description: 'Beautiful test property for automated testing',
  property_type: 'apartment',
  address: '123 Test Street',
  city: 'Dubai',
  state: 'Dubai',
  zipcode: '00000',
  bedrooms: 2,
  bathrooms: 2,
  max_guests: 4,
  price_per_night: 500,
  amenities: ['wifi', 'parking', 'pool'],
};

export const TEST_BOOKING = {
  guests: 2,
  special_requests: 'E2E test booking - please ignore',
};

/**
 * Get dates for booking (7 days from now, 5 night stay)
 */
export function getTestBookingDates() {
  const checkIn = new Date();
  checkIn.setDate(checkIn.getDate() + 7);
  
  const checkOut = new Date(checkIn);
  checkOut.setDate(checkOut.getDate() + 5);
  
  return {
    checkIn: checkIn.toISOString().split('T')[0],
    checkOut: checkOut.toISOString().split('T')[0],
    nights: 5,
  };
}

/**
 * Generate unique test email
 */
export function generateTestEmail() {
  return `test-${Date.now()}@krib-test.com`;
}

/**
 * Wait for network to be idle
 */
export async function waitForNetworkIdle(page: any, timeout = 5000) {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Take screenshot for debugging
 */
export async function takeDebugScreenshot(page: any, name: string) {
  await page.screenshot({ path: `test-results/${name}-${Date.now()}.png`, fullPage: true });
}

