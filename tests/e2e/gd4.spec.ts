import { test, expect } from '@playwright/test';

async function moSidebar(page: import('@playwright/test').Page) {
	const nut = page.locator('button.sl-menu-button');
	if (await nut.isVisible()) await nut.click();
}

test('trang chương: ô "Chương N · Trang i/n", vạch tiến độ và ô số trang', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	await moSidebar(page);
	const hop = page.locator('.sb-chuong');
	await expect(hop).toContainText('Chương 10');
	await expect(hop).toContainText('Trang 2/6');
	const thanh = hop.getByRole('progressbar');
	await expect(thanh).toHaveAttribute('aria-valuenow', '2');
	await expect(thanh).toHaveAttribute('aria-valuemax', '6');
	await expect(hop.locator('.sb-chuong-o')).toHaveCount(6);
	await expect(hop.locator('.sb-chuong-o.dang-o')).toHaveText('2');
});

test('trang chương: chỉ mở nhánh đang đọc (Nhánh > Phần > Chương)', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	await moSidebar(page);
	const sb = page.locator('#starlight__sidebar');
	await expect(sb.locator('details[open]')).toHaveCount(3);
	const dangMo = await sb.locator('details[open] > summary').allInnerTexts();
	expect(dangMo.join(' ')).toContain('Hồi quy tuyến tính');
	// Phần không chứa trang đang đọc thì gập.
	const phan1 = sb.locator('summary', { hasText: 'Phần I.' }).first().locator('xpath=..');
	await expect(phan1).not.toHaveAttribute('open', '');
});

test('trang luyện tập: sidebar là menu khu, không còn cây chương', async ({ page }) => {
	const cap = [
		['/phong-thi/', 'Luyện tập', 5, '/phong-thi/'],
		['/toan-thuat-toan/', 'Luyện tập', 5, '/toan-thuat-toan/'],
		['/thuat-ngu/', 'Tra cứu', 4, '/thuat-ngu/'],
		['/ho-so/', 'Hồ sơ', 5, '/ho-so/'],
	];
	for (const [url, ten, so, href] of cap) {
		await page.goto(url);
		await moSidebar(page);
		const sb = page.locator('#starlight__sidebar');
		await expect(sb.locator('.sb-khu-nhan'), url).toContainText(ten);
		await expect(sb.locator('.sb-muc'), url).toHaveCount(so);
		await expect(sb.locator('.sb-muc.dang-o')).toHaveAttribute('href', href);
		await expect(sb.locator('.sb-chuong')).toHaveCount(0);
		await expect(sb.locator('details'), url).toHaveCount(0);
	}
});

test('trang công cụ: bỏ cột phải "Trên trang này" khi ít mục, trang chương vẫn giữ', async ({ page, isMobile }) => {
	for (const url of ['/phong-thi/', '/phong-van/', '/thuat-toan/', '/toan-thuat-toan/', '/ho-so/', '/luyen-tap/']) {
		await page.goto(url);
		expect(await page.locator('html').getAttribute('data-has-toc'), url).toBeNull();
		await expect(page.locator('.right-sidebar-container'), url).toHaveCount(0);
	}
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	await expect(page.locator('html')).toHaveAttribute('data-has-toc', '');
	// Điện thoại dùng mục lục gập, máy tính dùng cột phải.
	await expect(page.locator(isMobile ? '#starlight__on-this-page--mobile' : '#starlight__on-this-page')).toBeVisible();
});
