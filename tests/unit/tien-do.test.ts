import { describe, it, expect } from 'vitest';
import { taoTrong, ghiLuotDoc, chuoiNgay, phanTram, docTuStorage, luuVaoStorage, ngayDiaPhuong } from '../../src/lib/tien-do';

const ba = { daDoc: {}, ngayHoc: ['2026-10-25', '2026-10-26', '2026-10-27'] };

describe('chuoiNgay', () => {
	it('đếm chuỗi kết thúc hôm nay hoặc hôm qua, 0 nếu đứt', () => {
		expect(chuoiNgay(ba, '2026-10-27')).toBe(3);
		expect(chuoiNgay(ba, '2026-10-28')).toBe(3);
		expect(chuoiNgay(ba, '2026-10-29')).toBe(0);
	});
	it('qua tháng', () => {
		expect(chuoiNgay({ daDoc: {}, ngayHoc: ['2026-10-31', '2026-11-01'] }, '2026-11-01')).toBe(2);
	});
	it('rỗng thì 0', () => expect(chuoiNgay(taoTrong(), '2026-10-27')).toBe(0));
});

describe('ghiLuotDoc', () => {
	it('hai lần cùng ngày chỉ một ngày học, không sửa gốc', () => {
		const g = taoTrong();
		const a = ghiLuotDoc(g, 'a/b', '2026-10-27');
		const b = ghiLuotDoc(a, 'a/c', '2026-10-27');
		expect(b.ngayHoc.length).toBe(1);
		expect(g).toEqual({ daDoc: {}, ngayHoc: [] });
		expect(a.daDoc).toEqual({ 'a/b': '2026-10-27' });
	});
});

describe('phanTram', () => {
	const td = { daDoc: { a: '2026-10-27', x: '2026-10-27' }, ngayHoc: ['2026-10-27'] };
	it('1/3 -> 33', () => expect(phanTram(td, ['a', 'b', 'c'])).toBe(33));
	it('slug ngoài danh sách không tính', () => expect(phanTram({ daDoc: { x: '2026-10-27' }, ngayHoc: [] }, ['a'])).toBe(0));
	it('danh sách rỗng -> 0', () => expect(phanTram(td, [])).toBe(0));
});

describe('storage', () => {
	it('JSON hỏng, lỗi, undefined -> trống', () => {
		expect(docTuStorage({ getItem: () => '{hỏng' })).toEqual(taoTrong());
		expect(docTuStorage({ getItem: () => { throw new Error('x'); } })).toEqual(taoTrong());
		expect(docTuStorage(undefined)).toEqual(taoTrong());
	});
	it('đọc lại dữ liệu đã lưu', () => {
		let v = '';
		luuVaoStorage({ setItem: (_k, x) => { v = x; } }, ba);
		expect(docTuStorage({ getItem: () => v })).toEqual(ba);
	});
	it('setItem ném lỗi không văng', () => {
		expect(() => luuVaoStorage({ setItem: () => { throw new Error('QuotaExceeded'); } }, taoTrong())).not.toThrow();
	});
});

it('ngayDiaPhuong theo giờ máy', () => expect(ngayDiaPhuong(new Date(2026, 9, 5, 23, 59))).toBe('2026-10-05'));
