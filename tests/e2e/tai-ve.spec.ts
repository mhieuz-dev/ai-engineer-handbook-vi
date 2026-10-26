import { test, expect } from '@playwright/test';

type Trang = import('@playwright/test').Page;
const TRANG = '/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/';

async function bam(page: Trang, loc: import('@playwright/test').Locator) {
	if (await page.evaluate(() => navigator.maxTouchPoints > 0)) await loc.tap();
	else await loc.click();
}
const nutTaiVe = (page: Trang) => page.getByRole('button', { name: /Tải về/ });
const menu = (page: Trang) => page.getByRole('menu');

test('nút Tải về mở menu 3 mục, link đúng, bấm ra ngoài thì đóng', async ({ page }) => {
	await page.goto(TRANG);
	const nut = nutTaiVe(page);
	await expect(nut).toBeVisible();
	await expect(nut).toHaveAttribute('aria-haspopup', 'menu');
	await expect(nut).toHaveAttribute('aria-expanded', 'false');
	await bam(page, nut);
	await expect(nut).toHaveAttribute('aria-expanded', 'true');
	await expect(menu(page).getByRole('menuitem', { name: /Trang này \(PDF\)/ })).toBeVisible();
	await expect(menu(page).getByRole('menuitem', { name: /Cả chương \(PDF\)/ })).toHaveAttribute('href', '/in/ai-engineer/ch10-hoi-quy-tuyen-tinh/?in=1');
	const nb = menu(page).getByRole('menuitem', { name: /Notebook/ });
	await expect(nb).toHaveAttribute('href', /notebooks\/ch10_hoi_quy_tuyen_tinh\.ipynb$/);
	await expect(nb).toHaveAttribute('target', '_blank');
	await bam(page, page.locator('h1').first());
	await expect(menu(page)).toBeHidden();
	await expect(nut).toHaveAttribute('aria-expanded', 'false');
});

test('mobile 375px: nút trong viewport, menu không tràn ngang', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto(TRANG);
	const nut = nutTaiVe(page);
	await expect(nut).toBeVisible();
	const b = (await nut.boundingBox())!;
	expect(b.x).toBeGreaterThanOrEqual(0);
	expect(b.x + b.width).toBeLessThanOrEqual(375);
	await bam(page, nut);
	await expect(menu(page)).toBeVisible();
	const mb = (await menu(page).boundingBox())!;
	expect(mb.x).toBeGreaterThanOrEqual(0);
	expect(mb.x + mb.width).toBeLessThanOrEqual(375);
	expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);
});

test('desktop: Trang này gọi window.print, Escape đóng, cột phải có PDF trang này', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.addInitScript(() => { (window as any).print = () => { (window as any).__daIn = true; }; });
	await page.goto(TRANG);
	await expect(page.locator('.tai-ve').getByText('PDF trang này')).toBeVisible();
	await nutTaiVe(page).click();
	await page.keyboard.press('Escape');
	await expect(menu(page)).toBeHidden();
	await nutTaiVe(page).click();
	await menu(page).getByRole('menuitem', { name: /Trang này \(PDF\)/ }).click();
	expect(await page.evaluate(() => (window as any).__daIn)).toBe(true);
	await expect(menu(page)).toBeHidden();
});

test('in trang thường: chỉ còn nội dung bài', async ({ page }) => {
	await page.goto(TRANG);
	const an = ['header.header', '.nut-da-doc', '.nut-tai-ve', '.pagination-links'];
	for (const sel of an) await expect(page.locator(sel).first(), `${sel} hiện trên màn hình`).toBeVisible();
	await page.emulateMedia({ media: 'print' });
	await expect(page.locator('h1').first()).toBeVisible();
	for (const sel of [...an, '#starlight__sidebar']) {
		await expect(page.locator(sel).first(), sel).toBeHidden();
	}
});

test('in trang thường: nút Colab bị ẩn', async ({ page }) => {
	await page.goto('/kiem-thu/thanh-phan/');
	await expect(page.locator('.colab-nut').first()).toBeVisible();
	await page.emulateMedia({ media: 'print' });
	await expect(page.locator('.colab-nut').first()).toBeHidden();
});

test('trang thuật ngữ không có nút Tải về', async ({ page }) => {
	await page.goto('/thuat-ngu/');
	await expect(nutTaiVe(page)).toHaveCount(0);
});
