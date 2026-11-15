import { test, expect, type Page } from '@playwright/test';

const CH05 = '/ai-engineer/ch05-dai-so-tuyen-tinh/01-vector/';

async function moTroLy(page: Page) {
	await page.goto(CH05);
	await page.locator('.kc-nut').click();
	await expect(page.locator('.cm-editor')).toBeVisible({ timeout: 30_000 });
	await page.locator('.kc-tab[data-tab="tro-ly"]').click();
}

test('không có máy chủ AI thì trợ lý vẫn trả lời cục bộ', async ({ page }) => {
	await moTroLy(page);
	await page.locator('.kc-tl-nhanh[data-viec="tom-tat"]').click();
	await expect(page.locator('.kc-tl-tra-loi')).toContainText('Trang này có các mục', { timeout: 15_000 });
	await expect(page.locator('.kc-tl-nguon')).toContainText('cục bộ');
});

test('có máy chủ: hiện câu trả lời, nguồn, và đưa code vào khung', async ({ page }) => {
	await page.route('**/api/ai', (route) =>
		route.fulfill({
			status: 200,
			contentType: 'application/json',
			body: JSON.stringify({
				text: '**Đậm** và `inline`\n\n```python\nprint(1)\n```\n\nCông thức $E=mc^2$ đẹp.',
				nhaCungCap: 'gemini',
				con: 39,
			}),
		}),
	);
	await moTroLy(page);
	await page.locator('.kc-tl-nhanh[data-viec="tom-tat"]').click();
	await expect(page.locator('.kc-tl-tra-loi strong')).toHaveText('Đậm');
	await expect(page.locator('.kc-tl-tra-loi .katex').first()).toBeVisible();
	await expect(page.locator('.kc-tl-nguon')).toContainText('gemini');
	await expect(page.locator('.kc-tl-nguon')).toContainText('còn 39 điểm');

	await page.locator('.kc-md-dua').click();
	await expect(page.locator('.kc-tab[data-tab="code"]')).toHaveAttribute('aria-selected', 'true');
	await expect(page.locator('.cm-content')).toContainText('print(1)');
});

test('hết lượt: báo rõ và trả lời cục bộ', async ({ page }) => {
	await page.route('**/api/ai', (route) =>
		route.fulfill({
			status: 429,
			contentType: 'application/json',
			body: JSON.stringify({ loi: 'het-luot', thongBao: 'Hết lượt AI miễn phí hôm nay.' }),
		}),
	);
	await moTroLy(page);
	await page.locator('.kc-tl-nhanh[data-viec="hoi-nguoc"]').click();
	await expect(page.locator('.kc-tl-tra-loi')).toContainText('Hết lượt AI miễn phí hôm nay.', { timeout: 15_000 });
	await expect(page.locator('.kc-tl-tra-loi')).toContainText('Thử trả lời');
});

test('lưu và xoá key riêng trên máy', async ({ page }) => {
	await moTroLy(page);
	await page.locator('.kc-key summary').click();
	await page.locator('.kc-key-khoa').fill('AIza-gia-lap');
	await page.locator('.kc-key-luu').click();
	await expect(page.locator('.kc-key-tt')).toContainText('Đang dùng key gemini');
	const luu = await page.evaluate(() => localStorage.getItem('air-ai-key-v1'));
	expect(luu).toContain('AIza-gia-lap');
	await page.reload();
	await page.locator('.kc-nut').click();
	await page.locator('.kc-tab[data-tab="tro-ly"]').click();
	await page.locator('.kc-key summary').click();
	await expect(page.locator('.kc-key-tt')).toContainText('Đang dùng key gemini');
	await page.locator('.kc-key-xoa').click();
	await expect(page.locator('.kc-key-tt')).toContainText('Chưa có key riêng');
});
