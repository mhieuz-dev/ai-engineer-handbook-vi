import { describe, it, expect } from 'vitest';
import { khuCuaDuongDan, KHU } from '../../src/data/khu';

describe('khu của đường dẫn', () => {
	it('trang chủ, lộ trình và chương thuộc khu Học', () => {
		expect(khuCuaDuongDan('/')).toBe('hoc');
		expect(khuCuaDuongDan('/lo-trinh/')).toBe('hoc');
		expect(khuCuaDuongDan('/ai-engineer/ch10-hoi-quy-tuyen-tinh/02-toan/')).toBe('hoc');
	});

	it('phòng thi, thuật toán, toán, phỏng vấn và hub thuộc khu Luyện tập', () => {
		expect(khuCuaDuongDan('/luyen-tap/')).toBe('luyen');
		expect(khuCuaDuongDan('/phong-thi/?chu-de=ch05')).toBe('luyen');
		expect(khuCuaDuongDan('/thuat-toan/')).toBe('luyen');
		expect(khuCuaDuongDan('/toan-thuat-toan/')).toBe('luyen');
		expect(khuCuaDuongDan('/phong-van/')).toBe('luyen');
	});

	it('thuật ngữ, notebook, giới thiệu, quyền riêng tư thuộc khu Tra cứu', () => {
		expect(khuCuaDuongDan('/thuat-ngu/')).toBe('tra');
		expect(khuCuaDuongDan('/notebook/')).toBe('tra');
		expect(khuCuaDuongDan('/gioi-thieu/')).toBe('tra');
		expect(khuCuaDuongDan('/quyen-rieng-tu/')).toBe('tra');
	});

	it('hồ sơ thuộc khu Hồ sơ', () => {
		expect(khuCuaDuongDan('/ho-so/')).toBe('hoso');
	});

	it('bỏ qua query và hash khi xét khu', () => {
		expect(khuCuaDuongDan('/thuat-ngu/#chu-a')).toBe('tra');
		expect(khuCuaDuongDan('/phong-thi/?de=abc#cau-2')).toBe('luyen');
	});

	it('đường dẫn lạ mặc định về khu Học', () => {
		expect(khuCuaDuongDan('/khong-ton-tai')).toBe('hoc');
	});

	it('mỗi khu có tên, màu và mô tả', () => {
		for (const id of ['hoc', 'luyen', 'tra', 'hoso'] as const) {
			expect(KHU[id].ten.length).toBeGreaterThan(0);
			expect(KHU[id].mau).toMatch(/^var\(--khu-/);
			expect(KHU[id].moTa.length).toBeGreaterThan(0);
		}
	});
});
