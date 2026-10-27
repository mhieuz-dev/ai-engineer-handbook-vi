import { test, expect } from '@playwright/test';

const URL = '/kiem-thu/thanh-phan/';

test('khung "Vì sao" có nhãn đúng', async ({ page }) => {
	await page.goto(URL);
	await expect(page.getByText('VÌ SAO LẠI LÀ η = 0,05?')).toBeVisible();
});

test('khung đào sâu đóng sẵn và mở khi bấm', async ({ page }) => {
	await page.goto(URL);
	const d = page.locator('details.khung-dao-sau');
	await expect(d).not.toHaveAttribute('open', /.*/);
	await d.locator('summary').click();
	await expect(d).toHaveAttribute('open', /.*/);
});

test('nút Colab trỏ đúng notebook', async ({ page }) => {
	await page.goto(URL);
	const a = page.getByRole('link', { name: /Mở trong Colab/ });
	await expect(a).toHaveAttribute('href', /notebooks\/ch10_hoi_quy_tuyen_tinh\.ipynb$/);
	await expect(a).toHaveAttribute('target', '_blank');
});

test('đáp án bài tập ẩn đến khi bấm', async ({ page }) => {
	await page.goto(URL);
	const dapAn = page.getByText('Đáp án mẫu: 42.');
	await expect(dapAn).toBeHidden();
	await page.getByText('Xem đáp án').click();
	await expect(dapAn).toBeVisible();
});

test('hình kết quả có chú thích đánh số', async ({ page }) => {
	await page.goto(URL);
	await expect(page.locator('figure figcaption')).toHaveText(/^Hình 10\.1\./);
});

test('nút Colab gọn, kèm đường dẫn notebook cùng hàng', async ({ page }) => {
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/04-code/');
	const nut = page.locator('.colab-nut');
	await expect(nut).toHaveText(/Mở trong Colab/);
	const hop = await nut.boundingBox();
	expect(hop!.height).toBeLessThanOrEqual(32);
	const path = page.getByText('notebooks/ch10_hoi_quy_tuyen_tinh.ipynb', { exact: true });
	await expect(path).toBeVisible();
	const hopP = await path.boundingBox();
	// điện thoại hẹp cho phép xuống dòng; desktop phải cùng hàng
	if ((page.viewportSize()?.width ?? 0) >= 1000) {
		expect(Math.abs(hopP!.y - hop!.y)).toBeLessThanOrEqual(8);
		expect(hopP!.x).toBeGreaterThan(hop!.x + hop!.width - 1);
	}
	expect(await path.evaluate((e) => getComputedStyle(e).fontFamily)).toMatch(/mono/i);
	await page.emulateMedia({ media: 'print' });
	await expect(path).toBeHidden();
	await expect(nut).toBeHidden();
});

const LOAI_KHUNG = ['truc-giac', 'vi-sao', 'loi', 'doc-bieu-do', 'phong-van', 'dao-sau'] as const;

/** Tương phản WCAG giữa chữ và nền của một phần tử; đọc được cả rgb(...) lẫn color(srgb ...) mà color-mix trả về. */
const tuongPhanChuNen = (chu: string, nen: string) => {
	const doc = (s: string) => {
		const m = s.match(/[\d.]+/g)!.map(Number);
		return s.startsWith('color(') ? m.slice(0, 3).map((v) => v * 255) : m.slice(0, 3);
	};
	const L = (c: number[]) => {
		const [r, g, b] = c.map((v) => {
			const x = v / 255;
			return x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
		});
		return 0.2126 * r + 0.7152 * g + 0.0722 * b;
	};
	const [a, b] = [L(doc(chu)), L(doc(nen))].sort((p, q) => q - p);
	return (a + 0.05) / (b + 0.05);
};

test('6 loại khung: viền 1px, bo góc, biểu tượng nét aria-hidden trước tiêu đề in hoa', async ({ page }) => {
	await page.goto(URL);
	for (const loai of LOAI_KHUNG) {
		const khung = page.locator(`.khung-${loai}`).first();
		const kieu = await khung.evaluate((e) => {
			const s = getComputedStyle(e);
			return { bo: parseFloat(s.borderTopRightRadius), vien: s.borderTopWidth, vienPhai: s.borderRightWidth };
		});
		expect(kieu.bo, loai).toBeGreaterThanOrEqual(8);
		expect(kieu.vien, loai).toBe('1px');
		expect(kieu.vienPhai, loai).toBe('1px');
		const icon = khung.locator(':scope > .khung-nhan > svg.khung-icon');
		await expect(icon, loai).toHaveCount(1);
		await expect(icon, loai).toHaveAttribute('aria-hidden', 'true');
		await expect(icon, loai).toBeVisible();
		// biểu tượng đứng trước tiêu đề, cùng hàng
		const hIcon = (await icon.boundingBox())!;
		const hTieuDe = (await khung.locator('.khung-tieu-de').boundingBox())!;
		expect(hIcon.x, loai).toBeLessThan(hTieuDe.x);
		expect(Math.abs(hIcon.y + hIcon.height / 2 - (hTieuDe.y + hTieuDe.height / 2)), loai).toBeLessThanOrEqual(4);
	}
	// đào sâu vẫn là <details> đóng sẵn
	await expect(page.locator('details.khung-dao-sau')).not.toHaveAttribute('open', /.*/);
});

test('viên nhãn chỉ hiện khi tác giả đặt nhan, nằm bên phải hàng tiêu đề', async ({ page }) => {
	await page.goto(URL);
	await expect(page.locator('.khung-tag')).toHaveCount(1);
	const tag = page.locator('.khung-vi-sao .khung-tag');
	await expect(tag).toHaveText('Nhãn mẫu');
	expect(parseFloat(await tag.evaluate((e) => getComputedStyle(e).borderTopLeftRadius))).toBeGreaterThanOrEqual(8);
	const hTag = (await tag.boundingBox())!;
	const hKhung = (await page.locator('.khung-vi-sao').boundingBox())!;
	expect(hTag.x + hTag.width).toBeGreaterThan(hKhung.x + hKhung.width - 40);
	await page.goto('/ai-engineer/ch10-hoi-quy-tuyen-tinh/01-truc-giac/');
	await expect(page.locator('.khung-truc-giac .khung-tag')).toHaveText('Trực giác cốt lõi');
});

for (const cheDo of ['light', 'dark'] as const) {
	test(`tiêu đề và viên nhãn của 6 loại khung đạt >= 4,5:1 trên nền khung (${cheDo})`, async ({ page }) => {
		await page.goto(URL);
		await page.evaluate((m) => (document.documentElement.dataset.theme = m), cheDo);
		for (const loai of LOAI_KHUNG) {
			const khung = page.locator(`.khung-${loai}`).first();
			const nen = await khung.evaluate((e) => getComputedStyle(e).backgroundColor);
			const chu = await khung.locator('.khung-tieu-de').evaluate((e) => getComputedStyle(e).color);
			expect(tuongPhanChuNen(chu, nen), `${loai} ${chu} / ${nen}`).toBeGreaterThanOrEqual(4.5);
		}
		const tag = page.locator('.khung-tag');
		const [chu, nen] = await tag.evaluate((e) => [getComputedStyle(e).color, getComputedStyle(e).backgroundColor]);
		expect(tuongPhanChuNen(chu, nen), `${chu} / ${nen}`).toBeGreaterThanOrEqual(4.5);
	});
}
