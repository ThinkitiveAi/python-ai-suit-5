import { test, expect } from '@playwright/test';

test.describe('Basic API Integration Tests', () => {
  test('should load enhanced availability page', async ({ page }) => {
    await page.goto('/provider/enhanced-availability');
    
    // Check if the page loads correctly
    await expect(page.locator('h1:has-text("Enhanced Provider Availability Management")')).toBeVisible();
  });

  test('should show availability management interface', async ({ page }) => {
    await page.goto('/provider/enhanced-availability');
    
    // Check for main components
    await expect(page.locator('text=Total Slots')).toBeVisible();
    await expect(page.locator('text=Availability Slots')).toBeVisible();
    await expect(page.locator('text=Appointments')).toBeVisible();
  });

  test('should open add availability modal', async ({ page }) => {
    await page.goto('/provider/enhanced-availability');
    
    // Click add button
    await page.click('button:has-text("Add Availability")');
    
    // Check if modal opens
    await expect(page.locator('h2:has-text("Add Availability Slot")')).toBeVisible();
  });

  test('should handle form submission', async ({ page }) => {
    await page.goto('/provider/enhanced-availability');
    
    // Open modal
    await page.click('button:has-text("Add Availability")');
    
    // Fill basic form
    await page.fill('input[type="date"]', '2024-02-15');
    await page.fill('input[placeholder="09:00"]', '09:00');
    await page.fill('input[placeholder="10:00"]', '10:00');
    
    // Submit form
    await page.click('button:has-text("Create")');
    
    // Modal should close
    await expect(page.locator('h2:has-text("Add Availability Slot")')).not.toBeVisible();
  });

  test('should show refresh functionality', async ({ page }) => {
    await page.goto('/provider/enhanced-availability');
    
    // Click refresh button
    await page.click('button:has-text("Refresh")');
    
    // Page should still be functional
    await expect(page.locator('h1:has-text("Enhanced Provider Availability Management")')).toBeVisible();
  });

  test('should work on different screen sizes', async ({ page }) => {
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/provider/enhanced-availability');
    await expect(page.locator('h1:has-text("Enhanced Provider Availability Management")')).toBeVisible();
    
    // Test desktop view
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/provider/enhanced-availability');
    await expect(page.locator('h1:has-text("Enhanced Provider Availability Management")')).toBeVisible();
  });
}); 