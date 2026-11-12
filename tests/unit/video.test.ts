import { describe, it, expect } from 'vitest';
import { VIDEO, videoCuaChuong } from '../../src/data/video';
import { chuongDaXuatBan } from '../../src/data/chuong';

describe('video từng chương', () => {
	it('mọi chương đã xuất bản đều có ít nhất một video', () => {
		for (const c of chuongDaXuatBan()) expect(videoCuaChuong(c.so).length).toBeGreaterThan(0);
	});
	it('mã video đúng dạng và không trùng', () => {
		const ids = Object.values(VIDEO).flat().map((v) => v.id);
		expect(new Set(ids).size).toBe(ids.length);
		for (const id of ids) expect(id).toMatch(/^[A-Za-z0-9_-]{11}$/);
	});
	it('mỗi video có tiêu đề, kênh và thời lượng', () => {
		for (const v of Object.values(VIDEO).flat()) {
			expect(v.tieuDe.trim().length).toBeGreaterThan(0);
			expect(v.kenh.trim().length).toBeGreaterThan(0);
			expect(v.thoiLuong).toMatch(/^\d+:\d{2}(:\d{2})?$/);
		}
	});
	it('chương không có video trả về mảng rỗng', () => {
		expect(videoCuaChuong(999)).toEqual([]);
	});
});
