import { test, expect } from '@playwright/test';
import { CHUONG } from '../../src/data/chuong';

test('hub Luyện tập: 5 thẻ có icon và số liệu tiến độ ngay màn hình đầu', async ({ page, isMobile }) => {
	await page.goto('/luyen-tap/');
	await expect(page.locator('.lt-khu')).toContainText('Luyện tập');
	const the = page.locator('.lt-mode .lt-the');
	await expect(the).toHaveCount(5);
	await expect(the.locator('.lt-ico svg')).toHaveCount(5);
	await expect(the.nth(0).locator('[data-lt-so="thi"]')).toHaveText('Chưa thi lần nào');
	await expect(the.nth(1).locator('[data-lt-so="thuat-toan"]')).toHaveText('0/41 bài đã giải');
	await expect(the.nth(2).locator('[data-lt-so="toan"]')).toHaveText('0/31 bài đã giải');
	await expect(the.nth(3).locator('[data-lt-so="phong-van"]')).toHaveText('Chưa luyện buổi nào');
	await expect(the.nth(4).locator('[data-lt-so="ho-so"]')).toHaveText('0% giáo trình');
	if (!isMobile) {
		const dau = await the.nth(1).boundingBox();
		expect(dau!.y).toBeLessThan(900);
	}
});

test('hub Luyện tập: đọc tiến độ thật từ storage', async ({ page }) => {
	await page.addInitScript((soChuong) => {
		localStorage.setItem('air-bai-thi-v1', JSON.stringify([{ diem: 6 }, { diem: 8 }]));
		localStorage.setItem('air-thuat-toan-v1', JSON.stringify({ daGiai: { a: '1', b: '1', c: '1' }, daThu: {}, ngay: [] }));
		localStorage.setItem('air-toan-v1', JSON.stringify({ daGiai: {}, ngay: [] }));
		localStorage.setItem('air-phong-van-v1', JSON.stringify([{ id: 'x' }]));
		localStorage.setItem('air-tien-do-v1', JSON.stringify({ daDoc: { 'ai-engineer/ch00-lo-trinh-va-colab/01-lo-trinh': '2026-11-16' }, ngayHoc: [] }));
	}, CHUONG.length);
	await page.goto('/luyen-tap/');
	await expect(page.locator('[data-lt-so="thi"]')).toHaveText('2 lần thi · TB 7.0/10');
	await expect(page.locator('[data-lt-so="thuat-toan"]')).toHaveText('3/41 bài đã giải');
	await expect(page.locator('[data-lt-so="phong-van"]')).toHaveText('1 buổi đã luyện');
	await expect(page.locator('[data-lt-so="ho-so"]')).toContainText('% giáo trình');
});

test('phòng thi: hai tab Theo chủ đề / Theo chương, đổi tab và bàn phím', async ({ page }) => {
	await page.goto('/phong-thi/');
	const tabChuDe = page.locator('[data-pt-tab="chude"]');
	const tabChuong = page.locator('[data-pt-tab="chuong"]');
	const panelChuDe = page.locator('[data-pt-panel="chude"]');
	const panelChuong = page.locator('[data-pt-panel="chuong"]');
	await expect(tabChuDe).toHaveAttribute('aria-selected', 'true');
	await expect(panelChuDe).toBeVisible();
	await expect(panelChuong).toBeHidden();
	await expect(page.locator('[data-pt-chude-id]').first()).toBeVisible();

	await tabChuong.click();
	await expect(tabChuong).toHaveAttribute('aria-selected', 'true');
	await expect(tabChuDe).toHaveAttribute('aria-selected', 'false');
	await expect(panelChuong).toBeVisible();
	await expect(panelChuDe).toBeHidden();
	await expect(page.locator('[data-pt-bat-dau]')).toBeVisible();

	await tabChuong.focus();
	await page.keyboard.press('ArrowLeft');
	await expect(tabChuDe).toHaveAttribute('aria-selected', 'true');
	await expect(panelChuDe).toBeVisible();
});

test('phòng thi: tab Theo chương vẫn bắt đầu thi được', async ({ page }) => {
	await page.goto('/phong-thi/');
	await page.locator('[data-pt-tab="chuong"]').click();
	await page.selectOption('[data-pt-kieu]', 'nhanh');
	await page.uncheck('[data-pt-gio]');
	await page.locator('[data-pt-bat-dau]').click();
	await expect(page.locator('.pt-thi')).toBeVisible();
	await expect(page.locator('.pt-dem')).toContainText('Câu 1/');
});
