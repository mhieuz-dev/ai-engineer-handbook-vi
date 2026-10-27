import { test, expect, type Page } from '@playwright/test';

/** Mở trang ở theme tối rồi chuyển sang chế độ in. */
async function moBanInTuThemeToi(page: Page, url: string) {
	await page.addInitScript(() => localStorage.setItem('starlight-theme', 'dark'));
	await page.emulateMedia({ colorScheme: 'dark' });
	await page.goto(url);
	await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
	await page.emulateMedia({ colorScheme: 'dark', media: 'print' });
}

/** Tương phản thấp nhất giữa chữ và nền (nền trong suốt được trộn với nền cha) của mọi chữ hiện trong các phần tử khớp. */
function tuongPhanThapNhat(page: Page, chon: string) {
	return page.locator(chon).evaluateAll((ds) => {
		const doc = (s: string): number[] => {
			const m = s.match(/[\d.]+/g)!.map(Number);
			if (s.startsWith('color(')) return [m[0] * 255, m[1] * 255, m[2] * 255, m[3] ?? 1];
			return [m[0], m[1], m[2], m[3] ?? 1];
		};
		const tron = (tren: number[], duoi: number[]) => [0, 1, 2].map((i) => tren[i] * tren[3] + duoi[i] * (1 - tren[3])).concat(1);
		const nenCua = (el: Element | null): number[] => {
			if (!el) return [255, 255, 255, 1];
			const c = doc(getComputedStyle(el).backgroundColor);
			return c[3] === 1 ? c : tron(c, nenCua(el.parentElement));
		};
		const L = (c: number[]) => {
			const [r, g, b] = c.slice(0, 3).map((v) => {
				const x = v / 255;
				return x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
			});
			return 0.2126 * r + 0.7152 * g + 0.0722 * b;
		};
		let thap = { tile: 99, chu: '' };
		for (const goc of ds) {
			const walker = document.createTreeWalker(goc, NodeFilter.SHOW_TEXT);
			while (walker.nextNode()) {
				const t = walker.currentNode as Text;
				const el = t.parentElement!;
				// bỏ phần MathML ẩn của KaTeX (chỉ cho trình đọc màn hình)
				if (!t.data.trim() || !el.checkVisibility() || el.closest('.katex-mathml')) continue;
				const nen = nenCua(el);
				const chu = tron(doc(getComputedStyle(el).color), nen);
				const [a, b] = [L(chu), L(nen)].sort((p, q) => q - p);
				const tile = (a + 0.05) / (b + 0.05);
				if (tile < thap.tile) thap = { tile, chu: `${t.data.trim().slice(0, 40)} (${getComputedStyle(el).color} / ${getComputedStyle(el).backgroundColor})` };
			}
		}
		return thap;
	});
}

for (const url of ['/kiem-thu/thanh-phan/', '/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/']) {
	test(`in từ theme tối (${url}): khung và công thức in nền sáng, chữ >= 4,5:1`, async ({ page }) => {
		await moBanInTuThemeToi(page, url);
		const khung = page.locator('aside.khung, details.khung');
		expect(await khung.count()).toBeGreaterThan(0);
		// nền khung phải sáng (độ sáng tương đối > 0,8), không còn nền tối
		const nenToiNhat = await khung.evaluateAll((ds) =>
			Math.min(
				...ds.map((d) => {
					const s = getComputedStyle(d).backgroundColor;
					const m = s.match(/[\d.]+/g)!.map(Number);
					const c = s.startsWith('color(') ? m.slice(0, 3) : m.slice(0, 3).map((v) => v / 255);
					return Math.min(...c);
				}),
			),
		);
		expect(nenToiNhat).toBeGreaterThan(0.85);
		const thap = await tuongPhanThapNhat(page, 'aside.khung, details.khung');
		expect(thap.tile, thap.chu).toBeGreaterThanOrEqual(4.5);
		const congThuc = page.locator('.katex-display');
		if (await congThuc.count()) {
			const nen = await congThuc.evaluateAll((ds) => [...new Set(ds.map((d) => getComputedStyle(d).backgroundColor))]);
			expect(nen).toEqual(['rgb(255, 255, 255)']);
			const thapCT = await tuongPhanThapNhat(page, '.katex-display');
			expect(thapCT.tile, thapCT.chu).toBeGreaterThanOrEqual(4.5);
		}
	});
}

test('in từ theme tối: trang 02 thật sự có công thức và viên số được kiểm', async ({ page }) => {
	await moBanInTuThemeToi(page, '/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	await expect(page.locator('.katex-display .tag', { hasText: '(10.1)' })).toHaveCount(1);
	expect(await page.locator('.katex-display .tag').first().evaluate((e) => getComputedStyle(e).backgroundColor)).toBe('rgb(243, 238, 227)');
});
