import { test, expect } from '@playwright/test';

async function moSidebar(page: import('@playwright/test').Page) {
	// trên điện thoại sidebar nằm trong menu thu gọn
	const nutMenu = page.locator('button.sl-menu-button');
	if (await nutMenu.isVisible()) await nutMenu.click();
}

test('sidebar có Phần II và chương 11 chỉ là nhãn Sắp có', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/');
	await moSidebar(page);
	const sb = page.locator('nav.sidebar, #starlight__sidebar').first();
	await expect(sb.getByText('Phần II. Machine Learning cổ điển')).toBeVisible();
	const muc = sb.locator('[aria-disabled="true"]', { hasText: 'Hồi quy logistic' });
	await expect(muc).toContainText('Sắp có');
	await expect(sb.locator('a', { hasText: 'Hồi quy logistic' })).toHaveCount(0);
});

test('trang cuối chương 10 không có Tiếp trỏ tới ch11', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/06-bai-tap/');
	await expect(page.locator('a[href*="ch11"]')).toHaveCount(0);
	await expect(page.locator('a[rel="next"]')).toHaveCount(0);
});

test('các trang chương 10 xếp 01..06 và có data-slug', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/');
	await moSidebar(page);
	const links = page.locator('a[data-slug^="ai-engineer/ch10-hoi-quy-tuyen-tinh/"]');
	const slugs = await links.evaluateAll((as) => as.map((a) => (a as HTMLElement).dataset.slug));
	expect(slugs).toEqual(['01-truc-giac','02-toan','03-tinh-tay','04-code','05-doc-ket-qua','06-bai-tap'].map((s) => `ai-engineer/ch10-hoi-quy-tuyen-tinh/${s}`));
});
