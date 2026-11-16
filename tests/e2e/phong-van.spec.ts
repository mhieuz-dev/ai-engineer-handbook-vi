import { test, expect, type Page } from '@playwright/test';

const TRA_LOI = 'Em từng làm dự án phân loại phản hồi sinh viên, cải thiện macro-F1 từ 0,72 lên 0,79 và giảm 30% thời gian xử lý. Đánh đổi là mô hình nặng hơn nên phải tối ưu suy luận.';

async function chiVongDau(page: Page) {
	const cbs = page.locator('[data-pv-vong-chon]');
	for (let i = 0; i < (await cbs.count()); i++) await cbs.nth(i).uncheck();
	await cbs.first().check();
}

test('8 phong cách, chọn vòng, chạy hết một buổi và tự đánh giá khi chưa có AI', async ({ page }) => {
	test.setTimeout(120_000);
	page.on('dialog', (d) => d.accept());
	await page.route('**/api/ai', (route) => route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ loi: 'het-nha-cung-cap' }) }));
	await page.goto('/phong-van/');
	await expect(page.locator('.pv-the')).toHaveCount(8);
	await expect(page.locator('[data-pv-vong-chon]')).toHaveCount(6);
	await chiVongDau(page);
	await page.click('[data-pv-bat-dau]');
	await expect(page.locator('.pv-round')).toContainText('Vòng 1/1');
	await page.locator('[data-pv-goi-y]').click();
	await expect(page.locator('[data-pv-goi-y-noi]')).toContainText('đã trừ 0,5 điểm');
	await page.locator('.pv-tra-loi').fill(TRA_LOI);
	await page.locator('[data-pv-gui]').click();
	await page.locator('[data-pv-tiep]').click();
	await expect(page.locator('.pv-kq')).toBeVisible();
	await expect(page.locator('[data-pv-td]')).toHaveCount(6);
	for (let i = 0; i < 6; i++) await page.locator(`[data-pv-td="${i}"]`).selectOption('4');
	await page.locator('[data-pv-tinh]').click();
	await expect(page.locator('[data-pv-td-kq]')).toContainText('9.5');
	await expect(page.locator('[data-pv-td-kq]')).toContainText('Đạt');
});

test('có máy chủ AI: phiếu đánh giá theo tiêu chí, trích dẫn và chương cần ôn', async ({ page }) => {
	test.setTimeout(120_000);
	page.on('dialog', (d) => d.accept());
	await page.route('**/api/ai', (route) =>
		route.fulfill({
			status: 200,
			contentType: 'application/json',
			body: JSON.stringify({
				phongVan: {
					tieuChi: [
						{ ten: 'Kiến thức nền', diem: 3, trichDan: 'macro-F1 từ 0,72 lên 0,79' },
						{ ten: 'Độ sâu kỹ thuật', diem: 3, trichDan: 'tối ưu suy luận' },
						{ ten: 'Code', diem: 2, trichDan: 'chưa có code' },
						{ ten: 'Thiết kế hệ thống', diem: 3, trichDan: 'giảm 30% thời gian xử lý' },
						{ ten: 'Giải thích và giao tiếp', diem: 4, trichDan: 'đánh đổi là mô hình nặng hơn' },
						{ ten: 'Hành vi STAR', diem: 3, trichDan: 'dự án phân loại phản hồi sinh viên' },
					],
					diem: 7.5,
					muc: 'dat',
					cauTraLoiMau: ['Nêu bối cảnh, số liệu trước sau và đánh đổi.'],
					chuongCanOn: [{ ten: 'Hồi quy tuyến tính', trang: '/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/' }],
				},
			}),
		}),
	);
	await page.goto('/phong-van/');
	await chiVongDau(page);
	await page.click('[data-pv-bat-dau]');
	await page.locator('.pv-tra-loi').fill(TRA_LOI);
	await page.locator('[data-pv-gui]').click();
	await page.locator('[data-pv-tiep]').click();
	await expect(page.locator('.pv-tong')).toBeVisible();
	await expect(page.locator('.pv-diem')).toContainText('7.5');
	await expect(page.locator('.pv-muc')).toContainText('Đạt');
	await expect(page.locator('.pv-bang tbody tr')).toHaveCount(6);
	await expect(page.locator('.pv-bang')).toContainText('macro-F1');
	await expect(page.locator('.pv-kq a[href="/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/"]')).toContainText('Hồi quy tuyến tính');
});

test('mobile 375px: phỏng vấn không tràn ngang', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/phong-van/');
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);
	await page.click('[data-pv-bat-dau]');
	await expect(page.locator('.pv-thi')).toBeVisible();
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);
});
