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
