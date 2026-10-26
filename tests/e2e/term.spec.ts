import { test, expect } from '@playwright/test';

const URL = '/kiem-thu/thanh-phan/';

test('desktop: rê chuột hiện nhắc nhanh', async ({ page }, info) => {
	test.skip(info.project.name !== 'desktop');
	await page.goto(URL);
	const tip = page.locator('.term-wrap .tip').first();
	await expect(tip).toBeHidden();
	await page.locator('.term').first().hover();
	await expect(tip).toBeVisible();
	await expect(tip).toContainText('NHẮC NHANH');
	await expect(tip).toContainText('Học kỹ ở Chương 6');
});

test('mobile: chạm mở, chạm lại đóng, chạm ra ngoài đóng', async ({ page }, info) => {
	test.skip(info.project.name !== 'mobile');
	await page.goto(URL);
	const term = page.locator('.term').first();
	const tip = page.locator('.term-wrap .tip').first();
	await term.evaluate((el) => el.scrollIntoView({ block: 'center' }));
	await term.tap();
	await expect(tip).toBeVisible();
	await expect(term).toHaveAttribute('aria-expanded', 'true');
	const box = await tip.boundingBox();
	expect(box!.x).toBeGreaterThanOrEqual(0);
	expect(box!.x + box!.width).toBeLessThanOrEqual(375);
	await term.tap();
	await expect(tip).toBeHidden();
	await term.tap();
	await expect(tip).toBeVisible();
	await page.locator('h1').tap();
	await expect(tip).toBeHidden();
	await expect(term).toHaveAttribute('aria-expanded', 'false');
});

test('mobile: thuật ngữ sát mép phải vẫn nằm trong 375px', async ({ page }, info) => {
	test.skip(info.project.name !== 'mobile');
	await page.goto(URL);
	const wrap = page.locator('.term-wrap').last();
	await wrap.locator('.term').evaluate((el) => el.scrollIntoView({ block: 'center' }));
	await wrap.locator('.term').tap();
	const tip = wrap.locator('.tip');
	await expect(tip).toBeVisible();
	const box = await tip.boundingBox();
	expect(box!.x).toBeGreaterThanOrEqual(0);
	expect(box!.x + box!.width).toBeLessThanOrEqual(375);
});

test('bàn phím: Tab tới link Học kỹ khi tooltip còn mở, Escape đóng', async ({ page }) => {
	await page.goto(URL);
	const wrap = page.locator('.term-wrap').first();
	const tip = wrap.locator('.tip');
	await wrap.locator('.term').focus();
	await expect(tip).toBeVisible();
	await page.keyboard.press('Tab');
	await expect(wrap.getByRole('link', { name: /Học kỹ ở Chương 6/ })).toBeFocused();
	await expect(tip).toBeVisible();
	await page.keyboard.press('Escape');
	await expect(tip).toBeHidden();
	await expect(wrap.locator('.term')).toBeFocused();
	await page.keyboard.press('Enter');
	await expect(tip).toBeVisible();
	await page.keyboard.press('Enter');
	await expect(tip).toBeHidden();
});

test('trang Thuật ngữ có mục Đạo hàm, không lộ trang kiểm thử', async ({ page }) => {
	await page.goto('/thuat-ngu/');
	const muc = page.locator('#dao-ham');
	await expect(muc).toContainText('Đạo hàm');
	await expect(muc.locator('a[href*="kiem-thu"]')).toHaveCount(0);
	await expect(page.locator('a[href*="/kiem-thu/"]')).toHaveCount(0);
});
