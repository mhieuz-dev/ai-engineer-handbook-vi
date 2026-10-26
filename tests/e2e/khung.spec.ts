import { test, expect } from '@playwright/test';

test('trang chủ có tên site và lang vi', async ({ page }) => {
	await page.goto('/');
	await expect(page).toHaveTitle(/AI & Robotics/);
	await expect(page.locator('html')).toHaveAttribute('lang', 'vi');
});

test('đầu trang không có biểu tượng GitHub', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	await expect(page.locator('header a[href*="github.com"]')).toHaveCount(0);
});

test('nút đổi sáng tối đổi nền', async ({ page }) => {
	await page.goto('/');
	const nenSang = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
	// trên điện thoại ThemeSelect nằm trong menu thu gọn: mở menu trước
	const nutMenu = page.locator('button.sl-menu-button');
	if (await nutMenu.isVisible()) await nutMenu.click();
	// chọn chế độ tối qua ThemeSelect của Starlight
	await page.locator('starlight-theme-select select:visible').first().selectOption('dark');
	const nenToi = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
	expect(nenSang).toBe('rgb(251, 248, 241)');
	expect(nenToi).toBe('rgb(20, 23, 28)');
});
