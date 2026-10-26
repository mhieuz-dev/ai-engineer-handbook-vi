import { test, expect } from '@playwright/test';

const C10 = '/ai-engineer/ch10-hoi-quy-tuyen-tinh';

async function moSidebar(page: import('@playwright/test').Page) {
	const nutMenu = page.locator('button.sl-menu-button');
	if (await nutMenu.isVisible()) await nutMenu.click();
}

test('mở trang không tự ✓; chỉ ✓ sau khi bấm Đã đọc ở trang 01', async ({ page }) => {
	await page.goto(`${C10}/01-truc-giac/`);
	await page.goto(`${C10}/02-toan/`);
	await moSidebar(page);
	const link = page.locator('a[data-slug="ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac"]');
	await expect(link).not.toContainText('✓');
	await expect(page.locator('.td-pt')).toHaveText('0%');
	await page.goto(`${C10}/01-truc-giac/`);
	if (await page.evaluate(() => navigator.maxTouchPoints > 0)) await page.locator('.nut-da-doc').tap();
	else await page.locator('.nut-da-doc').click();
	await page.goto(`${C10}/02-toan/`);
	await moSidebar(page);
	await expect(link).toContainText('✓');
	const pt = await page.locator('.td-pt').textContent();
	expect(parseInt(pt ?? '0', 10)).toBeGreaterThan(0);
});

test('JSON hỏng trong storage: trang vẫn tải, không pageerror', async ({ page }) => {
	const loi: Error[] = [];
	page.on('pageerror', (e) => loi.push(e));
	await page.addInitScript(() => localStorage.setItem('air-tien-do-v1', '{hỏng'));
	await page.goto(`${C10}/01-truc-giac/`);
	await expect(page.locator('h1')).toBeVisible();
	expect(loi).toEqual([]);
});

test('storage ném lỗi: không pageerror, khối tiến độ ẩn', async ({ page }) => {
	const loi: Error[] = [];
	page.on('pageerror', (e) => loi.push(e));
	await page.addInitScript(() => {
		// chỉ chặn khoá của tiến độ: script theme/sidebar của Starlight cũng đọc storage và tự nó không bọc try/catch
		const goc = Storage.prototype.getItem;
		Storage.prototype.getItem = function (k: string) {
			if (k === 'air-tien-do-v1') throw new Error('blocked');
			return goc.call(this, k);
		};
	});
	await page.goto(`${C10}/01-truc-giac/`);
	await expect(page.locator('h1')).toBeVisible();
	await expect(page.locator('.tien-do')).toBeHidden();
	expect(loi).toEqual([]);
});
