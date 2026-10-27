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

test('nút gạt sáng tối đổi nền, nhớ lựa chọn khi tải lại', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	// trên điện thoại nút gạt nằm trong menu thu gọn: mở menu trước
	const moMenu = async () => {
		const nutMenu = page.locator('button.sl-menu-button');
		if (await nutMenu.isVisible()) await nutMenu.click();
	};
	await moMenu();
	const nut = page.locator('button.nut-sang-toi[role="switch"]:visible').first();
	await expect(nut).toHaveAttribute('aria-checked', 'false');
	expect(await page.evaluate(() => getComputedStyle(document.body).backgroundColor)).toBe('rgb(251, 248, 241)');
	await nut.click();
	await expect(nut).toHaveAttribute('aria-checked', 'true');
	await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
	expect(await page.evaluate(() => getComputedStyle(document.body).backgroundColor)).toBe('rgb(20, 23, 28)');
	await page.reload();
	await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
	await moMenu();
	const nut2 = page.locator('button.nut-sang-toi[role="switch"]:visible').first();
	await expect(nut2).toHaveAttribute('aria-checked', 'true');
	await nut2.click();
	await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
	await expect(nut2).toHaveAttribute('aria-checked', 'false');
});

test('trang chủ có nút gạt sáng tối, không còn ô chọn cũ', async ({ page }) => {
	await page.goto('/');
	await expect(page.locator('button.nut-sang-toi[role="switch"]:visible').first()).toBeVisible();
	await expect(page.locator('starlight-theme-select select:visible')).toHaveCount(0);
});
