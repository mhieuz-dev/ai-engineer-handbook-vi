import { test, expect } from '@playwright/test';

type Trang = import('@playwright/test').Page;
const C10 = '/ai-engineer/ch10-hoi-quy-tuyen-tinh';
const SLUG = 'ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan';

// Sidebar mobile của Starlight là popover, không có aria-expanded.
const mo = (page: Trang) => page.evaluate(() => !!document.querySelector('#starlight__sidebar:popover-open'));

async function moSidebar(page: Trang) {
	const nutMenu = page.locator('button.sl-menu-button');
	if ((await nutMenu.isVisible()) && !(await mo(page))) await bam(page, nutMenu);
}

async function bam(page: Trang, loc: import('@playwright/test').Locator) {
	if (await page.evaluate(() => navigator.maxTouchPoints > 0)) await loc.tap();
	else await loc.click();
}
async function dongSidebar(page: Trang) {
	const nutMenu = page.locator('button.sl-menu-button');
	if ((await nutMenu.isVisible()) && (await mo(page))) await bam(page, nutMenu);
}

test('nút Đã đọc: bấm, tải lại, bấm lại, cập nhật sidebar ngay', async ({ page }) => {
	await page.goto(`${C10}/02-toan/`);
	await page.evaluate(() => (window as any).__chuaTai = true);
	const nut = page.locator('.nut-da-doc');
	const link = page.locator(`a[data-slug="${SLUG}"]`);

	await expect(nut).toContainText('Chưa đọc');
	await expect(nut).toHaveAttribute('aria-pressed', 'false');
	await moSidebar(page);
	await expect(link).not.toContainText('✓');
	await expect(page.locator('.td-pt')).toHaveText('0%');

	await dongSidebar(page);
	await bam(page, nut);
	await moSidebar(page);
	await expect(nut).toContainText('Đã đọc');
	await expect(nut).toHaveAttribute('aria-pressed', 'true');
	await expect(link).toContainText('✓');
	const pt = parseInt((await page.locator('.td-pt').textContent()) ?? '0', 10);
	expect(pt).toBeGreaterThan(0);
	expect(await page.evaluate(() => (window as any).__chuaTai)).toBe(true);

	await page.reload();
	await expect(page.locator('.nut-da-doc')).toContainText('Đã đọc');

	await dongSidebar(page);
	await bam(page, page.locator('.nut-da-doc'));
	await expect(page.locator('.nut-da-doc')).toContainText('Chưa đọc');
	await expect(page.locator('.nut-da-doc')).toHaveAttribute('aria-pressed', 'false');
	await moSidebar(page);
	await expect(link).not.toContainText('✓');
	await expect(page.locator('.td-pt')).toHaveText('0%');
});

test('trang ngoài chương không có nút nhưng vẫn ghi ngày học', async ({ page }) => {
	await page.goto('/thuat-ngu/');
	await expect(page.locator('h1')).toBeVisible();
	await expect(page.locator('.nut-da-doc')).toHaveCount(0);
	await moSidebar(page);
	await expect(page.locator('.td-chuoi')).toContainText('1 ngày học liên tiếp');
});

test('mở trang chương không tự đánh dấu đã đọc, chuỗi ngày là 1', async ({ page }) => {
	await page.goto(`${C10}/01-truc-giac/`);
	await moSidebar(page);
	await expect(page.locator('.td-chuoi')).toContainText('🔥 1 ngày học liên tiếp');
	await expect(page.locator('.td-pt')).toHaveText('0%');
});
