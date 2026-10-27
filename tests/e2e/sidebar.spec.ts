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
	await expect(muc).toBeVisible();
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

test('Phần chưa có chương xong thu gọn kèm đếm, Phần có chương xong mở sẵn', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/');
	await moSidebar(page);
	const sb = page.locator('nav.sidebar, #starlight__sidebar').first();
	const phan3 = sb.locator('summary', { hasText: 'Phần III. Deep Learning' }).locator('xpath=..');
	await expect(phan3).not.toHaveAttribute('open', '');
	await expect(phan3.locator('summary')).toContainText(/· \d+ chương sắp có/);
	const phan2 = sb.locator('summary', { hasText: 'Phần II. Machine Learning cổ điển' }).locator('xpath=..');
	await expect(phan2).toHaveAttribute('open', '');
});

test('desktop: sidebar là thẻ nổi bo góc, mục đang đọc là viên trắng có chấm', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	const the = page.locator('.sidebar-content');
	expect(parseFloat(await the.evaluate((e) => getComputedStyle(e).borderTopLeftRadius))).toBeGreaterThanOrEqual(12);
	expect(await the.evaluate((e) => getComputedStyle(e).boxShadow)).not.toBe('none');
	await expect(the.locator('.sb-nhan')).toHaveText(/menu · chương trình/i);
	const dangDoc = the.locator('a[aria-current="page"]');
	await expect(dangDoc).toHaveText('Toán từng bước');
	expect(await dangDoc.evaluate((e) => getComputedStyle(e).backgroundColor)).toBe('rgb(255, 255, 255)');
	expect(await dangDoc.evaluate((e) => getComputedStyle(e, '::before').content)).toBe('""');
	// không có ba chấm cửa sổ kiểu macOS
	await expect(page.locator('.sidebar-content [class*="cham"], .sidebar-content [class*="dot"]')).toHaveCount(0);
});

test('desktop: nút ‹ thu gọn sidebar, nhớ khi tải lại, mở lại bằng bàn phím', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	const nut = page.getByRole('button', { name: 'Thu gọn mục lục' });
	const the = page.locator('.sidebar-content');
	const trai = () => page.locator('main').evaluate((e) => e.getBoundingClientRect().left);
	await expect(nut).toHaveAttribute('aria-expanded', 'true');
	await expect(nut).toHaveAttribute('aria-controls', 'starlight__sidebar');
	await expect(the).toBeVisible();
	const traiTruoc = await trai();
	await nut.click();
	const nutMo = page.getByRole('button', { name: 'Mở mục lục' });
	await expect(nutMo).toHaveAttribute('aria-expanded', 'false');
	await expect(the).toBeHidden();
	expect(await trai()).toBeLessThan(traiTruoc - 100);
	await page.reload();
	await expect(nutMo).toHaveAttribute('aria-expanded', 'false');
	await expect(the).toBeHidden();
	await expect(nutMo).toBeVisible();
	await nutMo.focus();
	await page.keyboard.press('Enter');
	await expect(nut).toHaveAttribute('aria-expanded', 'true');
	await expect(the).toBeVisible();
	await page.reload();
	await expect(the).toBeVisible();
	await expect(nut).toHaveAttribute('aria-expanded', 'true');
});

test('mobile: không có nút thu gọn, menu ☰ vẫn mở sidebar', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.addInitScript(() => localStorage.setItem('air-sidebar-thu-gon', '1'));
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	await expect(page.locator('.nut-thu-gon')).toBeHidden();
	await page.locator('button.sl-menu-button').tap();
	await expect(page.locator('.sidebar-content a[aria-current="page"]')).toBeVisible();
});
