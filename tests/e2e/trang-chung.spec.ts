import { test, expect } from '@playwright/test';
import { CHUONG, PHAN, chuongDaXuatBan } from '../../src/data/chuong';

const TRANG_DAU = '/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/';

test('trang chủ: tiêu đề, hai thẻ nhánh, nút Chọn sách để học', async ({ page }) => {
	await page.goto('/');
	await expect(page.locator('h1')).toHaveText('AI & Robotics');
	await expect(page.getByText('Giáo trình tiếng Việt miễn phí: hiểu tận gốc AI, từ Python cơ bản đến mô hình ngôn ngữ lớn.')).toBeVisible();
	const ai = page.locator('#ke-sach .the-chon', { hasText: 'AI Engineer' });
	const robot = page.locator('#ke-sach .the-chon', { hasText: 'Robotics' });
	await expect(ai).toBeVisible();
	await expect(ai).toContainText('Đang viết');
	await expect(robot).toContainText('Sắp có');
	await expect(page.getByRole('link', { name: /Chọn sách để học/ })).toHaveAttribute('href', '#ke-sach');
	await expect(page.getByText('Cách học trên trang này')).toBeVisible();
});

test('trang chủ: thẻ title không lặp tên site', async ({ page }) => {
	await page.goto('/');
	await expect(page).toHaveTitle('AI & Robotics | Giáo trình AI tiếng Việt miễn phí');
});

test('sitemap không chứa trang mẫu kiểm thử và trang in', async ({ request }) => {
	const xml = await (await request.get('/sitemap-0.xml')).text();
	expect(xml).toContain('/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/');
	expect(xml).not.toContain('/kiem-thu/');
	expect(xml).not.toContain('/in/');
});

test('lộ trình: 65 dòng chương, chương đã xuất bản là link, còn lại có nhãn Sắp có', async ({ page }) => {
	await page.goto('/lo-trinh/');
	const dong = page.locator('li[id^="ch"]');
	await expect(dong).toHaveCount(65);
	await expect(page.locator('li#ch01 a')).toHaveAttribute('href', '/ai-engineer/ch01-python-tu-dau/01-bien-va-kieu/');
	await expect(page.locator('li#ch10 a')).toHaveAttribute('href', TRANG_DAU);
	await expect(page.locator('li[id^="ch"] a')).toHaveCount(chuongDaXuatBan().length);
	await expect(page.locator('li[id^="ch"] .nhan-sap-co')).toHaveCount(65 - chuongDaXuatBan().length);
	await expect(page.locator('li#ch64')).toContainText('Phỏng vấn và portfolio');
});

test('notebook: bảng chương đã xuất bản có nút Colab và link GitHub', async ({ page }) => {
	await page.goto('/notebook/');
	const coNotebook = CHUONG.filter((c) => c.notebook);
	await expect(page.locator('table tbody tr')).toHaveCount(coNotebook.length);
	await expect(page.locator('table tbody tr').first()).toContainText(coNotebook[0].notebook!);
	const hang = page.locator('table tbody tr').nth(coNotebook.findIndex((c) => c.so === 10));
	await expect(hang).toContainText('ch10_hoi_quy_tuyen_tinh.ipynb');
	await expect(hang.locator('a.colab-nut')).toHaveAttribute('href', /colab\.research\.google\.com\/github\/mhieuz-dev\/ai-engineer-handbook-vi\/blob\/main\/notebooks\/ch10_hoi_quy_tuyen_tinh\.ipynb$/);
	await expect(hang.getByRole('link', { name: 'GitHub' })).toHaveAttribute('href', /github\.com\/mhieuz-dev\/ai-engineer-handbook-vi\/blob\/main\/notebooks\/ch10_hoi_quy_tuyen_tinh\.ipynb$/);
});

test('giới thiệu: Mhz, MIT, GitHub, báo lỗi', async ({ page }) => {
	await page.goto('/gioi-thieu/');
	const noiDung = page.locator('main');
	await expect(noiDung).toContainText('Mhz');
	await expect(noiDung).toContainText('MIT');
	await expect(noiDung.getByRole('link', { name: 'LICENSE' })).toHaveAttribute('href', /github\.com\/mhieuz-dev\/ai-engineer-handbook-vi\/blob\/main\/LICENSE/);
	await expect(noiDung.getByRole('link', { name: 'GitHub Issues' })).toHaveAttribute('href', /github\.com\/mhieuz-dev\/ai-engineer-handbook-vi\/issues/);
});

test('menu trên cùng có Lộ trình, Thuật ngữ, Notebook', async ({ page, isMobile }) => {
	await page.goto('/');
	const nav = page.locator(isMobile ? '.nav-chung-mobile' : 'header .nav-chung');
	for (const [ten, href] of [['Lộ trình', '/lo-trinh/'], ['Thuật ngữ', '/thuat-ngu/'], ['Notebook', '/notebook/']]) {
		await expect(nav.getByRole('link', { name: ten })).toHaveAttribute('href', href);
	}
});

test('mobile 375px: trang chủ, lộ trình, notebook, giới thiệu, quyền riêng tư không tràn ngang', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	for (const url of ['/', '/lo-trinh/', '/notebook/', '/gioi-thieu/', '/quyen-rieng-tu/']) {
		await page.goto(url);
		expect(await page.evaluate(() => document.documentElement.scrollWidth), url).toBeLessThanOrEqual(375);
	}
});

test('mobile: menu ☰ trên trang bài có liên kết Lộ trình', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	await page.locator('button.sl-menu-button').tap();
	const lk = page.locator('.nav-sidebar').getByRole('link', { name: 'Lộ trình' });
	await expect(lk).toBeVisible();
	await lk.tap();
	await expect(page).toHaveURL(/\/lo-trinh\/$/);
});

for (const [rong, cao] of [[820, 1180], [900, 1200]]) {
	test(`máy tính bảng ${rong}px: link đầu trang nằm trên một dòng, không tràn ngang`, async ({ page, isMobile }) => {
		test.skip(!!isMobile);
		await page.setViewportSize({ width: rong, height: cao });
		await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
		const nhan = page.locator('header .nav-chung a, header button[data-open-modal] > span');
		await expect(nhan).toHaveCount(5);
		for (const el of await nhan.all()) {
			const { cao: h, dong } = await el.evaluate((e) => ({ cao: e.getBoundingClientRect().height, dong: parseFloat(getComputedStyle(e).lineHeight) }));
			expect(h, (await el.textContent()) ?? '').toBeLessThan(1.6 * dong);
		}
		expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(rong);
		const phai = await page.locator('header .right-group').evaluate((e) => e.getBoundingClientRect().right);
		expect(phai).toBeLessThanOrEqual(rong);
	});
}

test('desktop: menu phụ của sidebar ẩn, chỉ còn menu đầu trang', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	await expect(page.locator('.nav-sidebar')).toBeHidden();
	await expect(page.locator('header .nav-chung')).toBeVisible();
});

test('desktop: link đầu trang cách nhau bằng chấm nhỏ, nút Tải về là nút viền cuối hàng breadcrumb', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	const links = page.locator('header .nav-chung a');
	const cham = await links.evaluateAll((as) => as.map((a) => getComputedStyle(a, '::before').width));
	expect(cham).toEqual(['auto', '3px', '3px', '3px']);
	const nut = page.getByRole('button', { name: 'Tải về' });
	await expect(nut).toHaveText('Tải về');
	expect(await nut.evaluate((e) => getComputedStyle(e).borderTopWidth)).toBe('1px');
	const hNut = (await nut.boundingBox())!;
	const hHang = (await page.locator('.crumb-hang').boundingBox())!;
	expect(hNut.x + hNut.width).toBeGreaterThan(hHang.x + hHang.width - 2);
});

test('trang chủ: thanh tiến độ tổng và lưới thẻ theo Phần đếm đúng theo chuong.ts', async ({ page }) => {
	await page.goto('/');
	const daXong = chuongDaXuatBan().length;
	await expect(page.locator('.tdt-hang')).toContainText(`${daXong}/${CHUONG.length}`);
	const thanh = page.locator('.tdt-thanh');
	await expect(thanh).toHaveAttribute('aria-valuenow', String(Math.round((daXong / CHUONG.length) * 100)));
	await expect(page.locator('.the-phan')).toHaveCount(PHAN.length);
	await expect(page.locator('.o-chuong')).toHaveCount(CHUONG.length);
	await expect(page.locator('.o-chuong.xong')).toHaveCount(daXong);
	await expect(page.locator('.o-chuong.sap-co')).toHaveCount(CHUONG.length - daXong);
	await expect(page.locator('.o-chuong.xong').first()).toHaveAttribute('href', '/ai-engineer/ch00-lo-trinh-va-colab/01-lo-trinh/');
	await expect(page.locator('.o-chuong.sap-co').first()).toContainText('Prompt engineering');
});

test('trang chủ: Học tiếp ẩn khi chưa đọc, hiện đúng trang đọc gần nhất', async ({ page }) => {
	await page.goto('/');
	await expect(page.locator('.hoc-tiep:not(.on-lai)')).toBeHidden();

	await page.addInitScript(() => {
		localStorage.setItem(
			'air-tien-do-v1',
			JSON.stringify({
				daDoc: { 'ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan': '2026-11-15' },
				ngayHoc: ['2026-11-15'],
			}),
		);
	});
	await page.goto('/');
	const the = page.locator('.hoc-tiep:not(.on-lai)');
	await expect(the).toBeVisible();
	await expect(the).toContainText('Chương 10');
	await expect(the).toContainText('Trang 2');
	await expect(the.locator('.ht-nut')).toHaveAttribute('href', '/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
});

test('trang chủ mobile: các Phần gập lại, mở ra được', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/');
	const phan = page.locator('.the-phan').first();
	await expect(phan).not.toHaveAttribute('open', '');
	await phan.locator('summary').tap();
	await expect(phan).toHaveAttribute('open', '');
	await expect(phan.locator('.o-chuong').first()).toBeVisible();
});


test('quyền riêng tư: giải thích nơi lưu, có nút xuất và xoá; chưa cấu hình Firebase thì không hiện nút đăng nhập', async ({ page }) => {
	await page.goto('/quyen-rieng-tu/');
	await expect(page.locator('h1')).toContainText('Quyền riêng tư');
	await expect(page.locator('.qrt')).toContainText('chưa đăng nhập');
	await expect(page.getByRole('button', { name: 'Xuất dữ liệu ra tệp JSON' })).toBeVisible();
	await expect(page.getByRole('button', { name: 'Xoá dữ liệu trong trình duyệt' })).toBeVisible();
	await expect(page.locator('.dn-nut')).toHaveCount(0);
});


test('trang chủ: thẻ Phòng thi thử và thẻ Ôn lại từ kết quả thi', async ({ page }) => {
	await page.goto('/');
	const theThi = page.locator('.luyen-tap .lt-the', { hasText: 'Phòng thi thử' });
	await expect(theThi).toHaveAttribute('href', '/phong-thi/');
	const theThuatToan = page.locator('.luyen-tap .lt-the', { hasText: 'Luyện thuật toán' });
	await expect(theThuatToan).toHaveAttribute('href', '/thuat-toan/');
	await expect(page.locator('.on-lai')).toBeHidden();

	await page.addInitScript(() => {
		localStorage.setItem(
			'air-bai-thi-v1',
			JSON.stringify([
				{
					id: 'x',
					ngay: '2026-11-15T10:00:00Z',
					kieu: 'nhanh',
					phamVi: [0],
					diem: 7.4,
					soCau: 12,
					banDo: [
						{ id: 'chon-chi-so', ten: 'Chọn chỉ số đánh giá', trang: '/ai-engineer/ch12-danh-gia-mo-hinh/01-ma-tran-nham-lan/', dat: 0.4, tong: 1, phanTram: 40, muc: 'chua-nam' },
						{ id: 'ro-ri', ten: 'Rò rỉ dữ liệu', trang: '/ai-engineer/ch09-quy-trinh-du-an-ml/04-pipeline-va-ro-ri/', dat: 1, tong: 1, phanTram: 100, muc: 'vung' },
					],
				},
			]),
		);
	});
	await page.goto('/');
	const on = page.locator('.on-lai');
	await expect(on).toBeVisible();
	await expect(on).toContainText('Chọn chỉ số đánh giá (40%)');
	await expect(on.locator('.ht-nut')).toHaveAttribute('href', '/ai-engineer/ch12-danh-gia-mo-hinh/01-ma-tran-nham-lan/');
});
