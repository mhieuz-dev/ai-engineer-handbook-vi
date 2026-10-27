import { test, expect } from '@playwright/test';

const C10 = '/ai-engineer/ch10-hoi-quy-tuyen-tinh';
const TRANG = ['01-truc-giac', '02-toan', '03-tinh-tay', '04-code', '05-doc-ket-qua', '06-bai-tap'];

test('6 trang chương 10 tải được, có h1, không lỗi công thức', async ({ page }) => {
	for (const t of TRANG) {
		const res = await page.goto(`${C10}/${t}/`);
		expect(res?.status(), t).toBe(200);
		await expect(page.locator('h1').first(), t).toBeVisible();
		await expect(page.locator('.katex-error'), t).toHaveCount(0);
	}
});

test('trang 05 có 4 hình kết quả tải được, mỗi hình có khung đọc biểu đồ', async ({ page }) => {
	await page.goto(`${C10}/05-doc-ket-qua/`);
	const hinh = page.locator('figure img');
	await expect(hinh).toHaveCount(4);
	for (let i = 0; i < 4; i++) {
		const img = hinh.nth(i);
		await img.scrollIntoViewIfNeeded();
		await expect.poll(() => img.evaluate((el: HTMLImageElement) => el.complete && el.naturalWidth), { message: `hình ${i + 1}` }).toBeGreaterThan(0);
	}
	await expect(page.locator('figure figcaption')).toHaveText([/^Hình 10\.1\./, /^Hình 10\.2\./, /^Hình 10\.3\./, /^Hình 10\.4\./]);
	await expect(page.locator('.khung-doc-bieu-do')).toHaveCount(4);
});

test('mobile 375px: công thức và bảng không làm tràn trang, kể cả khi mở Đào sâu và đáp án', async ({ page, isMobile }) => {
	test.skip(!isMobile);
	for (const t of TRANG) {
		await page.goto(`${C10}/${t}/`);
		expect(await page.evaluate(() => document.documentElement.scrollWidth), t).toBeLessThanOrEqual(375);
		await page.evaluate(() => document.querySelectorAll('.sl-markdown-content details').forEach((d) => ((d as HTMLDetailsElement).open = true)));
		expect(await page.evaluate(() => document.documentElement.scrollWidth), `${t} (mở hết)`).toBeLessThanOrEqual(375);
	}
});

test('trang 02: khung Đào sâu về ngưỡng 0,12 đóng sẵn, có thanh trượt learning rate', async ({ page }) => {
	await page.goto(`${C10}/02-toan/`);
	const d = page.locator('details.khung-dao-sau', { hasText: 'vì sao ngưỡng là 0,12' });
	await expect(d).toHaveCount(1);
	await expect(d).not.toHaveAttribute('open', /.*/);
	await expect(page.locator('[data-tn-lr] input[type=range]')).toHaveCount(1);
});

test('trang 04: output in trong bài khớp notebook, nút Colab đúng notebook', async ({ page }) => {
	await page.goto(`${C10}/04-code/`);
	await expect(page.getByText('Bước 200 | w = 1.5993 | b = 0.5019 | MSE = 0.050001')).toBeVisible();
	// Dòng bước 2 là đáp án Bài tập 10.2, chỉ được in ở trang 06.
	await expect(page.locator('main')).not.toContainText('w = 1.5437');
	await expect(page.getByRole('link', { name: /Mở trong Colab/ }).first()).toHaveAttribute(
		'href',
		/notebooks\/ch10_hoi_quy_tuyen_tinh\.ipynb$/,
	);
});

test('chương có ít nhất 2 câu Tự kiểm tra; trang 06 có 3 bài tập và câu hỏi phỏng vấn', async ({ page }) => {
	let soCau = 0;
	for (const t of TRANG) {
		await page.goto(`${C10}/${t}/`);
		soCau += await page.locator('[data-tkt]').count();
	}
	expect(soCau).toBeGreaterThanOrEqual(2);
	await page.goto(`${C10}/06-bai-tap/`);
	await expect(page.locator('.bai-tap')).toHaveCount(3);
	await expect(page.locator('.bai-tap-dap-an')).toHaveCount(3);
	await expect(page.locator('.khung-phong-van')).toHaveCount(1);
	// Mỗi câu phỏng vấn có bản tiếng Anh in nghiêng.
	await expect(page.locator('.khung-phong-van p[lang="en"] em')).toHaveCount(4);
	await expect(page.locator('.khung-phong-van')).toContainText('thường bằng tiếng Anh');
});

test('tìm kiếm "hoi quy" (không dấu) ra trang Hồi quy tuyến tính', async ({ page }) => {
	await page.goto('/');
	await page.locator('button[data-open-modal]').first().click();
	const o = page.locator('#starlight__search input[type=search], #starlight__search .pagefind-ui__search-input').first();
	await expect(o).toBeVisible();
	await o.fill('hoi quy');
	const ketQua = page.locator('#starlight__search .pagefind-ui__result');
	await expect(ketQua.first()).toBeVisible({ timeout: 15_000 });
	await expect(ketQua.filter({ hasText: /hồi quy tuyến tính/i }).first()).toBeVisible();
	await expect(ketQua.locator(`a[href*="${C10}/"]`).first()).toBeVisible();
	// Pagefind còn khớp mờ theo từng chữ cái, nên kiểm thêm: chữ được tô đậm phải là "hồi" có dấu,
	// tức "hoi" đã khớp với "hồi" nhờ bỏ dấu, không phải khớp mờ ngẫu nhiên.
	await expect(ketQua.locator('mark', { hasText: /^hồi$/i }).first()).toBeVisible();
});

test('trang Thuật ngữ: "Xuất hiện ở" của Đạo hàm trỏ tới trang chương 10', async ({ page }) => {
	await page.goto('/thuat-ngu/');
	const muc = page.locator('#dao-ham');
	await expect(muc.locator(`.xuat-hien a[href^="${C10}/"]`).first()).toBeVisible();
});
