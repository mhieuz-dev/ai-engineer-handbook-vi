import { test, expect } from '@playwright/test';

const URL = '/kiem-thu/thanh-phan/';

test('desktop: rê chuột hiện nhắc nhanh', async ({ page }, info) => {
	test.skip(info.project.name !== 'desktop');
	await page.goto(URL);
	const tip = page.locator('.term-wrap .tip').first();
	await expect(tip).toBeHidden();
	await page.locator('.term').first().hover();
	await expect(tip).toBeVisible();
	await expect(tip).toContainText('NHẮC NHANH');
	await expect(tip).toContainText('Học kỹ ở Chương 6');
});

test('mobile: chạm mở, chạm lại đóng, chạm ra ngoài đóng', async ({ page }, info) => {
	test.skip(info.project.name !== 'mobile');
	await page.goto(URL);
	const term = page.locator('.term').first();
	const tip = page.locator('.term-wrap .tip').first();
	await term.evaluate((el) => el.scrollIntoView({ block: 'center' }));
	await term.tap();
	await expect(tip).toBeVisible();
	await expect(term).toHaveAttribute('aria-expanded', 'true');
	const box = await tip.boundingBox();
	expect(box!.x).toBeGreaterThanOrEqual(0);
	expect(box!.x + box!.width).toBeLessThanOrEqual(375);
	await term.tap();
	await expect(tip).toBeHidden();
	await term.tap();
	await expect(tip).toBeVisible();
	await page.locator('h1').tap();
	await expect(tip).toBeHidden();
	await expect(term).toHaveAttribute('aria-expanded', 'false');
});

test('mobile: thuật ngữ sát mép phải vẫn nằm trong 375px', async ({ page }, info) => {
	test.skip(info.project.name !== 'mobile');
	await page.goto(URL);
	const wrap = page.locator('.term-wrap').last();
	await wrap.locator('.term').evaluate((el) => el.scrollIntoView({ block: 'center' }));
	await wrap.locator('.term').tap();
	const tip = wrap.locator('.tip');
	await expect(tip).toBeVisible();
	const box = await tip.boundingBox();
	expect(box!.x).toBeGreaterThanOrEqual(0);
	expect(box!.x + box!.width).toBeLessThanOrEqual(375);
});

test('bàn phím: Tab tới link Học kỹ khi tooltip còn mở, Escape đóng', async ({ page }) => {
	await page.goto(URL);
	const wrap = page.locator('.term-wrap').first();
	const tip = wrap.locator('.tip');
	await wrap.locator('.term').focus();
	await expect(tip).toBeVisible();
	await page.keyboard.press('Tab');
	await expect(wrap.getByRole('link', { name: /Học kỹ ở Chương 6/ })).toBeFocused();
	await expect(tip).toBeVisible();
	await page.keyboard.press('Escape');
	await expect(tip).toBeHidden();
	await expect(wrap.locator('.term')).toBeFocused();
	await page.keyboard.press('Enter');
	await expect(tip).toBeVisible();
	await page.keyboard.press('Enter');
	await expect(tip).toBeHidden();
});

test('trang Thuật ngữ có mục Đạo hàm, không lộ trang kiểm thử', async ({ page }) => {
	await page.goto('/thuat-ngu/');
	const muc = page.locator('#dao-ham');
	await expect(muc).toContainText('Đạo hàm');
	await expect(muc.locator('a[href*="kiem-thu"]')).toHaveCount(0);
	await expect(page.locator('a[href*="/kiem-thu/"]')).toHaveCount(0);
});

test('bấm vào nội dung tooltip không đóng, bấm ra ngoài thì đóng', async ({ page }, info) => {
	const mobile = info.project.name === 'mobile';
	await page.goto(URL);
	const term = page.locator('.term').first();
	const tip = page.locator('.term-wrap .tip').first();
	const bam = (l: ReturnType<typeof page.locator>) => (mobile ? l.tap() : l.click());
	await term.evaluate((el) => el.scrollIntoView({ block: 'center' }));
	await bam(term);
	await expect(tip).toBeVisible();
	await bam(tip.locator('.nd'));
	await expect(tip).toBeVisible();
	await bam(page.locator('h1'));
	await expect(tip).toBeHidden();
});

test('trang chương 10: thuật ngữ học kỹ ở chính chương 10 không mời sang chương 10', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	const tip = (ten: RegExp) => page.locator('.term-wrap .tip', { has: page.locator('.nhan', { hasText: ten }) }).first();
	await expect(tip(/· MSE$/)).toHaveCount(1);
	await expect(tip(/· MSE$/).locator('.hoc-ky')).toHaveCount(0);
	await expect(tip(/· ĐẠO HÀM$/).locator('.hoc-ky')).toHaveText('Học kỹ ở Chương 6 →');
	await page.goto('/thuat-ngu/');
	await expect(page.locator('#mse .hoc-ky a')).toHaveText('Học kỹ ở Chương 10 →');
});

test('câu riêng của chương (oDay) chỉ hiện trong tooltip, không có ở trang Thuật ngữ', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/');
	const tip = page.locator('.term-wrap .tip', { has: page.locator('.nhan', { hasText: /· ĐẶC TRƯNG$/ }) });
	await expect(tip.locator('.o-day')).toHaveText('Ở đây chỉ có một đặc trưng là số giờ tự học.');
	await page.goto('/thuat-ngu/');
	await expect(page.locator('#dac-trung')).toContainText('Đặc trưng là một thông tin đầu vào');
	await expect(page.locator('main')).not.toContainText('Ở đây');
});
