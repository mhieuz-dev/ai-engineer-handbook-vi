import { test, expect } from '@playwright/test';

const CHUONG = '/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/';

test('điện thoại: trang chủ có nút ☰, mở ra ba nhóm và Hồ sơ', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/');
	const nut = page.locator('[data-mdd-nut]');
	await expect(nut).toBeVisible();
	await expect(nut).toHaveAttribute('aria-expanded', 'false');
	await expect(page.locator('button.sl-menu-button')).toHaveCount(0);

	await nut.tap();
	await expect(nut).toHaveAttribute('aria-expanded', 'true');
	const bang = page.locator('#mdd-bang');
	await expect(bang).toBeVisible();
	await expect(bang.locator('.mdd-nhom')).toHaveCount(3);
	await expect(bang.locator('.mdd-nhom-ten')).toHaveText([/Học/, /Luyện tập/, /Tra cứu/]);
	await expect(bang.locator('.mdd-hoso')).toHaveAttribute('href', '/ho-so/');
	await expect(bang.locator('[data-mdd-pt]')).toHaveText('0%');
	await expect(bang.getByRole('link', { name: /Luyện thuật toán/ })).toHaveAttribute('href', '/thuat-toan/');
	await expect(bang.getByRole('link', { name: /Toán cho thuật toán/ })).toHaveAttribute('href', '/toan-thuat-toan/');

	await page.keyboard.press('Escape');
	await expect(bang).toBeHidden();
	await expect(nut).toHaveAttribute('aria-expanded', 'false');
});

test('điện thoại: bấm một mục trong menu thì đóng và đi tới trang đó', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/');
	await page.locator('[data-mdd-nut]').tap();
	await page.locator('#mdd-bang').getByRole('link', { name: /Luyện thuật toán/ }).tap();
	await expect(page).toHaveURL(/\/thuat-toan\/$/);
	await expect(page.locator('h1')).toContainText('Luyện thuật toán');
});

test('điện thoại: trang chương chỉ có một nút menu (của Starlight), không lặp thêm', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto(CHUONG);
	await expect(page.locator('[data-mdd-nut]')).toHaveCount(0);
	await expect(page.locator('button.sl-menu-button')).toHaveCount(1);
});

test('điện thoại: nút ☰ không đè ô tìm kiếm', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/');
	const tim = page.locator('header button[data-open-modal]');
	const nut = page.locator('[data-mdd-nut]');
	const oTim = (await tim.boundingBox())!;
	const oNut = (await nut.boundingBox())!;
	expect(oTim.x + oTim.width).toBeLessThanOrEqual(oNut.x + 1);
});

test('bìa Robotics trên điện thoại: ảnh phủ đúng khung 2:3, không cắt chữ', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/');
	const bia = page.locator('#ke-sach .bia-robotics');
	await expect(bia).toBeVisible();
	const hop = (await bia.boundingBox())!;
	const anh = (await bia.locator('img').boundingBox())!;
	expect(Math.abs(hop.width - anh.width)).toBeLessThanOrEqual(1);
	expect(Math.abs(hop.height - anh.height)).toBeLessThanOrEqual(1);
	expect(Math.abs(hop.width / hop.height - 2 / 3)).toBeLessThan(0.01);
	// Không tràn ra ngoài sân khấu.
	const san = (await page.locator('#ke-sach .san-khau').boundingBox())!;
	expect(hop.x).toBeGreaterThanOrEqual(san.x);
	expect(hop.x + hop.width).toBeLessThanOrEqual(san.x + san.width + 0.5);
});

test('máy tính hẹp: cảnh 3D nhìn thấy trọn hai cuốn sách', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.setViewportSize({ width: 900, height: 760 });
	await page.goto('/');
	const san = page.locator('#ke-sach .san-khau');
	await san.scrollIntoViewIfNeeded();
	await expect(san.locator('canvas.canvas-3d')).toBeVisible({ timeout: 8000 });
	const hop = (await san.boundingBox())!;
	for (const id of ['ai-engineer', 'robotics']) {
		await expect(san).toHaveAttribute(`data-pos-${id}`, /^\d+,\d+$/);
		const [x, y] = (await san.getAttribute(`data-pos-${id}`))!.split(',').map(Number);
		expect(x, id).toBeGreaterThan(40);
		expect(x, id).toBeLessThan(hop.width - 40);
		expect(y, id).toBeGreaterThan(20);
		expect(y, id).toBeLessThan(hop.height - 20);
	}
});
