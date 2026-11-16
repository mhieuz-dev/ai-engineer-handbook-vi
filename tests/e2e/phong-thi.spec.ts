import { test, expect, type Page } from '@playwright/test';

const GIAI_CHAO = 'def chao(ten):\n    return f"Xin chào, {ten}!"\n';

const GIAI_DOANH_THU = `import pandas as pd
df = pd.read_csv("doanh_thu_2026.csv", dtype=str)
def so(s):
    if pd.isna(s) or not str(s).strip(): return None
    s = str(s).strip()
    if "," in s and "." in s: s = s.replace(".", "").replace(",", ".")
    elif "," in s: s = s.replace(",", ".")
    return float(s)
df["so_tien"] = df["so_tien"].map(so)
df["ngay"] = pd.to_datetime(df["ngay"], format="mixed", dayfirst=True)
sach = df.dropna(subset=["so_tien"]).drop_duplicates()
`;

async function chiChuong(page: Page, so: number) {
	await page.uncheck('[data-pt-tatca]');
	const cbs = page.locator('[data-pt-chuong-so]');
	for (let i = 0; i < (await cbs.count()); i++) await cbs.nth(i).uncheck();
	await cbs.nth(so).check();
}

test('thi nhanh: 12 câu, nộp bài, ra điểm và bản đồ kiến thức', async ({ page }) => {
	test.setTimeout(120_000);
	page.on('dialog', (d) => d.accept());
	await page.goto('/phong-thi/');
	await page.click('[data-pt-tab="chuong"]');
	expect(await page.locator('[data-pt-chuong-so]').count()).toBeGreaterThanOrEqual(5);
	await page.selectOption('[data-pt-kieu]', 'nhanh');
	await page.uncheck('[data-pt-gio]');
	await page.click('[data-pt-bat-dau]');
	await expect(page.locator('.pt-ds button')).toHaveCount(12);
	for (let i = 0; i < 12; i++) {
		const radio = page.locator('.pt-lua-chon input[type="radio"]');
		if (await radio.count()) await radio.first().check();
		else {
			const ta = page.locator('.pt-chu').first();
			if (await ta.count()) await ta.fill('Câu trả lời thử để kiểm tra luồng nộp bài.');
		}
		if (i < 11) await page.click('[data-pt-sau]');
	}
	await expect(page.locator('.pt-ds button.da-lam')).toHaveCount(12);
	await page.click('[data-pt-nop]');
	await expect(page.locator('.pt-kq')).toBeVisible({ timeout: 60_000 });
	await expect(page.locator('.pt-diem-so')).toContainText('/10');
	await expect(page.locator('.pt-bando tbody tr')).not.toHaveCount(0);
	await expect(page.locator('.pt-xem')).toHaveCount(12);
});

test('câu code chấm bằng test ẩn: Ch0 chao(ten)', async ({ page }) => {
	test.setTimeout(180_000);
	await page.goto('/phong-thi/');
	await page.click('[data-pt-tab="chuong"]');
	await page.selectOption('[data-pt-kieu]', 'chuong');
	await page.uncheck('[data-pt-gio]');
	await chiChuong(page, 0);
	await page.click('[data-pt-bat-dau]');
	await expect(page.locator('.pt-ds button')).toHaveCount(14);
	await page.click('.pt-ds button[data-i="12"]');
	await page.locator('.pt-code').fill(GIAI_CHAO);
	await page.locator('.pt-chay').click();
	await expect(page.locator('.pt-kq-code')).toContainText('Đạt', { timeout: 150_000 });
});

test('case Ch4: nạp CSV có bẫy vào Pyodide rồi chấm test ẩn', async ({ page }) => {
	test.setTimeout(180_000);
	await page.goto('/phong-thi/');
	await page.click('[data-pt-tab="chuong"]');
	await page.selectOption('[data-pt-kieu]', 'chuong');
	await page.uncheck('[data-pt-gio]');
	await chiChuong(page, 4);
	await page.click('[data-pt-bat-dau]');
	await page.click('.pt-ds button[data-i="13"]');
	await expect(page.locator('.pt-boi-canh')).toContainText('doanh_thu_2026.csv');
	await expect(page.locator('.pt-nv')).toHaveCount(3);
	await page.locator('.pt-nv .pt-code[data-nv="1"]').fill(GIAI_DOANH_THU);
	await page.locator('.pt-nv .pt-chay[data-nv="1"]').click();
	await expect(page.locator('.pt-kq-code').filter({ hasText: 'Đạt' })).toHaveCount(1, { timeout: 150_000 });
});

test('mobile 375px: phòng thi không tràn ngang', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/phong-thi/');
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);
});
