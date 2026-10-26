import { test, expect } from '@playwright/test';

const C10 = '/ai-engineer/ch10-hoi-quy-tuyen-tinh';
const IN10 = '/in/ai-engineer/ch10-hoi-quy-tuyen-tinh/';

test('trang chương có breadcrumb và thời gian đọc', async ({ page }) => {
	await page.goto(`${C10}/02-toan/`);
	const crumb = page.locator('.crumb');
	await expect(crumb).toContainText('Phần II');
	await expect(crumb).toContainText('Chương 10');
	await expect(crumb).toContainText('phút đọc');
});

test('trang ngoài chương không có breadcrumb', async ({ page }) => {
	await page.goto('/');
	await expect(page.locator('.crumb')).toHaveCount(0);
});

test('cột phải có TẢI VỀ với PDF chương và notebook', async ({ page }) => {
	await page.goto(`${C10}/02-toan/`);
	const khoi = page.locator('.tai-ve');
	await expect(khoi).toContainText('TẢI VỀ');
	await expect(khoi.locator('a', { hasText: 'PDF cả chương' })).toHaveAttribute('href', `${IN10}?in=1`);
	await expect(khoi.locator('a', { hasText: 'Notebook' })).toHaveAttribute(
		'href',
		'https://github.com/mhieuz-dev/ai-engineer-handbook-vi/blob/main/notebooks/ch10_hoi_quy_tuyen_tinh.ipynb',
	);
});

test('trang in có đủ 6 mục theo thứ tự, không thanh trượt, không nút Đã đọc', async ({ page }) => {
	await page.goto(IN10);
	await page.emulateMedia({ media: 'print' });
	const tieuDe = await page.locator('.in-muc > h2').allTextContents();
	expect(tieuDe).toEqual([
		'Bài toán và trực giác',
		'Toán từng bước',
		'Tính tay một ví dụ nhỏ',
		'Code',
		'Đọc kết quả',
		'Bài tập',
	]);
	await expect(page.locator('input[type=range]')).not.toBeVisible();
	await expect(page.locator('.nut-da-doc')).toHaveCount(0);
	await expect(page.locator('meta[name=robots]')).toHaveAttribute('content', /noindex/);
});
