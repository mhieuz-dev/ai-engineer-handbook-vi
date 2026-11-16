import { test, expect } from '@playwright/test';

test('trang Luyện tập: 5 cách luyện và chủ đề theo chương', async ({ page }) => {
	await page.goto('/luyen-tap/');
	await expect(page.locator('.lt-mode .lt-the')).toHaveCount(5);
	await expect(page.locator('.lt-nhom')).toHaveCount(8);
	expect(await page.locator('.lt-chude a').count()).toBeGreaterThan(20);
	const dau = page.locator('.lt-chude a').first();
	await expect(dau).toHaveAttribute('href', /^\/phong-thi\/\?chu-de=/);
});

test('bấm một chủ đề thì phòng thi tự mở đề đúng chủ đề', async ({ page }) => {
	await page.goto('/luyen-tap/');
	const dau = page.locator('.lt-chude a').first();
	const href = await dau.getAttribute('href');
	await dau.click();
	await expect(page).toHaveURL(new RegExp(href!.replace(/[?]/g, '\\?')));
	await expect(page.locator('.pt-thi')).toBeVisible();
	await expect(page.locator('.pt-setup')).toBeHidden();
	expect(await page.locator('.pt-ds button').count()).toBeGreaterThan(0);
	await expect(page.locator('.pt-dem')).toContainText('Câu 1/');
});

test('phòng thi có lưới chủ đề, bấm là bắt đầu', async ({ page }) => {
	await page.goto('/phong-thi/');
	expect(await page.locator('[data-pt-chude-id]').count()).toBeGreaterThan(20);
	await page.locator('[data-pt-chude-id]').first().click();
	await expect(page.locator('.pt-thi')).toBeVisible();
	await expect(page.locator('.pt-dem')).toContainText('Câu 1/');
});

test('mobile 375px: luyện tập không tràn ngang', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/luyen-tap/');
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);
});
