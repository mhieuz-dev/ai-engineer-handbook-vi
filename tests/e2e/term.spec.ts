import { test, expect, type Page } from '@playwright/test';

/** Màu đã tính của một token CSS, dạng rgb(...) để so với màu của phần tử. */
const mauToken = (page: Page, ten: string) =>
	page.evaluate((t) => {
		const s = document.createElement('span');
		s.style.color = `var(${t})`;
		document.body.append(s);
		const c = getComputedStyle(s).color;
		s.remove();
		return c;
	}, ten);

/** Tỉ lệ tương phản WCAG giữa hai màu rgb(...). */
function tuongPhan(a: string, b: string) {
	const L = (s: string) => {
		const [r, g, bl] = s.match(/[\d.]+/g)!.slice(0, 3).map((v) => {
			const c = Number(v) / 255;
			return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
		});
		return 0.2126 * r + 0.7152 * g + 0.0722 * bl;
	};
	const [x, y] = [L(a), L(b)].sort((p, q) => q - p);
	return (x + 0.05) / (y + 0.05);
}
const datCheDo = (page: Page, cheDo: 'light' | 'dark') => page.evaluate((m) => (document.documentElement.dataset.theme = m), cheDo);

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

test('tên tiếng Anh trong trang Thuật ngữ có màu nhấn', async ({ page }) => {
	await page.goto('/thuat-ngu/');
	const en = page.locator('#dao-ham .en');
	await expect(en).toHaveText('derivative');
	await expect(en).toHaveCSS('color', await mauToken(page, '--acc-chu'));
});


test('tên tiếng Anh hiện ngay sau chữ tiếng Việt, nghiêng, màu nhấn, lang="en"', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	const wrap = (ten: RegExp) => page.locator('.term-wrap', { has: page.locator('.nhan', { hasText: ten }) });
	const en = wrap(/· ĐẠO HÀM$/).first().locator(':scope > .term-en');
	await expect(en).toHaveText('(derivative)');
	await expect(en).toHaveAttribute('lang', 'en');
	await expect(en.locator('i')).toHaveText('derivative');
	await expect(en.locator('i')).toHaveCSS('color', await mauToken(page, '--acc-chu'));
	await expect(en.locator('i')).toHaveCSS('font-style', 'italic');
	await expect(en.locator('.ngoac').first()).toHaveCSS('font-style', 'normal');
	await expect(en.locator('.ngoac').first()).toHaveCSS('color', await mauToken(page, '--mut'));
	// Nằm ngoài chữ có gạch chấm, nên không bị gạch chân.
	await expect(wrap(/· ĐẠO HÀM$/).first().locator('.term')).toHaveText('đạo hàm');
	// Thuật ngữ vốn dùng tiếng Anh thì không lặp lại.
	for (const ten of [/· LEARNING RATE$/, /· GRADIENT DESCENT$/]) {
		await expect(wrap(ten).first().locator(':scope > .term-en'), String(ten)).toHaveCount(0);
	}
	await expect(wrap(/· LEARNING RATE$/).first().locator('.term')).toHaveText('learning rate');
});

test('en={false} tắt tên tiếng Anh; trang in vẫn có tên tiếng Anh', async ({ page }) => {
	await page.goto(URL);
	const wraps = page.locator('.term-wrap', { has: page.locator('.nhan', { hasText: /· ĐẠO HÀM$/ }) });
	await expect(wraps).toHaveCount(2);
	await expect(wraps.nth(0).locator(':scope > .term-en')).toHaveCount(1);
	await expect(wraps.nth(1).locator(':scope > .term-en')).toHaveCount(0);
	await page.goto('/in/ai-engineer/ch10-hoi-quy-tuyen-tinh/');
	await page.emulateMedia({ media: 'print' });
	await expect(page.locator('.term-en', { hasText: '(derivative)' }).first()).toBeVisible();
});

test('tên tiếng Anh ghi tay (<En>) cùng kiểu với tên tiếng Anh tự hiện của Term', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/05-doc-ket-qua/');
	const tay = page.locator('.tieng-anh:not(.term-en)', { hasText: 'loss curve' });
	const tu = page.locator('.term-en').first();
	await expect(tay).toHaveAttribute('lang', 'en');
	await expect(tay).toHaveText('(loss curve)');
	for (const thuocTinh of ['color', 'font-style', 'font-size']) {
		const lay = (l: typeof tay) => l.locator('i').evaluate((el, t) => getComputedStyle(el).getPropertyValue(t), thuocTinh);
		expect(await lay(tay), thuocTinh).toBe(await lay(tu));
	}
});

for (const cheDo of ['light', 'dark'] as const) {
	test(`tên tiếng Anh đủ tương phản (>= 4,5:1) ở chế độ ${cheDo}`, async ({ page }) => {
		await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
		await datCheDo(page, cheDo);
		const chu = await page.locator('.term-en i').first().evaluate((el) => getComputedStyle(el).color);
		expect(chu).toBe(await mauToken(page, '--acc-chu'));
		expect(tuongPhan(chu, await mauToken(page, '--bg'))).toBeGreaterThanOrEqual(4.5);
		await page.goto('/thuat-ngu/');
		await datCheDo(page, cheDo);
		const [mau, nen] = await page.locator('#dao-ham .en').evaluate((el) => [getComputedStyle(el).color, getComputedStyle(el).backgroundColor]);
		expect(tuongPhan(mau, nen)).toBeGreaterThanOrEqual(4.5);
	});
}

test('nút × đóng nhắc nhanh (chuột hoặc chạm), focus quay về chữ, bàn phím tới được', async ({ page }, info) => {
	const mobile = info.project.name === 'mobile';
	await page.goto(URL);
	const wrap = page.locator('.term-wrap').first();
	const term = wrap.locator('.term');
	const tip = wrap.locator('.tip');
	const dong = tip.getByRole('button', { name: 'Đóng' });
	await term.evaluate((el) => el.scrollIntoView({ block: 'center' }));
	if (mobile) await term.tap();
	else await term.hover();
	await expect(tip).toBeVisible();
	await expect(dong).toBeVisible();
	// nút × ở góc phải trên của khung
	const hDong = (await dong.boundingBox())!;
	const hTip = (await tip.boundingBox())!;
	expect(hDong.x + hDong.width).toBeGreaterThan(hTip.x + hTip.width - 16);
	expect(hDong.y).toBeLessThan(hTip.y + 16);
	if (mobile) await dong.tap();
	else await dong.click();
	await expect(tip).toBeHidden();
	await expect(term).toHaveAttribute('aria-expanded', 'false');
	await expect(term).toBeFocused();
	// mở lại được sau khi đóng
	if (mobile) await term.tap();
	else await page.keyboard.press('Enter');
	await expect(tip).toBeVisible();
	// bàn phím: Tab qua link Học kỹ tới ×, Enter đóng
	await term.focus();
	await page.keyboard.press('Tab');
	await page.keyboard.press('Tab');
	await expect(dong).toBeFocused();
	await page.keyboard.press('Enter');
	await expect(tip).toBeHidden();
	await expect(term).toBeFocused();
});
