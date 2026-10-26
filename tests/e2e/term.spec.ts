import { test, expect } from '@playwright/test';

const URL = '/kiem-thu/thanh-phan/';

test('desktop: rê chuột hiện nhắc nhanh', async ({ page }, info) => {
	test.skip(info.project.name !== 'desktop');
	await page.goto(URL);
	const tip = page.locator('.term .tip').first();
	await expect(tip).toBeHidden();
	await page.locator('.term').first().hover();
	await expect(tip).toBeVisible();
	await expect(tip).toContainText('NHẮC NHANH');
	await expect(tip).toContainText('Học kỹ ở Chương 6');
});

test('mobile: chạm bật tooltip trong viewport, chạm h1 thì đóng', async ({ page }, info) => {
	test.skip(info.project.name !== 'mobile');
	await page.goto(URL);
	const term = page.locator('.term').first();
	const tip = term.locator('.tip');
	await term.click();
	await expect(tip).toBeVisible();
	await expect(term).toHaveAttribute('aria-expanded', 'true');
	const box = await tip.boundingBox();
	expect(box!.x).toBeGreaterThanOrEqual(0);
	expect(box!.x + box!.width).toBeLessThanOrEqual(375);
	await page.locator('h1').click();
	await expect(tip).toBeHidden();
});

test('trang Thuật ngữ có mục Đạo hàm, không lộ trang kiểm thử', async ({ page }) => {
	await page.goto('/thuat-ngu/');
	const muc = page.locator('#dao-ham');
	await expect(muc).toContainText('Đạo hàm');
	await expect(muc.locator('a[href*="kiem-thu"]')).toHaveCount(0);
	await expect(page.locator('a[href*="/kiem-thu/"]')).toHaveCount(0);
});
