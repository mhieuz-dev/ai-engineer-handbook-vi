import { describe, it, expect } from 'vitest';
import { CHUONG, PHAN, chuongDaXuatBan, timChuongTheoSlugTrang, cauHinhSidebar } from '../../src/data/chuong';

describe('danh mục chương', () => {
	it('so duy nhất và liên tục 0..64', () => {
		expect(CHUONG.map((c) => c.so)).toEqual(Array.from({ length: 65 }, (_, i) => i));
	});
	it('slug duy nhất và đúng dạng', () => {
		const slugs = CHUONG.map((c) => c.slug);
		expect(new Set(slugs).size).toBe(slugs.length);
		for (const s of slugs) expect(s).toMatch(/^ai-engineer\/ch\d{2}-[a-z0-9-]+$/);
	});
	it('slug mang đúng số chương', () => {
		for (const c of CHUONG) expect(c.slug).toContain(`/ch${String(c.so).padStart(2, '0')}-`);
	});
	it('mọi phan tồn tại trong PHAN', () => {
		const ids = new Set(PHAN.map((p) => p.id));
		for (const c of CHUONG) expect(ids.has(c.phan)).toBe(true);
	});
	it('chỉ chương 10 đã xuất bản', () => {
		expect(chuongDaXuatBan().map((c) => c.so)).toEqual([10]);
	});
	it('tìm chương theo slug trang', () => {
		expect(timChuongTheoSlugTrang('ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan')?.so).toBe(10);
		expect(timChuongTheoSlugTrang('gioi-thieu')).toBeUndefined();
	});
	it('cấu hình sidebar chỉ gồm chương đã xong', () => {
		const cfg = cauHinhSidebar();
		expect(cfg).toHaveLength(1);
		const phan = cfg[0].items as any[];
		expect(phan).toHaveLength(1);
		expect(phan[0].label).toBe('Phần II. Machine Learning cổ điển');
		expect(phan[0].items[0]).toEqual({
			label: '10. Hồi quy tuyến tính',
			items: [{ autogenerate: { directory: 'ai-engineer/ch10-hoi-quy-tuyen-tinh' } }],
		});
	});
});
