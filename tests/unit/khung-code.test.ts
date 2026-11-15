import { describe, it, expect } from 'vitest';
import { soOutput } from '../../src/lib/khung-code/so-output';
import { giaiThichLoi, docDong } from '../../src/lib/khung-code/loi';

describe('so khối Output', () => {
	it('khớp khi giống hệt', () => {
		const kq = soOutput('a\nb', 'a\nb');
		expect(kq.khop).toBe(true);
		expect(kq.lech).toEqual([]);
	});
	it('bỏ qua khoảng trắng cuối dòng và cuối khối', () => {
		expect(soOutput('a  \nb\n\n', 'a\nb').khop).toBe(true);
	});
	it('số thực dung sai 1e-6', () => {
		expect(soOutput('0.30000000000000004', '0.3').khop).toBe(true);
		expect(soOutput('1.0000001', '1.0').khop).toBe(true);
		expect(soOutput('1.001', '1.0').khop).toBe(false);
	});
	it('báo đúng dòng lệch', () => {
		const kq = soOutput('a\nX\nc', 'a\nY\nc');
		expect(kq.khop).toBe(false);
		expect(kq.lech).toHaveLength(1);
		expect(kq.lech[0]).toMatchObject({ dong: 2, mong: 'Y', ra: 'X' });
		expect(kq.khopDong).toBe(2);
	});
	it('khác số dòng vẫn so từng dòng', () => {
		expect(soOutput('a\nb', 'a').khop).toBe(false);
	});
});

describe('giải thích lỗi Python', () => {
	it('đọc số dòng từ traceback, lấy khung gần cuối', () => {
		const tb = 'Traceback (most recent call last):\n  File "<exec>", line 3, in <module>\n  File "<exec>", line 7, in f\nZeroDivisionError: division by zero';
		expect(docDong(tb)).toBe(7);
	});
	it('ZeroDivisionError', () => {
		const g = giaiThichLoi('Traceback...\n  File "<exec>", line 2, in <module>\nZeroDivisionError: division by zero');
		expect(g.loai).toBe('ZeroDivisionError');
		expect(g.dong).toBe(2);
		expect(g.giaiThich).toContain('Chia cho 0');
	});
	it('NameError nêu tên biến', () => {
		const g = giaiThichLoi("NameError: name 'x' is not defined");
		expect(g.loai).toBe('NameError');
		expect(g.giaiThich).toContain('`x`');
	});
	it('ModuleNotFoundError nêu tên gói', () => {
		const g = giaiThichLoi("ModuleNotFoundError: No module named 'torch'");
		expect(g.loai).toBe('ModuleNotFoundError');
		expect(g.giaiThich).toContain('torch');
	});
	it('lỗi lạ vẫn có lời giải thích', () => {
		const g = giaiThichLoi('SomethingWeird: abc');
		expect(g.loai).toBe('Lỗi');
		expect(g.giaiThich).toContain('SomethingWeird');
	});
});
