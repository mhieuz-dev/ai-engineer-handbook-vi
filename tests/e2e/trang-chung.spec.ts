import { test, expect } from '@playwright/test';

const TRANG_DAU = '/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/';

test('trang chủ: tiêu đề, hai thẻ nhánh, nút Bắt đầu học', async ({ page }) => {
	await page.goto('/');
	await expect(page.locator('h1')).toHaveText('AI & Robotics');
	await expect(page.getByText('Giáo trình tiếng Việt miễn phí: hiểu tận gốc AI, từ Python cơ bản đến mô hình ngôn ngữ lớn.')).toBeVisible();
	const ai = page.locator('.the-nhanh', { hasText: 'AI Engineer' });
	const robot = page.locator('.the-nhanh', { hasText: 'Robotics' });
	await expect(ai).toBeVisible();
	await expect(ai).toContainText('Đang viết');
	await expect(robot).toContainText('Sắp có');
	await expect(page.getByRole('link', { name: 'Bắt đầu học' })).toHaveAttribute('href', TRANG_DAU);
	await expect(page.getByText('Cách học trên trang này')).toBeVisible();
});

test('lộ trình: 65 dòng chương, chỉ chương 10 là link, còn lại có nhãn Sắp có', async ({ page }) => {
	await page.goto('/lo-trinh/');
	const dong = page.locator('li[id^="ch"]');
	await expect(dong).toHaveCount(65);
	await expect(page.locator('li#ch10 a')).toHaveAttribute('href', TRANG_DAU);
	await expect(page.locator('li[id^="ch"] a')).toHaveCount(1);
	await expect(page.locator('li[id^="ch"] .nhan-sap-co')).toHaveCount(64);
	await expect(page.locator('li#ch64')).toContainText('Phỏng vấn và portfolio');
});

test('notebook: bảng chương đã xuất bản có nút Colab và link GitHub', async ({ page }) => {
	await page.goto('/notebook/');
	const hang = page.locator('table tbody tr');
	await expect(hang).toHaveCount(1);
	await expect(hang).toContainText('ch10_hoi_quy_tuyen_tinh.ipynb');
	await expect(hang.locator('a.colab-nut')).toHaveAttribute('href', /colab\.research\.google\.com\/github\/mhieuz-dev\/ai-engineer-handbook-vi\/blob\/main\/notebooks\/ch10_hoi_quy_tuyen_tinh\.ipynb$/);
	await expect(hang.getByRole('link', { name: 'GitHub' })).toHaveAttribute('href', /github\.com\/mhieuz-dev\/ai-engineer-handbook-vi\/blob\/main\/notebooks\/ch10_hoi_quy_tuyen_tinh\.ipynb$/);
});

test('giới thiệu: Mhz, MIT, GitHub, báo lỗi, không nhắc Claude', async ({ page }) => {
	await page.goto('/gioi-thieu/');
	const noiDung = page.locator('main');
	await expect(noiDung).toContainText('Mhz');
	await expect(noiDung).toContainText('MIT');
	await expect(noiDung.getByRole('link', { name: 'LICENSE' })).toHaveAttribute('href', /github\.com\/mhieuz-dev\/ai-engineer-handbook-vi\/blob\/main\/LICENSE/);
	await expect(noiDung.getByRole('link', { name: 'GitHub Issues' })).toHaveAttribute('href', /github\.com\/mhieuz-dev\/ai-engineer-handbook-vi\/issues/);
	expect(await page.content()).not.toMatch(/claude/i);
});

test('menu trên cùng có Lộ trình, Thuật ngữ, Notebook', async ({ page, isMobile }) => {
	await page.goto('/');
	const nav = page.locator(isMobile ? '.nav-chung-mobile' : 'header .nav-chung');
	for (const [ten, href] of [['Lộ trình', '/lo-trinh/'], ['Thuật ngữ', '/thuat-ngu/'], ['Notebook', '/notebook/']]) {
		await expect(nav.getByRole('link', { name: ten })).toHaveAttribute('href', href);
	}
});

test('mobile 375px: trang chủ, lộ trình, notebook, giới thiệu không tràn ngang', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	for (const url of ['/', '/lo-trinh/', '/notebook/', '/gioi-thieu/']) {
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

test('desktop: menu phụ của sidebar ẩn, chỉ còn menu đầu trang', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	await expect(page.locator('.nav-sidebar')).toBeHidden();
	await expect(page.locator('header .nav-chung')).toBeVisible();
});
