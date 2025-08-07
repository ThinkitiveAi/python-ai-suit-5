import { test, expect } from '@playwright/test';

test.describe('API Integration Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
  });

  test.describe('Provider Authentication', () => {
    test('should navigate to provider login', async ({ page }) => {
      // Click on the Provider button in the floating navigation
      await page.locator('button:has-text("Provider")').click();
      
      // Should navigate to provider login page
      await expect(page).toHaveURL(/.*provider-login/);
    });

    test('should login with dummy provider credentials', async ({ page }) => {
      // Navigate to provider login
      await page.goto('/auth/provider-login');
      
      // Fill in dummy credentials
      await page.fill('input[placeholder*="email"]', 'provider@medical.com');
      await page.fill('input[type="password"]', 'password123');
      
      // Click login button
      await page.click('button:has-text("Sign In")');
      
      // Should redirect to provider dashboard or show success
      await expect(page).toHaveURL(/.*provider/);
    });
  });

  test.describe('Enhanced Availability Management', () => {
    test('should navigate to enhanced availability page', async ({ page }) => {
      // Navigate directly to enhanced availability
      await page.goto('/provider/enhanced-availability');
      
      // Should show the enhanced availability component
      await expect(page.locator('h1:has-text("Enhanced Provider Availability Management")')).toBeVisible();
    });

    test('should display availability statistics', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Check for statistics cards
      await expect(page.locator('text=Total Slots')).toBeVisible();
      await expect(page.locator('text=Available')).toBeVisible();
      await expect(page.locator('text=Booked')).toBeVisible();
      await expect(page.locator('text=Appointments')).toBeVisible();
    });

    test('should show availability slots table', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Check for availability table
      await expect(page.locator('h3:has-text("Availability Slots")')).toBeVisible();
      await expect(page.locator('table')).toBeVisible();
    });

    test('should show appointments table', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Check for appointments table
      await expect(page.locator('h3:has-text("Appointments")')).toBeVisible();
      await expect(page.locator('table')).toBeVisible();
    });

    test('should open add availability modal', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Click add availability button
      await page.click('button:has-text("Add Availability")');
      
      // Should open modal
      await expect(page.locator('h2:has-text("Add Availability Slot")')).toBeVisible();
      
      // Check for form fields
      await expect(page.locator('label:has-text("Date")')).toBeVisible();
      await expect(page.locator('label:has-text("Start Time")')).toBeVisible();
      await expect(page.locator('label:has-text("End Time")')).toBeVisible();
      await expect(page.locator('label:has-text("Duration")')).toBeVisible();
      await expect(page.locator('label:has-text("Status")')).toBeVisible();
    });

    test('should fill and submit availability form', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Open add modal
      await page.click('button:has-text("Add Availability")');
      
      // Fill form
      await page.fill('input[type="date"]', '2024-02-15');
      await page.fill('input[placeholder="09:00"]', '09:00');
      await page.fill('input[placeholder="10:00"]', '10:00');
      await page.fill('input[type="number"]', '60');
      await page.selectOption('select', 'available');
      await page.fill('input[placeholder*="Consultation"]', 'Test Consultation');
      await page.fill('textarea', 'Test notes');
      
      // Submit form
      await page.click('button:has-text("Create")');
      
      // Should close modal and show success notification
      await expect(page.locator('h2:has-text("Add Availability Slot")')).not.toBeVisible();
    });

    test('should handle form validation', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Open add modal
      await page.click('button:has-text("Add Availability")');
      
      // Try to submit without required fields
      await page.click('button:has-text("Create")');
      
      // Should show validation errors
      await expect(page.locator('text=required')).toBeVisible();
    });
  });

  test.describe('Appointment Management', () => {
    test('should open create appointment modal from available slot', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Wait for data to load
      await page.waitForTimeout(2000);
      
      // Look for available slot and click the plus button
      const availableSlot = page.locator('tr').filter({ hasText: 'Available' }).first();
      if (await availableSlot.isVisible()) {
        await availableSlot.locator('button[aria-label*="add"]').click();
        
        // Should open appointment modal
        await expect(page.locator('h2:has-text("Create Appointment")')).toBeVisible();
      }
    });

    test('should fill and submit appointment form', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Wait for data to load
      await page.waitForTimeout(2000);
      
      // Look for available slot and click the plus button
      const availableSlot = page.locator('tr').filter({ hasText: 'Available' }).first();
      if (await availableSlot.isVisible()) {
        await availableSlot.locator('button[aria-label*="add"]').click();
        
        // Fill appointment form
        await page.fill('input[placeholder*="Patient"]', 'patient-123');
        await page.fill('input[type="date"]', '2024-02-15');
        await page.fill('input[placeholder="09:00"]', '09:00');
        await page.fill('input[placeholder="10:00"]', '10:00');
        await page.fill('input[placeholder*="Consultation"]', 'Test Appointment');
        await page.fill('textarea[placeholder*="Reason"]', 'Test reason');
        await page.fill('textarea[placeholder*="notes"]', 'Test notes');
        
        // Submit form
        await page.click('button:has-text("Create")');
        
        // Should close modal
        await expect(page.locator('h2:has-text("Create Appointment")')).not.toBeVisible();
      }
    });
  });

  test.describe('CRUD Operations', () => {
    test('should edit availability slot', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Wait for data to load
      await page.waitForTimeout(2000);
      
      // Click edit button on first slot
      const firstSlot = page.locator('tr').nth(1); // Skip header row
      if (await firstSlot.isVisible()) {
        await firstSlot.locator('button[aria-label*="edit"]').click();
        
        // Should open edit modal
        await expect(page.locator('h2:has-text("Edit Availability Slot")')).toBeVisible();
        
        // Modify some fields
        await page.fill('input[placeholder*="Consultation"]', 'Updated Consultation');
        await page.fill('textarea', 'Updated notes');
        
        // Submit changes
        await page.click('button:has-text("Update")');
        
        // Should close modal
        await expect(page.locator('h2:has-text("Edit Availability Slot")')).not.toBeVisible();
      }
    });

    test('should delete availability slot', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Wait for data to load
      await page.waitForTimeout(2000);
      
      // Click delete button on first slot
      const firstSlot = page.locator('tr').nth(1); // Skip header row
      if (await firstSlot.isVisible()) {
        await firstSlot.locator('button[aria-label*="delete"]').click();
        
        // Should open delete confirmation modal
        await expect(page.locator('h2:has-text("Confirm Delete")')).toBeVisible();
        
        // Confirm deletion
        await page.click('button:has-text("Delete")');
        
        // Should close modal
        await expect(page.locator('h2:has-text("Confirm Delete")')).not.toBeVisible();
      }
    });

    test('should edit appointment', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Wait for data to load
      await page.waitForTimeout(2000);
      
      // Click edit button on first appointment
      const firstAppointment = page.locator('tr').filter({ hasText: 'patient' }).first();
      if (await firstAppointment.isVisible()) {
        await firstAppointment.locator('button[aria-label*="edit"]').click();
        
        // Should open edit modal
        await expect(page.locator('h2:has-text("Edit Appointment")')).toBeVisible();
        
        // Modify some fields
        await page.fill('input[placeholder*="Consultation"]', 'Updated Appointment');
        await page.fill('textarea[placeholder*="Reason"]', 'Updated reason');
        
        // Submit changes
        await page.click('button:has-text("Update")');
        
        // Should close modal
        await expect(page.locator('h2:has-text("Edit Appointment")')).not.toBeVisible();
      }
    });

    test('should delete appointment', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Wait for data to load
      await page.waitForTimeout(2000);
      
      // Click delete button on first appointment
      const firstAppointment = page.locator('tr').filter({ hasText: 'patient' }).first();
      if (await firstAppointment.isVisible()) {
        await firstAppointment.locator('button[aria-label*="delete"]').click();
        
        // Should open delete confirmation modal
        await expect(page.locator('h2:has-text("Confirm Delete")')).toBeVisible();
        
        // Confirm deletion
        await page.click('button:has-text("Delete")');
        
        // Should close modal
        await expect(page.locator('h2:has-text("Confirm Delete")')).not.toBeVisible();
      }
    });
  });

  test.describe('Error Handling', () => {
    test('should handle network errors gracefully', async ({ page }) => {
      // Mock network failure
      await page.route('**/api/**', route => route.abort());
      
      await page.goto('/provider/enhanced-availability');
      
      // Should still show the component with error handling
      await expect(page.locator('h1:has-text("Enhanced Provider Availability Management")')).toBeVisible();
    });

    test('should show loading states', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Click refresh button
      await page.click('button:has-text("Refresh")');
      
      // Should show loading state
      await expect(page.locator('button:has-text("Refresh")')).toHaveAttribute('data-loading', 'true');
    });
  });

  test.describe('Responsive Design', () => {
    test('should work on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      
      await page.goto('/provider/enhanced-availability');
      
      // Should still be functional
      await expect(page.locator('h1:has-text("Enhanced Provider Availability Management")')).toBeVisible();
      
      // Tables should be scrollable on mobile
      await expect(page.locator('.mantine-ScrollArea-root')).toBeVisible();
    });

    test('should work on tablet viewport', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      
      await page.goto('/provider/enhanced-availability');
      
      // Should still be functional
      await expect(page.locator('h1:has-text("Enhanced Provider Availability Management")')).toBeVisible();
    });
  });

  test.describe('Theme Integration', () => {
    test('should use new violet theme colors', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Check for violet theme colors in buttons
      const addButton = page.locator('button:has-text("Add Availability")');
      await expect(addButton).toHaveCSS('background', /linear-gradient.*8b5cf6/);
    });

    test('should have modern styling', async ({ page }) => {
      await page.goto('/provider/enhanced-availability');
      
      // Check for modern card styling
      const cards = page.locator('.mantine-Card-root');
      await expect(cards.first()).toHaveCSS('border-radius', '12px');
      await expect(cards.first()).toHaveCSS('box-shadow');
    });
  });
}); 