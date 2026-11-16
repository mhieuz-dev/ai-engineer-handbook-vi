import { test, expect } from '@playwright/test';

test('thuật ngữ: thanh A–Z dính đầu trang, đủ 26 chữ và nút Tất cả', async ({ page }) => {
	await page.goto('/thuat-ngu/');
	const thanh = page.locator('.tn-loc');
	await expect(thanh).toBeVisible();
	expect(await thanh.evaluate((e) => getComputedStyle(e).position)).toBe('sticky');
	await expect(thanh.locator('[data-tn-chu]')).toHaveCount(27); // Tất cả + 26 chữ (không có mục bắt đầu bằng #)
	await expect(thanh.locator('[data-tn-chu=""]')).toHaveAttribute('aria-pressed', 'true');
	await expect(thanh.locator('[data-tn-chu="Z"]')).toBeDisabled();
});

test('thuật ngữ: chọn một chữ cái thì chỉ còn mục chữ đó', async ({ page }) => {
	await page.goto('/thuat-ngu/');
	const tong = Number(await page.locator('[data-tn-so]').textContent());
	await page.locator('[data-tn-chu="D"]').click();
	await expect(page.locator('[data-tn-chu="D"]')).toHaveAttribute('aria-pressed', 'true');
	const hien = page.locator('.muc:visible');
	expect(await hien.count()).toBeGreaterThan(0);
	expect(await hien.evaluateAll((els) => [...new Set(els.map((e) => (e as HTMLElement).dataset.chu))])).toEqual(['D']);
	const so = Number(await page.locator('[data-tn-so]').textContent());
	expect(so).toBeLessThan(tong);
	await expect(page.locator('#dao-ham')).toBeVisible();
	await expect(page.locator('.nhom-chu:visible')).toHaveCount(1);
	await page.locator('[data-tn-chu=""]').click();
	await expect(page.locator('.muc:visible')).toHaveCount(tong);
});

test('thuật ngữ: gõ không dấu vẫn ra kết quả, không có thì báo rỗng', async ({ page }) => {
	await page.goto('/thuat-ngu/');
	const o = page.locator('[data-tn-tim]');
	await o.fill('dao ham');
	await expect(page.locator('.muc:visible').first()).toContainText('Đạo hàm');
	await expect(page.locator('#dao-ham')).toBeVisible();
	expect(Number(await page.locator('[data-tn-so]').textContent())).toBeGreaterThanOrEqual(1);
	await o.fill('khong-co-thuat-ngu-nao');
	await expect(page.locator('.tn-trong')).toBeVisible();
	await expect(page.locator('[data-tn-so]')).toHaveText('0');
	await o.press('Escape');
	await expect(page.locator('.tn-trong')).toBeHidden();
});

test('thuật ngữ: lọc theo Phần', async ({ page }) => {
	await page.goto('/thuat-ngu/');
	const sel = page.locator('[data-tn-phan]');
	await expect(sel.locator('option')).not.toHaveCount(1);
	const giaTri = await sel.locator('option').nth(1).getAttribute('value');
	await sel.selectOption(giaTri!);
	const hien = page.locator('.muc:visible');
	expect(await hien.count()).toBeGreaterThan(0);
	expect(await hien.evaluateAll((els) => [...new Set(els.map((e) => (e as HTMLElement).dataset.phan))])).toEqual([giaTri]);
});

test('thuật ngữ: mục lục phải là A–Z', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/thuat-ngu/');
	const toc = page.locator('.toc-az');
	await expect(toc).toBeVisible();
	await expect(toc.locator('h2')).toHaveText('A–Z');
	await expect(toc.locator('a[href^="#chu-"]')).not.toHaveCount(0);
	await expect(toc.locator('a', { hasText: 'A' }).first()).toHaveAttribute('href', '#chu-a');
});

test('thuật ngữ: vào #chu-d thì chọn sẵn chữ D', async ({ page }) => {
	await page.goto('/thuat-ngu/#chu-d');
	await expect(page.locator('[data-tn-chu="D"]')).toHaveAttribute('aria-pressed', 'true');
	expect(await page.locator('.muc:visible').evaluateAll((els) => [...new Set(els.map((e) => (e as HTMLElement).dataset.chu))])).toEqual(['D']);
});
