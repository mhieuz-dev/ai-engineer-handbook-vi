import { test, expect, type Page } from '@playwright/test';
import fs from 'node:fs';
import { chuongDaXuatBan } from '../../src/data/chuong';

const TONG = chuongDaXuatBan().length;

async function gieo(page: Page) {
	await page.addInitScript(() => {
		localStorage.setItem(
			'air-tien-do-v1',
			JSON.stringify({
				daDoc: {
					'ai-engineer/ch00-lo-trinh-va-colab/01-lo-trinh/': '2026-11-15',
					'ai-engineer/ch01-python-tu-dau/01-bien-va-kieu/': '2026-11-15',
				},
				ngayHoc: ['2026-11-15'],
			}),
		);
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
						{ id: 'a', ten: 'Rò rỉ dữ liệu', trang: '/ai-engineer/ch09-quy-trinh-du-an-ml/04-pipeline-va-ro-ri/', dat: 1, tong: 1, phanTram: 100, muc: 'vung' },
						{ id: 'b', ten: 'Chọn chỉ số', trang: '/ai-engineer/ch12-danh-gia-mo-hinh/01-ma-tran-nham-lan/', dat: 0.4, tong: 1, phanTram: 40, muc: 'chua-nam' },
					],
				},
			]),
		);
		localStorage.setItem('air-thuat-toan-v1', JSON.stringify({ daGiai: { '1': '2026-11-15', '2': '2026-11-15' }, daThu: { '3': 2 }, ngay: ['2026-11-15'] }));
		localStorage.setItem('air-phong-van-v1', JSON.stringify([{ ngay: '2026-11-14T10:00:00Z', preset: 'Kiểu Google', cap: 'intern', diem: 6.5, muc: 'Cân nhắc' }]));
	});
}

test('hồ sơ: tổng quan, biểu đồ, bản đồ kiến thức và học gì tiếp', async ({ page }) => {
	await gieo(page);
	await page.goto('/ho-so/');
	await expect(page.locator('[data-hs-tong]')).toContainText(`2/${TONG}`);
	await expect(page.locator('[data-hs-tong]')).toContainText('1');
	await expect(page.locator('.hs-svg')).toHaveCount(1);
	await expect(page.locator('.hs-bang tbody tr')).toHaveCount(2);
	await expect(page.locator('.hs-bang')).toContainText('Chọn chỉ số');
	await expect(page.locator('.hs-dang')).toHaveCount(12);
	await expect(page.locator('.hs-dang').first()).toContainText('2/5');
	await expect(page.locator('[data-hs-tiep]')).toContainText('Chương 2. Python cho dữ liệu');
	await expect(page.locator('[data-hs-tiep] a[href="/ai-engineer/ch02-python-cho-du-lieu/01-chuoi-tuple-set/"]')).toBeVisible();
	await expect(page.locator('[data-hs-tiep]')).toContainText('Chọn chỉ số (40%)');
});

test('xuất, nhập và xoá dữ liệu', async ({ page }) => {
	page.on('dialog', (d) => d.accept());
	await gieo(page);
	await page.goto('/ho-so/');
	const [tai] = await Promise.all([page.waitForEvent('download'), page.click('[data-hs-xuat]')]);
	const tep = await tai.path();
	expect(tep).toBeTruthy();
	const json = JSON.parse(fs.readFileSync(tep!, 'utf8'));
	expect(Object.keys(json.duLieu)).toContain('air-tien-do-v1');
	expect(json.duLieu['air-tien-do-v1'].daDoc).toBeTruthy();

	const du = {
		duLieu: {
			'air-tien-do-v1': {
				daDoc: {
					'ai-engineer/ch00-lo-trinh-va-colab/01-lo-trinh/': '2026-11-16',
					'ai-engineer/ch01-python-tu-dau/01-bien-va-kieu/': '2026-11-16',
					'ai-engineer/ch02-python-cho-du-lieu/01-chuoi-tuple-set/': '2026-11-16',
					'ai-engineer/ch03-numpy/01-mang-va-shape/': '2026-11-16',
				},
				ngayHoc: ['2026-11-16'],
			},
		},
	};
	await page.locator('[data-hs-nhap]').setInputFiles({ name: 'ho-so.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(du)) });
	await expect(page.locator('[data-hs-tong]')).toContainText(`4/${TONG}`);
	await expect(page.locator('[data-hs-tt-dl]')).toContainText('Đã nhập dữ liệu');

	await page.click('[data-hs-xoa]');
	await expect(page.locator('[data-hs-tong]')).toContainText(`0/${TONG}`);
	await expect(page.locator('[data-hs-tt-dl]')).toContainText('Đã xoá');
});

test('mobile 375px: hồ sơ không tràn ngang', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await gieo(page);
	await page.goto('/ho-so/');
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);
});
