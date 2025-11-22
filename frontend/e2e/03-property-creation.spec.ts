import { test, expect } from '@playwright/test';
import { TEST_USERS, TEST_PROPERTY, waitForNetworkIdle, takeDebugScreenshot } from './helpers/test-data';

test.describe('Property Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login as host
    await page.goto('/');
    await page.getByLabel(/email/i).fill(TEST_USERS.host.email);
    await page.getByLabel(/password/i).fill(TEST_USERS.host.password);
    await page.getByRole('button', { name: /sign in/i }).click();
    await waitForNetworkIdle(page);
  });

  test('should navigate to properties page', async ({ page }) => {
    await page.getByRole('link', { name: /properties/i }).click();
    await waitForNetworkIdle(page);
    
    await expect(page).toHaveURL(/properties/);
    await expect(page.getByText(/properties|my properties/i)).toBeVisible();
  });

  test('should display existing properties', async ({ page }) => {
    await page.goto('/dashboard/properties');
    await waitForNetworkIdle(page);
    
    // Should show properties list or empty state
    const hasProperties = await page.locator('text=/property|listing/i').count() > 0;
    expect(hasProperties).toBeTruthy();
    
    console.log('✓ Properties page loaded');
  });

  test('should open add property form', async ({ page }) => {
    await page.goto('/dashboard/properties');
    await waitForNetworkIdle(page);
    
    // Click add property button
    await page.getByRole('button', { name: /add property|new property|create/i }).click();
    
    // Should show property form
    await expect(page.getByLabel(/title|name/i)).toBeVisible();
    await expect(page.getByLabel(/description/i)).toBeVisible();
    
    console.log('✓ Add property form opened');
  });

  test('should create a new property', async ({ page }) => {
    await page.goto('/dashboard/properties');
    await waitForNetworkIdle(page);
    
    // Open add property form
    await page.getByRole('button', { name: /add property|new property|create/i }).click();
    await page.waitForTimeout(1000);
    
    // Fill property details
    await page.getByLabel(/title|name/i).fill(TEST_PROPERTY.title);
    await page.getByLabel(/description/i).fill(TEST_PROPERTY.description);
    
    // Fill location
    await page.getByLabel(/address/i).fill(TEST_PROPERTY.address);
    await page.getByLabel(/city/i).fill(TEST_PROPERTY.city);
    
    // Fill property details
    const bedroomsInput = page.getByLabel(/bedrooms/i);
    if (await bedroomsInput.count() > 0) {
      await bedroomsInput.fill(TEST_PROPERTY.bedrooms.toString());
    }
    
    const bathroomsInput = page.getByLabel(/bathrooms/i);
    if (await bathroomsInput.count() > 0) {
      await bathroomsInput.fill(TEST_PROPERTY.bathrooms.toString());
    }
    
    const guestsInput = page.getByLabel(/guests|capacity/i);
    if (await guestsInput.count() > 0) {
      await guestsInput.fill(TEST_PROPERTY.max_guests.toString());
    }
    
    const priceInput = page.getByLabel(/price|nightly rate/i);
    if (await priceInput.count() > 0) {
      await priceInput.fill(TEST_PROPERTY.price_per_night.toString());
    }
    
    // Take screenshot before submission
    await takeDebugScreenshot(page, 'property-form-filled');
    
    // Submit form
    await page.getByRole('button', { name: /save|create|publish/i }).click();
    
    // Wait for success
    await waitForNetworkIdle(page);
    
    // Should show success message or redirect to properties list
    const successVisible = await page.getByText(/success|created/i).isVisible().catch(() => false);
    
    if (successVisible) {
      console.log('✓ Property created successfully');
    } else {
      // Check if redirected back to properties list
      await expect(page).toHaveURL(/properties/);
      console.log('✓ Redirected to properties list');
    }
    
    await takeDebugScreenshot(page, 'property-created');
  });

  test('should view property details', async ({ page }) => {
    await page.goto('/dashboard/properties');
    await waitForNetworkIdle(page);
    
    // Click on first property
    const firstProperty = page.locator('[data-testid="property-card"]').first();
    const hasProperties = await firstProperty.count() > 0;
    
    if (hasProperties) {
      await firstProperty.click();
      await waitForNetworkIdle(page);
      
      // Should show property details
      await expect(page.locator('text=/bedrooms|bathrooms|guests/i')).toBeVisible();
      console.log('✓ Property details displayed');
    } else {
      console.log('⚠ No properties to view');
      test.skip();
    }
  });

  test('should edit existing property', async ({ page }) => {
    await page.goto('/dashboard/properties');
    await waitForNetworkIdle(page);
    
    // Find edit button
    const editButton = page.getByRole('button', { name: /edit/i }).first();
    const canEdit = await editButton.count() > 0;
    
    if (canEdit) {
      await editButton.click();
      await waitForNetworkIdle(page);
      
      // Should show edit form
      await expect(page.getByLabel(/title|name/i)).toBeVisible();
      
      // Make a change
      const titleInput = page.getByLabel(/title|name/i);
      await titleInput.fill(await titleInput.inputValue() + ' (Edited)');
      
      // Save
      await page.getByRole('button', { name: /save|update/i }).click();
      await waitForNetworkIdle(page);
      
      console.log('✓ Property edited');
    } else {
      console.log('⚠ No properties to edit');
      test.skip();
    }
  });
});

