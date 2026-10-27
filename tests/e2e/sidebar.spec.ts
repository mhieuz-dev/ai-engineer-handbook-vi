import { test, expect } from '@playwright/test';
import { readdirSync } from 'node:fs';
import { CHUONG, PHAN, chuongDaXuatBan } from '../../src/data/chuong';

async function moSidebar(page: import('@playwright/test').Page) {
	// trên điện thoại sidebar nằm trong menu thu gọn
	const nutMenu = page.locator('button.sl-menu-button');
	if (await nutMenu.isVisible()) await nutMenu.click();
}

// Chương chưa viết đầu tiên (bất kể Phần nào) và chương đã viết lớn nhất: tự lấy từ dữ liệu, không ghi cứng số chương.
const chuaViet = CHUONG.find((c) => c.trangThai === 'sap-co')!;
const phanChuaViet = PHAN.find((p) => p.id === chuaViet.phan)!;
const cuoiCung = [...chuongDaXuatBan()].sort((a, b) => b.so - a.so)[0];
const trangCuoi = readdirSync(`src/content/docs/${cuoiCung.slug}`).filter((f) => f.endsWith('.mdx')).sort().at(-1)!.replace(/\.mdx$/, '');
const soHai = (c: { so: number }) => `ch${String(c.so).padStart(2, '0')}`;

test('sidebar: chương chưa viết chỉ là nhãn Sắp có', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/');
	await moSidebar(page);
	const sb = page.locator('nav.sidebar, #starlight__sidebar').first();
	await expect(sb.getByText('Phần II. Machine Learning cổ điển')).toBeVisible();
	const phan = sb.locator('summary', { hasText: phanChuaViet.ten }).locator('xpath=..');   // thẻ details của đúng Phần đó
	if (!(await phan.evaluate((d) => (d as HTMLDetailsElement).open))) await phan.locator('summary').first().click();   // Phần chỉ có chương Sắp có thì thu gọn sẵn
	const nhan = `${chuaViet.so}. ${chuaViet.ten}`; // kèm số chương: "Dự án Phần II" là chuỗi con của "Dự án Phần III"
	const muc = sb.locator('[aria-disabled="true"]', { hasText: nhan });
	await expect(muc).toBeVisible();
	await expect(muc).toContainText('Sắp có');
	await expect(sb.locator('a', { hasText: nhan })).toHaveCount(0);
});

test('trang cuối của chương đã viết lớn nhất không có Tiếp trỏ tới chương chưa viết', async ({ page }) => {
	await page.goto(`/${cuoiCung.slug}/${trangCuoi}/`);
	await expect(page.locator(`a[href*="${soHai({ so: cuoiCung.so + 1 })}"]`)).toHaveCount(0);
	await expect(page.locator('a[rel="next"]')).toHaveCount(0);
});

test('các trang chương 10 xếp 01..06 và có data-slug', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/');
	await moSidebar(page);
	const links = page.locator('a[data-slug^="ai-engineer/ch10-hoi-quy-tuyen-tinh/"]');
	const slugs = await links.evaluateAll((as) => as.map((a) => (a as HTMLElement).dataset.slug));
	expect(slugs).toEqual(['01-truc-giac','02-toan','03-tinh-tay','04-code','05-doc-ket-qua','06-bai-tap'].map((s) => `ai-engineer/ch10-hoi-quy-tuyen-tinh/${s}`));
});

test('Phần chưa có chương xong thu gọn kèm đếm, Phần có chương xong mở sẵn', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/');
	await moSidebar(page);
	const sb = page.locator('nav.sidebar, #starlight__sidebar').first();
	// Phần đầu tiên chưa có chương nào xong, lấy từ dữ liệu (đầu tiên là Phần III, rồi III-B, IV khi viết tiếp)
	const phanTrong = PHAN.find((p) => p.nhanh === 'ai-engineer' && !chuongDaXuatBan().some((c) => c.phan === p.id))!;
	const thu = sb.locator('summary', { hasText: phanTrong.ten }).locator('xpath=..');
	await expect(thu).not.toHaveAttribute('open', '');
	await expect(thu.locator('summary')).toContainText(/· \d+ chương sắp có/);
	const phan2 = sb.locator('summary', { hasText: 'Phần II. Machine Learning cổ điển' }).locator('xpath=..');
	await expect(phan2).toHaveAttribute('open', '');
});

test('desktop: sidebar là thẻ nổi bo góc, mục đang đọc là viên trắng có chấm', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	const the = page.locator('.sidebar-content');
	expect(parseFloat(await the.evaluate((e) => getComputedStyle(e).borderTopLeftRadius))).toBeGreaterThanOrEqual(12);
	expect(await the.evaluate((e) => getComputedStyle(e).boxShadow)).not.toBe('none');
	await expect(the.locator('.sb-nhan')).toHaveText(/menu · chương trình/i);
	const dangDoc = the.locator('a[aria-current="page"]');
	await expect(dangDoc).toHaveText('Toán từng bước');
	expect(await dangDoc.evaluate((e) => getComputedStyle(e).backgroundColor)).toBe('rgb(255, 255, 255)');
	expect(await dangDoc.evaluate((e) => getComputedStyle(e, '::before').content)).toBe('""');
	// không có ba chấm cửa sổ kiểu macOS
	await expect(page.locator('.sidebar-content [class*="cham"], .sidebar-content [class*="dot"]')).toHaveCount(0);
});

test('desktop: nút ‹ thu gọn sidebar, nhớ khi tải lại, mở lại bằng bàn phím', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	const nut = page.getByRole('button', { name: 'Thu gọn mục lục' });
	const the = page.locator('.sidebar-content');
	const trai = () => page.locator('main').evaluate((e) => e.getBoundingClientRect().left);
	await expect(nut).toHaveAttribute('aria-expanded', 'true');
	await expect(nut).toHaveAttribute('aria-controls', 'starlight__sidebar');
	await expect(the).toBeVisible();
	const traiTruoc = await trai();
	await nut.click();
	const nutMo = page.getByRole('button', { name: 'Mở mục lục' });
	await expect(nutMo).toHaveAttribute('aria-expanded', 'false');
	await expect(the).toBeHidden();
	expect(await trai()).toBeLessThan(traiTruoc - 100);
	await page.reload();
	await expect(nutMo).toHaveAttribute('aria-expanded', 'false');
	await expect(the).toBeHidden();
	await expect(nutMo).toBeVisible();
	await nutMo.focus();
	await page.keyboard.press('Enter');
	await expect(nut).toHaveAttribute('aria-expanded', 'true');
	await expect(the).toBeVisible();
	await page.reload();
	await expect(the).toBeVisible();
	await expect(nut).toHaveAttribute('aria-expanded', 'true');
});

test('mobile: không có nút thu gọn, menu ☰ vẫn mở sidebar', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.addInitScript(() => localStorage.setItem('air-sidebar-thu-gon', '1'));
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	await expect(page.locator('.nut-thu-gon')).toBeHidden();
	await page.locator('button.sl-menu-button').tap();
	await expect(page.locator('.sidebar-content a[aria-current="page"]')).toBeVisible();
});

/** Tương phản thấp nhất giữa chữ và nền đã trộn (nền trong suốt chồng lên nền trang) của mọi chữ hiện trong sidebar. */
async function tuongPhanThapNhat(page: import('@playwright/test').Page) {
	return page.locator('.sidebar-content').evaluate((goc) => {
		const doc = (s: string): number[] => {
			const m = s.match(/[\d.]+/g)!.map(Number);
			if (s.startsWith('color(')) return [m[0] * 255, m[1] * 255, m[2] * 255, m[3] ?? 1];
			return [m[0], m[1], m[2], m[3] ?? 1];
		};
		const tron = (tren: number[], duoi: number[]) => [0, 1, 2].map((i) => tren[i] * tren[3] + duoi[i] * (1 - tren[3])).concat(1);
		const nenCua = (el: Element | null): number[] => {
			if (!el) return doc(getComputedStyle(document.body).backgroundColor);
			// nền kính của thẻ nằm ở ::before
			const c = doc(getComputedStyle(el, el === goc ? '::before' : null).backgroundColor);
			if (c[3] === 1) return c;
			return tron(c, nenCua(el.parentElement));
		};
		const L = (c: number[]) => {
			const [r, g, b] = c.slice(0, 3).map((v) => {
				const x = v / 255;
				return x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
			});
			return 0.2126 * r + 0.7152 * g + 0.0722 * b;
		};
		let thap = { tile: 99, chu: '' };
		const walker = document.createTreeWalker(goc, NodeFilter.SHOW_TEXT);
		while (walker.nextNode()) {
			const t = walker.currentNode as Text;
			const el = t.parentElement!;
			if (!t.data.trim() || !el.checkVisibility() || el.closest('.tn-o')) continue;
			const nen = nenCua(el);
			const chu = tron(doc(getComputedStyle(el).color), nen);
			const [a, b] = [L(chu), L(nen)].sort((p, q) => q - p);
			const tile = (a + 0.05) / (b + 0.05);
			if (tile < thap.tile) thap = { tile, chu: t.data.trim() };
		}
		return thap;
	});
}

for (const cheDo of ['light', 'dark'] as const) {
	test(`desktop ${cheDo}: thẻ sidebar là kính mờ, mọi chữ trong thẻ >= 4,5:1`, async ({ page, isMobile }) => {
		test.skip(!!isMobile);
		await page.addInitScript((m) => localStorage.setItem('starlight-theme', m), cheDo);
		await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
		const the = page.locator('.sidebar-content');
		expect(await the.evaluate((e) => getComputedStyle(e, '::before').backdropFilter)).toContain('blur');
		const nen = await the.evaluate((e) => getComputedStyle(e, '::before').backgroundColor);
		expect(nen).toMatch(/^rgba\(.*, 0\.\d+\)$/);
		// nút ‹ không bị thẻ cắt: điểm giữa nửa ngoài mép thẻ vẫn trúng nút
		const nut = (await page.locator('.nut-thu-gon').boundingBox())!;
		const trung = await page.evaluate(([x, y]) => !!document.elementFromPoint(x, y)?.closest('.nut-thu-gon'), [nut.x + nut.width * 0.8, nut.y + nut.height / 2]);
		expect(trung).toBe(true);
		const thap = await tuongPhanThapNhat(page);
		expect(thap.tile, thap.chu).toBeGreaterThanOrEqual(4.5);
	});
}

test('mobile: sidebar trong menu ☰ nền đặc, không kính mờ, chữ >= 4,5:1', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	await page.locator('button.sl-menu-button').tap();
	const the = page.locator('.sidebar-content');
	await expect(the).toBeVisible();
	expect(await the.evaluate((e) => getComputedStyle(e).backdropFilter)).toBe('none');
	expect(await the.evaluate((e) => getComputedStyle(e, '::before').backdropFilter)).toBe('none');
	expect(await page.locator('.sidebar-pane').evaluate((e) => getComputedStyle(e).backgroundColor)).toBe('rgb(251, 248, 241)');
	const thap = await tuongPhanThapNhat(page);
	expect(thap.tile, thap.chu).toBeGreaterThanOrEqual(4.5);
});
