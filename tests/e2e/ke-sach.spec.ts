import { test, expect, type Page } from '@playwright/test';

const TRANG_DAU = '/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/';
/** Chunk của cảnh 3D: three được gộp vào chunk canh-3d hoặc tách riêng tên three. */
const LA_CHUNK_3D = /three|canh-3d/i;

function ghiRequest(page: Page): string[] {
	const ds: string[] = [];
	page.on('request', (r) => ds.push(r.url()));
	return ds;
}

const theAi = (page: Page) => page.locator('#ke-sach').getByRole('link', { name: /AI Engineer/ });
const theRobotics = (page: Page) => page.locator('#ke-sach').getByRole('button', { name: /Robotics/ });

test('mobile: kệ sách sau hero, không tải three, thẻ chọn hoạt động', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	const req = ghiRequest(page);
	await page.goto('/');
	const ke = page.locator('#ke-sach');
	await expect(ke).toBeVisible();
	const yNut = (await page.getByRole('link', { name: 'Bắt đầu học' }).boundingBox())!.y;
	const yKe = (await ke.boundingBox())!.y;
	expect(yKe).toBeGreaterThan(yNut);
	await ke.scrollIntoViewIfNeeded();
	await page.waitForTimeout(800);
	expect(req.filter((u) => LA_CHUNK_3D.test(u))).toEqual([]);
	await expect(page.locator('#ke-sach canvas')).toHaveCount(0);
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);

	await expect(theAi(page)).toContainText('65 chương');
	await expect(theAi(page)).toContainText('đã viết 1');
	await theRobotics(page).tap();
	await expect(page.getByText('Nhánh Robotics đang được soạn')).toBeVisible();
	await expect(page).toHaveURL(/\/$/);
	await theAi(page).tap();
	await expect(page).toHaveURL(new RegExp(`${TRANG_DAU}$`));
});

test('desktop, giảm chuyển động: không canvas, không three, thẻ AI Engineer chuyển trang', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.emulateMedia({ reducedMotion: 'reduce' });
	const req = ghiRequest(page);
	await page.goto('/');
	await page.locator('#ke-sach').scrollIntoViewIfNeeded();
	await page.waitForTimeout(1000);
	await expect(page.locator('#ke-sach canvas')).toHaveCount(0);
	expect(req.filter((u) => LA_CHUNK_3D.test(u))).toEqual([]);
	await theAi(page).click();
	await expect(page).toHaveURL(new RegExp(`${TRANG_DAU}$`));
});

test('desktop không có WebGL: giữ bản phẳng, không tải three', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.addInitScript(() => {
		const goc = HTMLCanvasElement.prototype.getContext;
		// @ts-expect-error thay tạm để giả lập máy không có WebGL
		HTMLCanvasElement.prototype.getContext = function (loai: string, ...du: unknown[]) {
			return /webgl/.test(loai) ? null : goc.call(this, loai, ...du);
		};
	});
	const req = ghiRequest(page);
	await page.goto('/');
	await page.locator('#ke-sach').scrollIntoViewIfNeeded();
	await page.waitForTimeout(1000);
	await expect(page.locator('#ke-sach canvas')).toHaveCount(0);
	await expect(page.locator('#ke-sach .bia-phang').first()).toBeVisible();
	expect(req.filter((u) => LA_CHUNK_3D.test(u))).toEqual([]);
});

test('desktop: three chỉ tải khi tới gần kệ, đứng yên không vẽ lại, bấm thẻ vào sách', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	// Ở 1280x800 kệ nằm ngay màn đầu (y ≈ 470px) nên tải luôn là đúng. Thu thấp màn để kệ nằm hẳn
	// dưới mép cộng 200px rootMargin, kiểm được "chưa tới thì chưa tải".
	await page.setViewportSize({ width: 1280, height: 240 });
	const req = ghiRequest(page);
	await page.goto('/');
	const ke = page.locator('#ke-sach');
	const yKe = (await ke.boundingBox())!.y;
	expect(yKe).toBeGreaterThan(240 + 200);
	await page.waitForTimeout(1000);
	expect(req.filter((u) => LA_CHUNK_3D.test(u))).toEqual([]);

	await page.setViewportSize({ width: 1280, height: 800 });
	await ke.scrollIntoViewIfNeeded();
	await expect(page.locator('#ke-sach canvas')).toBeVisible({ timeout: 5000 });
	expect(req.filter((u) => LA_CHUNK_3D.test(u)).length).toBeGreaterThan(0);
	await expect(page.locator('#ke-sach canvas')).toHaveAttribute('aria-hidden', 'true');
	const sanKhau = page.locator('#ke-sach [data-frames]');
	await expect(sanKhau).toHaveAttribute('data-trang-thai', 'san-sang');

	await page.mouse.move(5, 5);
	await page.waitForTimeout(800);
	const truoc = Number(await sanKhau.getAttribute('data-frames'));
	expect(truoc).toBeGreaterThan(0);
	await page.waitForTimeout(2000);
	const sau = Number(await sanKhau.getAttribute('data-frames'));
	expect(sau - truoc).toBeLessThanOrEqual(3);

	const t0 = Date.now();
	await theAi(page).click();
	await expect(page).toHaveURL(new RegExp(`${TRANG_DAU}$`), { timeout: 2000 });
	expect(Date.now() - t0).toBeLessThanOrEqual(2000);
});

test('desktop: bàn phím Tab tới thẻ Robotics, Enter hiện thông báo', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/');
	await theAi(page).focus();
	await page.keyboard.press('Tab');
	await expect(theRobotics(page)).toBeFocused();
	await page.keyboard.press('Enter');
	await expect(page.locator('#ke-sach [aria-live]')).toContainText('Nhánh Robotics đang được soạn');
	await expect(page).toHaveURL(/\/$/);
});

test('desktop tối: chụp kệ sách, thẻ chọn đủ tương phản', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.emulateMedia({ colorScheme: 'dark' });
	await page.goto('/');
	await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
	const ke = page.locator('#ke-sach');
	await ke.scrollIntoViewIfNeeded();
	await expect(ke.locator('[data-frames]')).toHaveAttribute('data-trang-thai', 'san-sang', { timeout: 5000 });
	expect((await ke.screenshot()).length).toBeGreaterThan(1000);
	for (const the of [theAi(page), theRobotics(page)]) {
		const { mau, nen } = await the.evaluate((e) => {
			const cs = getComputedStyle(e);
			return { mau: cs.color, nen: cs.backgroundColor };
		});
		expect(mau).not.toBe(nen);
	}
});

test('mobile: hai bìa vẽ tay tải được dạng ảnh, vẫn không tải three', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	const req = ghiRequest(page);
	await page.goto('/');
	await page.locator('#ke-sach').scrollIntoViewIfNeeded();
	const anh = page.locator('#ke-sach img.anh-bia');
	await expect(anh).toHaveCount(2);
	for (const [i, ten] of ['ai-engineer', 'robotics'].entries()) {
		await expect(anh.nth(i)).toHaveAttribute('src', `/hinh/bia/${ten}.webp`);
		await expect(anh.nth(i)).toHaveAttribute('loading', 'lazy');
		await expect.poll(() => anh.nth(i).evaluate((e: HTMLImageElement) => e.complete && e.naturalWidth)).toBeGreaterThan(0);
	}
	expect(req.filter((u) => LA_CHUNK_3D.test(u))).toEqual([]);
	const bia = req.filter((u) => u.includes('/hinh/bia/'));
	expect(bia.length).toBe(2);
	expect(bia.every((u) => u.endsWith('.webp'))).toBe(true);
	const byte = await page.evaluate(() =>
		performance.getEntriesByType('resource').filter((e) => e.name.includes('/hinh/bia/')).reduce((t, e) => t + (e as PerformanceResourceTiming).encodedBodySize, 0),
	);
	expect(byte).toBeLessThanOrEqual(40 * 1024);
});

test('desktop: cảnh 3D dùng bìa SVG làm texture', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	const req = ghiRequest(page);
	await page.goto('/');
	await page.locator('#ke-sach').scrollIntoViewIfNeeded();
	await expect(page.locator('#ke-sach [data-frames]')).toHaveAttribute('data-trang-thai', 'san-sang', { timeout: 5000 });
	expect(req.some((u) => u.endsWith('/hinh/bia/ai-engineer.svg'))).toBe(true);
	expect(req.some((u) => u.endsWith('/hinh/bia/robotics.svg'))).toBe(true);
});

test('desktop: bật giảm chuyển động khi kệ 3D đang chạy thì gỡ cảnh, về kệ phẳng', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/');
	await page.locator('#ke-sach').scrollIntoViewIfNeeded();
	const sanKhau = page.locator('#ke-sach [data-frames]');
	await expect(sanKhau).toHaveAttribute('data-trang-thai', 'san-sang', { timeout: 5000 });
	await expect(page.locator('#ke-sach canvas')).toHaveCount(1);
	await page.emulateMedia({ reducedMotion: 'reduce' });
	await expect(page.locator('#ke-sach canvas')).toHaveCount(0);
	await expect(sanKhau).toHaveAttribute('data-trang-thai', 'phang');
	await expect(page.locator('#ke-sach .bia-phang').first()).toBeVisible();
	// Tắt giảm chuyển động thì kệ 3D được dựng lại.
	await page.emulateMedia({ reducedMotion: 'no-preference' });
	await expect(sanKhau).toHaveAttribute('data-trang-thai', 'san-sang', { timeout: 5000 });
	await expect(page.locator('#ke-sach canvas')).toHaveCount(1);
});

test.describe('máy tính bảng cảm ứng ≥ 820px', () => {
	test.use({ viewport: { width: 1024, height: 768 }, hasTouch: true, isMobile: true });
	test('giữ kệ phẳng, không tải three', async ({ page }, info) => {
		test.skip(info.project.name !== 'desktop');
		const req = ghiRequest(page);
		await page.goto('/');
		expect(await page.evaluate(() => [innerWidth >= 820, matchMedia('(pointer: fine)').matches])).toEqual([true, false]);
		await page.locator('#ke-sach').scrollIntoViewIfNeeded();
		await page.waitForTimeout(1000);
		await expect(page.locator('#ke-sach canvas')).toHaveCount(0);
		expect(req.filter((u) => LA_CHUNK_3D.test(u))).toEqual([]);
	});
});
