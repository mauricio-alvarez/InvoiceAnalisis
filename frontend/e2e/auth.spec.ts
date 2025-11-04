import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should display login page', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('h1')).toContainText('Welcome Back');
  });

  test('should display register page', async ({ page }) => {
    await page.goto('/register');
    await expect(page.locator('h1')).toContainText('Create Account');
  });
});
