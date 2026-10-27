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
	// thẻ nhánh vẫn còn tên nhánh, chỉ ẩn con số
	await moSidebar(page);
	await expect(page.locator('.the-nhanh')).toContainText('AI Engineer');
	expect(loi).toEqual([]);
});

test('thẻ nhánh đầu sidebar hiện tiến độ thật và chuỗi ngày, nằm trên nhãn Menu', async ({ page }) => {
	await page.addInitScript(() => {
		if (sessionStorage.getItem('da-gieo')) return;
		sessionStorage.setItem('da-gieo', '1');
		const p = (n: number) => String(n).padStart(2, '0');
		const homQua = new Date();
		homQua.setDate(homQua.getDate() - 1);
		const ngay = `${homQua.getFullYear()}-${p(homQua.getMonth() + 1)}-${p(homQua.getDate())}`;
		localStorage.setItem('air-tien-do-v1', JSON.stringify({ daDoc: { 'ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac': ngay }, ngayHoc: [ngay] }));
	});
	await page.goto(`${C10}/02-toan/`);
	await moSidebar(page);
	const the = page.locator('.the-nhanh');
	await expect(the).toBeVisible();
	await expect(the.locator('.tn-o')).toHaveText('AI');
	await expect(the).toContainText('AI Engineer');
	await expect(the.locator('.td-nhan')).toHaveText(/^Tiến độ [1-9]\d?% · 2 ngày liên tiếp$/);
	expect(Number(await the.locator('[role="progressbar"]').getAttribute('aria-valuenow'))).toBeGreaterThan(0);
	const yThe = (await the.boundingBox())!.y;
	const yNhan = (await page.locator('.sb-nhan').boundingBox())!.y;
	const yCay = (await page.locator('a[data-slug]').first().boundingBox())!.y;
	expect(yThe).toBeLessThan(yNhan);
	expect(yNhan).toBeLessThan(yCay);
	await expect(page.locator('.sidebar-content .tien-do')).toHaveCount(1);
});
