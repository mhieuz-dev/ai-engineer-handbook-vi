import { test, expect } from '@playwright/test';

const URL = '/kiem-thu/thanh-phan/';

async function datThanh(page: import('@playwright/test').Page, v: string) {
	const thanh = page.locator('[data-tn-lr] input[type=range]');
	await thanh.fill(v);
	await thanh.dispatchEvent('input');
}

test('thanh trượt 0,135 phát nổ, 0,05 hội tụ', async ({ page }) => {
	await page.goto(URL);
	await datThanh(page, '0.135');
	await expect(page.getByText('Phát nổ!')).toBeVisible();
	await expect(page.getByText('Bước chân dài quá ngưỡng 0,12, loss tăng mãi.')).toBeVisible();
	await datThanh(page, '0.05');
	await expect(page.getByText('MSE = 0,050')).toBeVisible();
	await expect(page.locator('[data-tn-lr] [data-gia-tri]')).toHaveText('0,050');
	await datThanh(page, '0.118');
	await expect(page.locator('[data-tn-lr] [data-ketqua]')).toContainText('gần ngưỡng 0,12');
	await expect(page.locator('[data-tn-lr] [data-ketqua]')).not.toContainText('hơi ngắn');
});

test('thanh trượt dùng được bằng bàn phím', async ({ page, isMobile }) => {
	test.skip(!!isMobile, 'bàn phím chỉ kiểm trên desktop');
	await page.goto(URL);
	const thanh = page.locator('[data-tn-lr] input[type=range]');
	await thanh.focus();
	await page.keyboard.press('ArrowRight');
	await expect(page.locator('[data-tn-lr] [data-gia-tri]')).toHaveText('0,051');
});

test('tự kiểm tra: sai rồi chọn lại đúng, hai câu không ảnh hưởng nhau', async ({ page }) => {
	await page.goto(URL);
	const bam = async (loc: import('@playwright/test').Locator) =>
		(await page.evaluate(() => navigator.maxTouchPoints > 0)) ? loc.tap() : loc.click();
	const cau1 = page.locator('[data-tkt]').nth(0);
	const cau2 = page.locator('[data-tkt]').nth(1);
	await bam(cau1.getByRole('button', { name: 'Vẫn chạy tốt' }));
	await expect(cau1.getByText('Chưa đúng.')).toBeVisible();
	await expect(cau1.getByRole('button', { name: 'Vẫn chạy tốt' })).toHaveClass(/sai/);
	await expect(cau2.locator('[data-phan-hoi]')).toBeEmpty();
	await bam(cau1.getByRole('button', { name: 'Loss phát nổ' }));
	await expect(cau1.getByText('Đúng!')).toBeVisible();
	await expect(cau1.getByText('0,000037')).toBeVisible();
	await expect(cau1.getByRole('button', { name: 'Loss phát nổ' })).toHaveClass(/dung/);
	await expect(cau2.locator('[data-phan-hoi]')).toBeEmpty();
});
