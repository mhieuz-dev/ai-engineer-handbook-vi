import { test, expect } from '@playwright/test';

const TRANG = '/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/';

test('khung đầu chương: nhãn Phần · Chương, tiêu đề, trang i/n, phút đọc', async ({ page }) => {
	await page.goto(TRANG);
	const dau = page.locator('.dau-chuong');
	await expect(dau).toContainText('Phần II');
	await expect(dau).toContainText('Chương 10');
	await expect(dau.locator('h1#_top')).toHaveText('Toán từng bước');
	await expect(dau.locator('.dc-meta')).toContainText('Trang 2/6');
	await expect(dau.locator('.dc-meta')).toContainText('phút đọc');
});

test('khung đầu chương: thanh 6 bước, bước đang đọc được đánh dấu', async ({ page }) => {
	await page.goto(TRANG);
	const buoc = page.locator('.dc-buoc li');
	await expect(buoc).toHaveCount(6);
	await expect(buoc.nth(1)).toHaveClass(/dang-o/);
	await expect(buoc.nth(1).getByRole('link')).toHaveAttribute('aria-current', 'page');
	await expect(buoc.nth(0).getByRole('link')).toHaveAttribute('href', '/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/');
});

test('khung đầu chương: trang đã đọc được tô màu', async ({ page }) => {
	await page.addInitScript(() => {
		localStorage.setItem(
			'air-tien-do-v1',
			JSON.stringify({
				daDoc: {
					'ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac': '2026-11-15',
					'ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan': '2026-11-16',
				},
				ngayHoc: ['2026-11-15', '2026-11-16'],
			}),
		);
	});
	await page.goto(TRANG);
	const daDoc = page.locator('.dc-buoc li.da-doc');
	await expect(daDoc).toHaveCount(2);
	await expect(daDoc.nth(0)).toContainText('Bài toán và trực giác');
});

test('Tải về và Colab nằm cùng hàng dưới thanh bước', async ({ page }) => {
	await page.goto(TRANG);
	const hang = page.locator('.dc-nut');
	await expect(hang.getByRole('button', { name: 'Tải về' })).toBeVisible();
	await expect(hang.getByRole('link', { name: /Mở trong Colab/ })).toHaveAttribute('href', /colab\.research\.google\.com/);
});

test('hai khung Cần biết trước và Sau chương này cao bằng nhau', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/');
	const khoi = page.locator('.can-biet-truoc .cbt-khoi');
	await expect(khoi).toHaveCount(2);
	const [a, b] = await khoi.evaluateAll((els) => els.map((e) => Math.round(e.getBoundingClientRect().height)));
	expect(Math.abs(a - b)).toBeLessThanOrEqual(1);
});

test('cuối trang: thẻ trang trước/sau ghi số trang, hết chương thì "Sang Chương N"', async ({ page }) => {
	await page.goto(TRANG);
	const nav = page.locator('.dc-dieu-huong');
	await expect(nav.locator('a[rel="prev"]')).toContainText('Trang trước');
	await expect(nav.locator('a[rel="prev"]')).toContainText('Chương 10 · Trang 1/6');
	await expect(nav.locator('a[rel="next"]')).toContainText('Trang 3/6');

	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/06-bai-tap/');
	const sau = page.locator('.dc-dieu-huong a[rel="next"]');
	await expect(sau).toContainText('Sang Chương 11');
	await expect(sau).toContainText('Chương 11 · Trang 1/5');
	await expect(sau).toHaveAttribute('href', '/ai-engineer/ch11-hoi-quy-logistic/01-bai-toan-phan-loai/');
});

test('trang không phải chương vẫn dùng điều hướng mặc định', async ({ page }) => {
	await page.goto('/gioi-thieu/');
	await expect(page.locator('.dc-dieu-huong')).toHaveCount(0);
	await expect(page.locator('.dau-chuong')).toHaveCount(0);
});
