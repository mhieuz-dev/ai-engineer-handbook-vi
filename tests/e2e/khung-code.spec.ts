import { test, expect } from '@playwright/test';

const CH05 = '/ai-engineer/ch05-dai-so-tuyen-tinh/01-vector/';

test('khung code chỉ có ở trang chương', async ({ page }) => {
	await page.goto('/gioi-thieu/');
	await expect(page.locator('.kc-nut')).toHaveCount(0);
	await page.goto(CH05);
	await expect(page.locator('.kc-nut')).toBeVisible();
	await expect(page.locator('#kc-panel')).toBeHidden();
});

test('mở khung, chạy code, báo lỗi đúng dòng, trợ lý giải thích lỗi', async ({ page }) => {
	test.setTimeout(240_000);
	await page.goto(CH05);
	await page.locator('.kc-nut').click();
	await expect(page.locator('#kc-panel')).toBeVisible();
	await expect(page.locator('.cm-editor')).toBeVisible({ timeout: 30_000 });

	const noi = page.locator('.cm-content');
	await noi.click();
	await page.keyboard.press('Control+A');
	await page.keyboard.type('print("Xin chao tu Pyodide")');
	await page.locator('.kc-chay').click();
	await expect(page.locator('.kc-kq-ten')).toHaveText('Xong', { timeout: 120_000 });
	await expect(page.locator('.kc-out')).toHaveText('Xin chao tu Pyodide');

	await noi.click();
	await page.keyboard.press('Control+A');
	await page.keyboard.type('print(1/0)');
	await page.locator('.kc-chay').click();
	await expect(page.locator('.kc-kq-ten')).toHaveText('Lỗi ZeroDivisionError', { timeout: 60_000 });
	await expect(page.locator('.cm-dong-loi')).toHaveCount(1);
	await expect(page.locator('.kc-out')).toContainText('ZeroDivisionError');

	await page.locator('.kc-tab[data-tab="tro-ly"]').click();
	await page.locator('.kc-tl-nhanh[data-viec="loi"]').click();
	await expect(page.locator('.kc-tl-tra-loi')).toContainText('Chia cho 0');
});

test('Thử ngay chạy các khối phía trên rồi báo khớp Output', async ({ page }) => {
	test.setTimeout(240_000);
	await page.goto(CH05);
	const nut = page.locator('.kc-thu-ngay').first();
	await nut.evaluate((el) => el.scrollIntoView({ block: 'center' }));
	await nut.click();
	await expect(page.locator('#kc-panel')).toBeVisible();
	await expect(page.locator('.kc-kq-nhan')).toContainText('Khớp Output', { timeout: 180_000 });
	await expect(page.locator('.kc-thu-ngay.kc-dat')).toHaveCount(1);
});

test('khối cần PyTorch đổi thành Cần Colab', async ({ page }) => {
	await page.goto('/ai-engineer/ch25-pytorch-can-ban/01-tensor/');
	const so = await page.locator('.kc-can-colab').count();
	expect(so).toBeGreaterThan(0);
	await expect(page.locator('.kc-can-colab').first()).toHaveText('Cần Colab');
	await expect(page.locator('.kc-can-colab').first()).toBeDisabled();
});

test('tự lưu bản nháp trong trình duyệt', async ({ page }) => {
	await page.goto(CH05);
	await page.locator('.kc-nut').click();
	await expect(page.locator('.cm-editor')).toBeVisible({ timeout: 30_000 });
	const noi = page.locator('.cm-content');
	await noi.click();
	await page.keyboard.press('Control+A');
	const ma = 'x = 42  # nhap rieng cua toi';
	await page.keyboard.type(ma);
	await page.waitForTimeout(700);
	await page.reload();
	await page.locator('.kc-nut').click();
	await expect(page.locator('.cm-content')).toContainText('nhap rieng cua toi', { timeout: 30_000 });
});

test('Esc đóng khung; mobile mở toàn màn hình', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto(CH05);
	await page.locator('.kc-nut').click();
	await expect(page.locator('#kc-panel')).toBeVisible();
	const o = await page.locator('#kc-panel').boundingBox();
	expect(o!.x).toBeLessThanOrEqual(1);
	expect(o!.y).toBeLessThanOrEqual(1);
	expect(o!.width).toBeGreaterThanOrEqual(374);
	expect(o!.height).toBeGreaterThanOrEqual(811);
	await page.keyboard.press('Escape');
	await expect(page.locator('#kc-panel')).toBeHidden();
});
