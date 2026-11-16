import { test, expect } from '@playwright/test';

const GIAI = `def hai_don(gia, tong):
    thay = {}
    for j, x in enumerate(gia):
        if tong - x in thay:
            return [thay[tong - x], j]
        thay[x] = j
    return []
`;

test('danh sách 41 bài, 13 dạng, có link LeetCode', async ({ page }) => {
	await page.goto('/thuat-toan/');
	await expect(page.locator('.tt-the')).toHaveCount(41);
	await expect(page.locator('.tt-nhom')).toHaveCount(13);
	await expect(page.locator('[data-tt-tong]')).toContainText('0/41');
	await page.locator('.tt-the[data-tt-mo="1"]').click();
	await expect(page.locator('.tt-mota')).toContainText('sàn thương mại điện tử');
	await expect(page.locator('.tt-link a')).toHaveAttribute('href', 'https://leetcode.com/problems/two-sum/');
});

test('nộp bài: sai thì chưa đạt, đúng thì đạt và mở lời giải', async ({ page }) => {
	test.setTimeout(180_000);
	await page.goto('/thuat-toan/');
	await page.locator('.tt-the[data-tt-mo="1"]').click();
	const ta = page.locator('.tt-nhap');
	await ta.fill('def hai_don(gia, tong):\n    return [0, 0]\n');
	await page.locator('[data-tt-nop]').click();
	await expect(page.locator('[data-tt-kq]')).toContainText('Chưa đạt', { timeout: 120_000 });

	await ta.fill(GIAI);
	await page.locator('[data-tt-nop]').click();
	await expect(page.locator('[data-tt-kq]')).toContainText('toàn bộ test ẩn', { timeout: 120_000 });
	await expect(page.locator('[data-tt-loi-giai]')).toBeVisible();
	await expect(page.locator('[data-tt-loi-giai]')).toContainText('Độ phức tạp');
	await expect(page.locator('.tt-chung-minh')).toContainText('bảng băm');

	await page.locator('[data-tt-quay]').click();
	await expect(page.locator('[data-tt-tong]')).toContainText('1/41');
	await expect(page.locator('.tt-the.da-giai')).toHaveCount(1);
});

test('lộ trình từ dễ đến khó: 41 bước, đồ án cuối', async ({ page }) => {
	await page.goto('/thuat-toan/');
	await page.getByRole('tab', { name: 'Từ dễ đến khó' }).click();
	await expect(page.locator('.tt-nhom')).toHaveCount(1);
	await expect(page.locator('.tt-buoc')).toHaveCount(41);
	await expect(page.locator('.tt-buoc').first()).toHaveText('Bước 1');
	await expect(page.locator('.tt-the[data-tt-mo="41"]')).toContainText('Đồ án tốt nghiệp');
	await expect(page.locator('.tt-the[data-tt-mo="41"] .tt-buoc')).toHaveText('Bước 41');
});

test('gợi ý ba nấc và chịu thua mở lời giải', async ({ page }) => {
	await page.goto('/thuat-toan/');
	await page.locator('.tt-the[data-tt-mo="2"]').click();
	await page.locator('[data-tt-goiy="0"]').click();
	await expect(page.locator('[data-tt-goiy-noi]')).toContainText('Nấc 1:');
	await page.locator('[data-tt-goiy="2"]').click();
	await expect(page.locator('[data-tt-goiy-noi]')).toContainText('Nấc 3:');
	await expect(page.locator('[data-tt-loi-giai]')).toBeHidden();
	await page.locator('[data-tt-chiu]').click();
	await expect(page.locator('[data-tt-loi-giai]')).toBeVisible();
	await expect(page.locator('[data-tt-chiu]')).toBeHidden();
});

test('mobile 375px: luyện thuật toán không tràn ngang', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/thuat-toan/');
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);
	await page.locator('.tt-the[data-tt-mo="1"]').click();
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);
});
