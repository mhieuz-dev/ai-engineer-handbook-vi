import { test, expect } from '@playwright/test';

const URL = '/ai-engineer/ch05-dai-so-tuyen-tinh/01-vector/';

test('thẻ video nhẹ: ảnh lười tải, chưa nhúng iframe', async ({ page }) => {
	await page.goto(URL);
	const the = page.locator('.video-hoc .video-the');
	await expect(the).toHaveCount(1);
	const nut = the.locator('.video-nut');
	await expect(nut).toHaveAttribute('href', 'https://www.youtube.com/watch?v=fNk_zzaMoSs');
	await expect(nut).toHaveAttribute('target', '_blank');
	const anh = the.locator('img');
	await expect(anh).toHaveAttribute('loading', 'lazy');
	await expect(anh).toHaveAttribute('src', /i\.ytimg\.com\/vi\/fNk_zzaMoSs\/mqdefault\.jpg$/);
	await expect(the.locator('.video-play')).toBeVisible();
	await expect(the.locator('.video-tieu-de')).toBeVisible();
	await expect(the.locator('.video-lien-ket')).toHaveAttribute('href', 'https://www.youtube.com/watch?v=fNk_zzaMoSs');
	await expect(the.locator('.video-lien-ket')).toHaveText('Mở trên YouTube ↗');
	await expect(page.locator('.video-hoc iframe')).toHaveCount(0);
});

test('bấm phát: nhúng youtube-nocookie, ảnh và nút phát ẩn đi', async ({ page }) => {
	await page.goto(URL);
	await page.locator('.video-nut').click();
	const iframe = page.locator('.video-hoc iframe');
	await expect(iframe).toHaveCount(1);
	await expect(iframe).toHaveAttribute('src', 'https://www.youtube-nocookie.com/embed/fNk_zzaMoSs?autoplay=1&rel=0');
	await expect(page.locator('.video-nut')).toBeHidden();
	await expect(page.locator('.video-lien-ket')).toBeVisible();
});

test('phát video khác thì video cũ dừng', async ({ page }) => {
	await page.goto(URL);
	// Dữ liệu thật mỗi chương một video: nhân bản thẻ để thử chuyện chuyển qua lại.
	await page.evaluate(() => {
		const the = document.querySelector('.video-the')!;
		const hai = the.cloneNode(true) as HTMLElement;
		hai.dataset.id = 'aaaaaaaaaaa';
		the.after(hai);
	});
	const thes = page.locator('.video-the');
	await thes.nth(0).locator('.video-nut').click();
	await expect(thes.nth(0).locator('iframe')).toHaveCount(1);
	await thes.nth(1).locator('.video-nut').click();
	await expect(thes.nth(0).locator('iframe')).toHaveCount(0);
	await expect(thes.nth(1).locator('iframe')).toHaveCount(1);
	await expect(thes.nth(0).locator('.video-nut')).toBeVisible();
});

test('bản in ẩn khung phát, hiện đường dẫn video', async ({ page }) => {
	await page.goto(URL);
	await page.emulateMedia({ media: 'print' });
	await expect(page.locator('.video-hoc .video-nut')).toBeHidden();
	await expect(page.locator('.video-hoc .video-url')).toBeVisible();
	await expect(page.locator('.video-hoc .video-url')).toHaveText('youtube.com/watch?v=fNk_zzaMoSs');
	await expect(page.locator('.video-hoc .video-lien-ket')).toBeHidden();
});
