import { test, expect } from '@playwright/test';

const GIAI_NHI_PHAN = `def dem_so_sanh(xs, x):
    lo, hi, dem = 0, len(xs) - 1, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        dem += 1
        if xs[mid] == x:
            return dem
        if xs[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return dem
`;

test('danh sách 31 bài toán, 6 module', async ({ page }) => {
	await page.goto('/toan-thuat-toan/');
	await expect(page.locator('.tn-the')).toHaveCount(31);
	await expect(page.locator('.tn-nhom')).toHaveCount(6);
	await expect(page.locator('[data-tn-tong]')).toContainText('0/31');
});

test('bài chứng minh: gợi ý, xem lời giải, rubric và đánh dấu đã hiểu', async ({ page }) => {
	await page.goto('/toan-thuat-toan/');
	await page.locator('.tn-the[data-tn-mo="1"]').click();
	await expect(page.locator('.tn-mota')).toContainText('log n');
	await page.locator('[data-tn-goiy="0"]').click();
	await expect(page.locator('[data-tn-goiy-noi]')).toContainText('Nấc 1:');
	await expect(page.locator('[data-tn-loi-giai]')).toBeHidden();
	await page.locator('[data-tn-xem]').click();
	await expect(page.locator('[data-tn-loi-giai]')).toBeVisible();
	await expect(page.locator('[data-tn-loi-giai]')).toContainText('log n < n < n log n');
	await expect(page.locator('[data-tn-loi-giai]')).toContainText('Vì sao đúng');
	await page.locator('[data-tn-rubric="0"]').check();
	await expect(page.locator('[data-tn-diem]')).toContainText('3/10');
	await page.locator('[data-tn-hieu]').click();
	await page.locator('[data-tn-quay]').click();
	await expect(page.locator('[data-tn-tong]')).toContainText('1/31');
	await expect(page.locator('.tn-the.da-giai')).toHaveCount(1);
});

test('bài code: chạy và nộp test ẩn', async ({ page }) => {
	test.setTimeout(180_000);
	await page.goto('/toan-thuat-toan/');
	await page.locator('.tn-the[data-tn-mo="6"]').click();
	await page.locator('.tn-nhap').fill(GIAI_NHI_PHAN);
	await page.locator('[data-tn-chay]').click();
	await expect(page.locator('[data-tn-kq]')).toContainText('Đạt ví dụ', { timeout: 120_000 });
	await page.locator('[data-tn-nop]').click();
	await expect(page.locator('[data-tn-kq]')).toContainText('toàn bộ test ẩn', { timeout: 120_000 });
	await page.locator('[data-tn-quay]').click();
	await expect(page.locator('[data-tn-tong]')).toContainText('1/31');
});

test('mobile 375px: toán không tràn ngang', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/toan-thuat-toan/');
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);
	await page.locator('.tn-the[data-tn-mo="1"]').click();
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);
});
