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
	it('chương đã xuất bản đều có notebook đặt tên theo số chương', () => {
		for (const c of chuongDaXuatBan()) expect(c.notebook).toMatch(new RegExp(`^ch${String(c.so).padStart(2, '0')}_[a-z0-9_]+\\.ipynb$`));
		expect(CHUONG.filter((c) => c.notebook).every((c) => c.trangThai === 'xong')).toBe(true);
	});
	it('tìm chương theo slug trang', () => {
		expect(timChuongTheoSlugTrang('ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan')?.so).toBe(10);
		expect(timChuongTheoSlugTrang('gioi-thieu')).toBeUndefined();
	});
	it('cấu hình sidebar chỉ gồm chương đã xong, nhóm theo Phần', () => {
		const cfg = cauHinhSidebar();
		expect(cfg).toHaveLength(1);
		const phan = cfg[0].items as any[];
		const daXong = chuongDaXuatBan();
		expect(phan.map((p) => p.label)).toEqual(PHAN.filter((p) => daXong.some((c) => c.phan === p.id)).map((p) => p.ten));
		expect(phan.flatMap((p) => p.items)).toEqual(
			daXong.map((c) => ({ label: `${c.so}. ${c.ten}`, items: [{ autogenerate: { directory: c.slug } }] })),
		);
	});
});
