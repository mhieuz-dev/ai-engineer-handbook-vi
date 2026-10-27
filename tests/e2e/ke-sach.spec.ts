import { test, expect, type Page } from '@playwright/test';
import { chuongDaXuatBan } from '../../src/data/chuong';

const TRANG_DAU = '/ai-engineer/ch01-python-tu-dau/01-bien-va-kieu/';
/** Chunk của cảnh 3D: three được gộp vào chunk canh-3d hoặc tách riêng tên three. */
const LA_CHUNK_3D = /three|canh-3d/i;

function ghiRequest(page: Page): string[] {
	const ds: string[] = [];
	page.on('request', (r) => ds.push(r.url()));
	return ds;
}

const theAi = (page: Page) => page.locator('#ke-sach').getByRole('link', { name: /AI Engineer/ });
const bang = (page: Page) => page.locator('#ke-sach [role="dialog"]');
const nutBatDau = (page: Page) => bang(page).getByRole('link', { name: 'Bắt đầu học' });
const nutQuayLai = (page: Page) => bang(page).getByRole('button', { name: '← Quay lại kệ sách' });
const theRobotics = (page: Page) => page.locator('#ke-sach').getByRole('button', { name: /Robotics/ });

test('mobile: kệ sách sau hero, không tải three, thẻ chọn hoạt động', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	const req = ghiRequest(page);
	await page.goto('/');
	const ke = page.locator('#ke-sach');
	await expect(ke).toBeVisible();
	const yNut = (await page.getByRole('link', { name: /Chọn sách để học/ }).boundingBox())!.y;
	const yKe = (await ke.boundingBox())!.y;
	expect(yKe).toBeGreaterThan(yNut);
	await ke.scrollIntoViewIfNeeded();
	await page.waitForTimeout(800);
	expect(req.filter((u) => LA_CHUNK_3D.test(u))).toEqual([]);
	await expect(page.locator('#ke-sach canvas')).toHaveCount(0);
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);

	await expect(theAi(page)).toContainText('65 chương');
	await expect(theAi(page)).toContainText(`đã viết ${chuongDaXuatBan().length}`);
	await theRobotics(page).tap();
	await expect(bang(page)).toContainText('Nhánh này đang được soạn');
	await expect(nutBatDau(page)).toHaveCount(0);
	await expect(nutQuayLai(page)).toBeFocused();
	await expect(page).toHaveURL(/\/$/);
	await nutQuayLai(page).tap();
	await expect(bang(page)).toBeHidden();
	await expect(page).toHaveURL(/\/$/);
	await theAi(page).tap();
	await expect(page).toHaveURL(/\/$/);
	await expect(bang(page)).toContainText(`65 chương · đã viết ${chuongDaXuatBan().length}`);
	await expect(nutBatDau(page)).toBeFocused();
	expect((await nutBatDau(page).boundingBox())!.height).toBeGreaterThanOrEqual(44);
	await nutBatDau(page).tap();
	await expect(page).toHaveURL(new RegExp(`${TRANG_DAU}$`));
});

test('desktop, giảm chuyển động: không canvas, không three, thẻ AI Engineer mở bảng rồi mới chuyển trang', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.emulateMedia({ reducedMotion: 'reduce' });
	const req = ghiRequest(page);
	await page.goto('/');
	await page.locator('#ke-sach').scrollIntoViewIfNeeded();
	await page.waitForTimeout(1000);
	await expect(page.locator('#ke-sach canvas')).toHaveCount(0);
	expect(req.filter((u) => LA_CHUNK_3D.test(u))).toEqual([]);
	await theAi(page).click();
	await expect(page).toHaveURL(/\/$/);
	await expect(nutBatDau(page)).toBeFocused();
	await page.keyboard.press('Escape');
	await expect(bang(page)).toBeHidden();
	await expect(theAi(page)).toBeFocused();
	await theAi(page).click();
	await nutBatDau(page).click();
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

	await theAi(page).click();
	await expect(page).toHaveURL(/\/$/);
	await expect(bang(page)).toBeVisible();
	await expect(nutBatDau(page)).toBeFocused();
	await expect(nutBatDau(page)).toHaveAttribute('href', TRANG_DAU);
	// Quay lại: bảng ẩn, URL giữ nguyên, sách trượt về kệ rồi đứng yên (≤ 3 khung trong 2 giây).
	await nutQuayLai(page).click();
	await expect(bang(page)).toBeHidden();
	await expect(page).toHaveURL(/\/$/);
	await expect(theAi(page)).toBeFocused();
	await page.mouse.move(5, 5);
	await page.waitForTimeout(1200);
	const t1 = Number(await sanKhau.getAttribute('data-frames'));
	await page.waitForTimeout(2000);
	expect(Number(await sanKhau.getAttribute('data-frames')) - t1).toBeLessThanOrEqual(3);
	// Bấm thẻ lần nữa rồi chuyển trang bằng nút Bắt đầu học.
	await theAi(page).click();
	await nutBatDau(page).click();
	await expect(page).toHaveURL(new RegExp(`${TRANG_DAU}$`));
});

test('desktop: Robotics mở bảng không có nút Bắt đầu học, Escape đóng', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/');
	await expect(page.locator('#ke-sach [data-frames]')).toHaveAttribute('data-trang-thai', 'san-sang', { timeout: 5000 });
	await theRobotics(page).click();
	await expect(bang(page)).toBeVisible();
	await expect(bang(page)).toContainText('Nhánh này đang được soạn');
	await expect(bang(page)).toContainText('Sắp có');
	await expect(nutBatDau(page)).toHaveCount(0);
	await expect(nutQuayLai(page)).toBeFocused();
	await page.keyboard.press('Escape');
	await expect(bang(page)).toBeHidden();
	await expect(page).toHaveURL(/\/$/);
});

test('desktop: mở bảng trước khi cảnh 3D sẵn sàng thì sách vẫn được rút ra khi cảnh dựng xong', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.setViewportSize({ width: 1280, height: 240 });
	await page.goto('/');
	const sanKhau = page.locator('#ke-sach [data-frames]');
	await expect(sanKhau).toHaveAttribute('data-trang-thai', 'phang');
	await theAi(page).dispatchEvent('click');
	await expect(bang(page)).toBeVisible();
	await page.setViewportSize({ width: 1280, height: 800 });
	await page.locator('#ke-sach').scrollIntoViewIfNeeded();
	await expect(sanKhau).toHaveAttribute('data-trang-thai', 'san-sang', { timeout: 5000 });
	await expect.poll(async () => Number(await sanKhau.getAttribute('data-nho'))).toBeGreaterThan(0.5);
	await expect(page.locator('#ke-sach')).toHaveAttribute('data-sach-mo', 'ai-engineer');
});

test('desktop: đóng bảng thì sách trượt về sát kệ, đứng yên; mở thì khung hình nghỉ ≤ 3; Escape trả focus', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/');
	const sanKhau = page.locator('#ke-sach [data-frames]');
	await expect(sanKhau).toHaveAttribute('data-trang-thai', 'san-sang', { timeout: 5000 });
	await theAi(page).click();
	await expect.poll(async () => Number(await sanKhau.getAttribute('data-nho'))).toBeGreaterThan(0.5);
	await page.mouse.move(5, 5);
	await page.waitForTimeout(1200);
	const a = Number(await sanKhau.getAttribute('data-frames'));
	await page.waitForTimeout(2000);
	expect(Number(await sanKhau.getAttribute('data-frames')) - a).toBeLessThanOrEqual(3);
	await page.keyboard.press('Escape');
	await expect(theAi(page)).toBeFocused();
	await expect.poll(async () => await sanKhau.getAttribute('data-nho')).toBe('0.00');
	await expect(page.locator('#ke-sach')).not.toHaveAttribute('data-sach-mo', /.+/);
});

test('desktop: bấm cuốn khác khi một cuốn đang mở thì đóng cuốn trước, mở cuốn sau', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/');
	await expect(page.locator('#ke-sach [data-frames]')).toHaveAttribute('data-trang-thai', 'san-sang', { timeout: 5000 });
	await theAi(page).click();
	await expect(nutBatDau(page)).toBeVisible();
	await theRobotics(page).click();
	await expect(bang(page)).toContainText('Robotics');
	await expect(nutBatDau(page)).toHaveCount(0);
	await expect(page.locator('#ke-sach')).toHaveAttribute('data-sach-mo', 'robotics');
});

test('mobile: bấm cuốn khác khi một cuốn đang mở thì bảng đổi sang cuốn sau', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/');
	await theAi(page).tap();
	await expect(nutBatDau(page)).toBeVisible();
	await theRobotics(page).tap();
	await expect(bang(page)).toContainText('Robotics');
	await expect(nutBatDau(page)).toHaveCount(0);
	await theAi(page).tap();
	await expect(nutBatDau(page)).toBeVisible();
});

const keGoc = (page: Page) => page.locator('#ke-sach');
const sanKhau3D = (page: Page) => page.locator('#ke-sach [data-frames]');

/** Tọa độ trang của tâm bìa cuốn `id`, lấy từ data-pos-<id> mà cảnh 3D ghi khi đứng yên (chờ tới khi có). */
async function viTriBia(page: Page, id: string) {
	await page.mouse.move(5, 5);
	await expect(sanKhau3D(page)).toHaveAttribute(`data-pos-${id}`, /^\d+,\d+$/);
	const [x, y] = (await sanKhau3D(page).getAttribute(`data-pos-${id}`))!.split(',').map(Number);
	const b = (await page.locator('#ke-sach canvas').boundingBox())!;
	const diem = { x: b.x + x, y: b.y + y };
	// Điểm bấm phải trúng canvas chứ không phải bảng thông tin nằm đè lên.
	expect(await page.evaluate(({ x, y }) => document.elementFromPoint(x, y)?.tagName, diem)).toBe('CANVAS');
	return diem;
}
async function bamCanvas(page: Page, id: string) {
	const { x, y } = await viTriBia(page, id);
	await page.mouse.click(x, y);
}

/** Bất biến: bảng hiện ⇔ có data-sach-mo; ở bản 3D thì sách rút ra ⇔ bảng hiện. */
async function kiemDaDong(page: Page, co3D: boolean) {
	await expect(bang(page)).toBeHidden();
	await expect(keGoc(page)).not.toHaveAttribute('data-sach-mo', /.+/);
	if (co3D) {
		await page.mouse.move(5, 5);
		await expect.poll(async () => await sanKhau3D(page).getAttribute('data-nho')).toBe('0.00');
	}
}
async function kiemDangMo(page: Page, id: string, ten: RegExp, co3D: boolean) {
	await expect(bang(page)).toBeVisible();
	await expect(bang(page).locator('.bang-ten')).toHaveText(ten);
	await expect(keGoc(page)).toHaveAttribute('data-sach-mo', id);
	if (co3D) await expect.poll(async () => Number(await sanKhau3D(page).getAttribute('data-nho'))).toBeGreaterThan(0.5);
}

for (const co3D of [true, false]) {
	test(`${co3D ? 'desktop 3D' : 'mobile phẳng'}: bấm cuốn đang mở lần nữa thì đóng, bấm cuốn khác thì đổi`, async ({ page, isMobile }) => {
		test.skip(co3D === !!isMobile);
		await page.goto('/');
		await keGoc(page).scrollIntoViewIfNeeded();
		if (co3D) await expect(sanKhau3D(page)).toHaveAttribute('data-trang-thai', 'san-sang', { timeout: 5000 });
		const bam = (l: ReturnType<typeof theAi>) => (co3D ? l.click() : l.tap());

		await bam(theAi(page));
		await kiemDangMo(page, 'ai-engineer', /AI Engineer/, co3D);
		await bam(theAi(page));
		await kiemDaDong(page, co3D);
		await expect(theAi(page)).toBeFocused();

		await bam(theRobotics(page));
		await kiemDangMo(page, 'robotics', /Robotics/, co3D);
		await bam(theRobotics(page));
		await kiemDaDong(page, co3D);

		await bam(theAi(page));
		await kiemDangMo(page, 'ai-engineer', /AI Engineer/, co3D);
		await bam(theRobotics(page));
		await kiemDangMo(page, 'robotics', /Robotics/, co3D);
		await expect(nutBatDau(page)).toHaveCount(0);
		// Quay lại vẫn đóng cả bảng lẫn cuốn trong cảnh.
		await bam(nutQuayLai(page));
		await kiemDaDong(page, co3D);
	});
}

test('mobile: bấm bìa phẳng của cuốn đang mở thì đóng', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/');
	const bia = page.locator('#ke-sach .bia-phang[data-cuon="robotics"]');
	await bia.tap();
	await kiemDangMo(page, 'robotics', /Robotics/, false);
	await bia.tap();
	await kiemDaDong(page, false);
});

test('desktop: bấm cuốn trên canvas 3D lần hai thì cuốn đóng lại, bảng ẩn theo', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.setViewportSize({ width: 1280, height: 800 });
	await page.goto('/');
	await keGoc(page).scrollIntoViewIfNeeded();
	await expect(sanKhau3D(page)).toHaveAttribute('data-trang-thai', 'san-sang', { timeout: 5000 });

	await bamCanvas(page, 'ai-engineer');
	await kiemDangMo(page, 'ai-engineer', /AI Engineer/, true);
	await bamCanvas(page, 'ai-engineer'); // lúc này là tâm tấm bìa đã lật của cuốn đang mở
	await kiemDaDong(page, true);

	await bamCanvas(page, 'robotics');
	await kiemDangMo(page, 'robotics', /Robotics/, true);
	await bamCanvas(page, 'robotics');
	await kiemDaDong(page, true);
});

test('desktop: cử chỉ bị hủy (pointercancel) trên cuốn đang mở không tính là bấm, sách vẫn mở', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.setViewportSize({ width: 1280, height: 800 });
	await page.goto('/');
	await keGoc(page).scrollIntoViewIfNeeded();
	await expect(sanKhau3D(page)).toHaveAttribute('data-trang-thai', 'san-sang', { timeout: 5000 });
	await theAi(page).click();
	await kiemDangMo(page, 'ai-engineer', /AI Engineer/, true);
	const diem = await viTriBia(page, 'ai-engineer');
	await page.locator('#ke-sach canvas').evaluate((cv, { x, y }) => {
		const tao = (loai: string) => new PointerEvent(loai, { bubbles: true, clientX: x, clientY: y, pointerId: 7, button: 0, isPrimary: true });
		cv.dispatchEvent(tao('pointerdown'));
		cv.dispatchEvent(tao('pointercancel'));
	}, diem);
	await page.waitForTimeout(300); // không có gì để chờ: khẳng định trạng thái không đổi sau vài khung
	await kiemDangMo(page, 'ai-engineer', /AI Engineer/, true);
	// Bấm thật (down + up) ở cùng chỗ thì vẫn đóng như thường.
	await page.mouse.click(diem.x, diem.y);
	await kiemDaDong(page, true);
});

test('trang chủ: nút hero "Chọn sách để học" trỏ tới #ke-sach', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('link', { name: /Chọn sách để học/ })).toHaveAttribute('href', '#ke-sach');
});

test('desktop: bàn phím Tab tới thẻ Robotics, Enter mở bảng thông tin', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/');
	await theAi(page).focus();
	await page.keyboard.press('Tab');
	await expect(theRobotics(page)).toBeFocused();
	await page.keyboard.press('Enter');
	await expect(bang(page)).toContainText('Nhánh này đang được soạn');
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
