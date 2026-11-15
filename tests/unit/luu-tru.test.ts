import { describe, it, expect } from 'vitest';
import { tronTienDo, tronMang, tronDuLieu, docTatCa, ghiTatCa, KHOA_LUU } from '../../src/lib/luu-tru';

function khoGia(): Storage {
	const m = new Map<string, string>();
	return {
		get length() {
			return m.size;
		},
		clear: () => m.clear(),
		getItem: (k: string) => m.get(k) ?? null,
		key: (i: number) => [...m.keys()][i] ?? null,
		removeItem: (k: string) => void m.delete(k),
		setItem: (k: string, v: string) => void m.set(k, v),
	} as Storage;
}

describe('gộp dữ liệu học', () => {
	it('hợp trang đã đọc và ngày học, không trùng', () => {
		const a = { daDoc: { 'a/1': '2026-11-01' }, ngayHoc: ['2026-11-01', '2026-11-02'] };
		const b = { daDoc: { 'a/2': '2026-11-03', 'a/1': '2026-11-04' }, ngayHoc: ['2026-11-02', '2026-11-03'] };
		const kq = tronTienDo(a, b) as { daDoc: Record<string, string>; ngayHoc: string[] };
		expect(Object.keys(kq.daDoc).sort()).toEqual(['a/1', 'a/2']);
		expect(kq.daDoc['a/1']).toBe('2026-11-04');
		expect(kq.ngayHoc).toEqual(['2026-11-01', '2026-11-02', '2026-11-03']);
	});
	it('gộp mảng kết quả theo id, bản sau thắng', () => {
		const kq = tronMang(
			[{ id: 'x', diem: 5 }, { id: 'y', diem: 6 }],
			[{ id: 'x', diem: 8 }, { id: 'z', diem: 7 }],
		) as { id: string; diem: number }[];
		expect(kq).toHaveLength(3);
		expect(kq.find((x) => x.id === 'x')?.diem).toBe(8);
	});
	it('tronDuLieu giữ khóa hai bên và gộp đúng tiến độ', () => {
		const kq = tronDuLieu(
			{ 'air-tien-do-v1': { daDoc: { a: '1' }, ngayHoc: ['1'] }, 'air-bai-thi-v1': [{ id: 'b1', diem: 6 }] },
			{ 'air-tien-do-v1': { daDoc: { b: '2' }, ngayHoc: ['2'] }, 'air-thuat-toan-v1': { giai: ['bai-1'] } },
		);
		expect(kq['air-thuat-toan-v1']).toEqual({ giai: ['bai-1'] });
		expect((kq['air-tien-do-v1'] as { daDoc: Record<string, string> }).daDoc).toEqual({ a: '1', b: '2' });
		expect((kq['air-bai-thi-v1'] as unknown[]).length).toBe(1);
	});
});

describe('đọc ghi localStorage', () => {
	it('chỉ đọc các khóa của học tập, bỏ JSON hỏng', () => {
		const s = khoGia();
		s.setItem('air-tien-do-v1', JSON.stringify({ daDoc: {}, ngayHoc: [] }));
		s.setItem('air-bai-thi-v1', '{hỏng');
		s.setItem('khac', '1');
		const d = docTatCa(s);
		expect(Object.keys(d)).toEqual(['air-tien-do-v1']);
	});
	it('ghi đúng các khóa có trong dữ liệu', () => {
		const s = khoGia();
		ghiTatCa({ 'air-tien-do-v1': { daDoc: {}, ngayHoc: [] }, 'khong-thuoc': 1 }, s);
		expect(s.getItem('air-tien-do-v1')).toContain('daDoc');
		expect(s.getItem('khong-thuoc')).toBeNull();
		expect(KHOA_LUU).toContain('air-tien-do-v1');
	});
});
