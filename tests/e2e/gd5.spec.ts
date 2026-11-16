import { test, expect } from '@playwright/test';
import { PHAN, CHUONG, chuongDaXuatBan } from '../../src/data/chuong';

test('trang chủ: hero có câu giới thiệu, hai nút và thanh tiến độ', async ({ page }) => {
	await page.goto('/');
	await expect(page.locator('.hero-dan')).toContainText('năm bước');
	const nut = page.locator('.hero-nut a');
	await expect(nut).toHaveCount(2);
	await expect(nut.nth(0)).toContainText('Bắt đầu từ Chương 0');
	await expect(nut.nth(0)).toHaveAttribute('href', /\/ai-engineer\/ch00-lo-trinh-va-colab\/01-lo-trinh\/$/);
	await expect(nut.nth(1)).toContainText('Xem lộ trình');
	await expect(nut.nth(1)).toHaveAttribute('href', '#cac-phan-ten');
	await expect(page.locator('.tdt-thanh')).toHaveAttribute(
		'aria-valuenow',
		String(Math.round((chuongDaXuatBan().length / CHUONG.length) * 100)),
	);
});

test('trang chủ: ba thẻ lối vào có màu khu, icon và ba lối tắt', async ({ page }) => {
	await page.goto('/');
	const the = page.locator('.lv-the');
	await expect(the).toHaveCount(3);
	for (const [i, lop, href] of [
		[0, 'lv-hoc', '/lo-trinh/'],
		[1, 'lv-luyen', '/luyen-tap/'],
		[2, 'lv-tra', '/thuat-ngu/'],
	] as const) {
		const t = the.nth(i);
		await expect(t).toHaveClass(new RegExp(lop));
		await expect(t.locator('.lv-nhan svg')).toHaveCount(1);
		await expect(t.locator('.lv-ds a')).toHaveCount(3);
		await expect(t.locator('.lv-vao')).toHaveAttribute('href', href);
		// Viền trên đổi theo màu khu.
		expect(await t.evaluate((e) => getComputedStyle(e).borderTopWidth)).toBe('3px');
	}
});

test('trang chủ: lộ trình theo Phần là một cột dọc có dòng thời gian', async ({ page }) => {
	await page.goto('/');
	const xs = await page.locator('.the-phan').evaluateAll((els) => [...new Set(els.map((e) => Math.round(e.getBoundingClientRect().x)))]);
	expect(xs.length).toBe(1);
	await expect(page.locator('.the-phan')).toHaveCount(PHAN.length);
	const nen = await page.locator('.luoi-phan').evaluate((e) => getComputedStyle(e, '::before').content);
	expect(nen).not.toBe('none');
});

test('trang chủ: bỏ khối luyện tập 5 thẻ và liên kết nhanh cũ, giữ kệ sách', async ({ page }) => {
	await page.goto('/');
	await expect(page.locator('.luyen-tap')).toHaveCount(0);
	await expect(page.locator('.nav-chung-mobile')).toHaveCount(0);
	await expect(page.locator('#ke-sach')).toBeVisible();
	const rong = await page.locator('.ke-sach-wrap').evaluate((e) => e.getBoundingClientRect().width);
	expect(rong).toBeLessThanOrEqual(640);
});

test('lộ trình dùng chung component với trang chủ: 65 dòng và đủ neo #chNN', async ({ page }) => {
	await page.goto('/lo-trinh/');
	await expect(page.locator('li[id^="ch"]')).toHaveCount(CHUONG.length);
	await expect(page.locator('.the-phan')).toHaveCount(PHAN.length);
	await expect(page.locator('li#ch01 a')).toHaveAttribute('href', '/ai-engineer/ch01-python-tu-dau/01-bien-va-kieu/');
	await expect(page.locator('li#ch64')).toContainText('Phỏng vấn và portfolio');
});
