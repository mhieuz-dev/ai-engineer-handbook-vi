import { test, expect, type Page } from '@playwright/test';

async function moSidebar(page: Page) {
	const nut = page.locator('button.sl-menu-button');
	if (await nut.isVisible()) await nut.click();
}

test('lưới không còn lệch 16px: con thứ hai của lưới có margin-top 0', async ({ page }) => {
	const cap = [
		['/phong-thi/', '.pt-chude-luoi'],
		['/ho-so/', '.hs-tong'],
		['/phong-van/', '.pv-preset'],
		['/toan-thuat-toan/', '.tn-luoi'],
		['/ai-engineer/ch05-dai-so-tuyen-tinh/01-vector/', '.can-biet-truoc'],
	];
	for (const [url, sel] of cap) {
		await page.goto(url);
		await page.locator(sel).first().waitFor();
		const n = await page.locator(`${sel} > *`).count();
		expect(n, `${url} ${sel}`).toBeGreaterThan(1);
		const mt = await page.locator(`${sel} > *`).nth(1).evaluate((e) => getComputedStyle(e).marginTop);
		expect(mt, `${url} ${sel}`).toBe('0px');
	}
});

test('địa chỉ chương thiếu trang con chuyển về trang 01', async ({ page }) => {
	const cap: [string, RegExp, string][] = [
		['/ai-engineer/ch05-dai-so-tuyen-tinh/', /\/01-vector\/$/, 'Vector'],
		['/ai-engineer/ch10-hoi-quy-tuyen-tinh/', /\/01-truc-giac\/$/, 'Bài toán'],
		['/ai-engineer/ch47-llm-hoat-dong/', /\/01-llm-la-gi\/$/, 'LLM'],
	];
	for (const [url, re, chu] of cap) {
		await page.goto(url);
		await expect(page).toHaveURL(re);
		await expect(page.locator('h1').first()).toContainText(chu);
	}
});

test('404 có lối đi tiếp', async ({ page }) => {
	await page.goto('/khong-ton-tai');
	await expect(page.locator('h1')).toContainText('Không tìm thấy');
	await expect(page.locator('.p404-the[href="/"]')).toHaveCount(1);
	await expect(page.locator('.p404-the[href="/lo-trinh/"]')).toHaveCount(1);
	await expect(page.locator('.p404-the[href="/luyen-tap/"]')).toHaveCount(1);
});

test('chưa đọc gì thì sidebar không ghi ngày liên tiếp', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	await moSidebar(page);
	await expect(page.locator('.td-pt')).toHaveText('0%');
	await expect(page.locator('.td-chuoi')).toBeHidden();
});

test('cột phải không còn emoji, hai nhãn cùng cỡ', async ({ page, isMobile }) => {
	test.skip(!!isMobile);
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/');
	const chu = await page.locator('.tai-ve').innerText();
	expect(chu).not.toMatch(/📄|📚|📓/);
	await expect(page.locator('.tai-ve svg')).toHaveCount(3);
	const a = await page.locator('#starlight__on-this-page').evaluate((e) => getComputedStyle(e).fontSize);
	const b = await page.locator('.tai-ve h2').evaluate((e) => getComputedStyle(e).fontSize);
	expect(a).toBe(b);
});

test('Luyện thuật toán: bài tập ở trên, Toán là cốt lõi ở dưới', async ({ page }) => {
	await page.goto('/thuat-toan/');
	const yDe = (await page.locator('.tt-the').first().boundingBox())!.y;
	const yToan = (await page.getByRole('heading', { name: 'Toán là cốt lõi' }).boundingBox())!.y;
	expect(yDe).toBeLessThan(yToan);
});

test('Luyện tập chỉ còn một đoạn mở đầu trong khối', async ({ page }) => {
	await page.goto('/luyen-tap/');
	await expect(page.locator('.lt p.lt-mo')).toHaveCount(1);
});

test('trang chủ: 9 Phần xếp một cột và h1 không lặp tên site', async ({ page }) => {
	await page.goto('/');
	const xs = await page.locator('.the-phan').evaluateAll((els) => [...new Set(els.map((e) => Math.round(e.getBoundingClientRect().x)))]);
	expect(xs.length).toBe(1);
	await expect(page.locator('main h1#_top')).toHaveText('Hiểu tận gốc AI, từ Python đến mô hình ngôn ngữ lớn');
});
