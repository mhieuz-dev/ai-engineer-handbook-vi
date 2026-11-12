import { test, expect } from '@playwright/test';

const URL = '/ai-engineer/ch05-dai-so-tuyen-tinh/01-vector/';

test('thẻ video nhẹ: ảnh lười tải, bấm mở YouTube ở tab mới', async ({ page }) => {
	await page.goto(URL);
	const the = page.locator('.video-hoc .video-the');
	await expect(the).toHaveCount(1);
	await expect(the).toHaveAttribute('href', 'https://www.youtube.com/watch?v=fNk_zzaMoSs');
	await expect(the).toHaveAttribute('target', '_blank');
	const anh = the.locator('img');
	await expect(anh).toHaveAttribute('loading', 'lazy');
	await expect(anh).toHaveAttribute('src', /i\.ytimg\.com\/vi\/fNk_zzaMoSs\/mqdefault\.jpg$/);
	await expect(the.locator('.video-play')).toBeVisible();
	await expect(page.locator('.video-hoc iframe')).toHaveCount(0);
});

test('bản in ẩn ảnh, hiện đường dẫn video', async ({ page }) => {
	await page.goto(URL);
	await page.emulateMedia({ media: 'print' });
	await expect(page.locator('.video-hoc .video-anh')).toBeHidden();
	await expect(page.locator('.video-hoc .video-lien-ket')).toBeVisible();
	await expect(page.locator('.video-hoc .video-lien-ket')).toHaveText('youtube.com/watch?v=fNk_zzaMoSs');
});
