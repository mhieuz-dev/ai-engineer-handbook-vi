import { describe, it, expect } from 'vitest';
import { dungCay, type Nut, type NutNhom } from '../../src/lib/sidebar-cay';
import type { Chuong, Nhanh, Phan } from '../../src/data/chuong';

const nhanh: Nhanh[] = [{ id: 'ai-engineer', ten: 'AI Engineer' }];
const phan: Phan[] = [
	{ id: 'p1', nhanh: 'ai-engineer', ten: 'Phần 1' },
	{ id: 'p2', nhanh: 'ai-engineer', ten: 'Phần 2' },
];
const c = (so: number, p: string, trangThai: Chuong['trangThai']): Chuong => ({ so, phan: p, ten: `T${so}`, slug: `ai-engineer/ch0${so}-t`, trangThai });
const chuong = [c(3, 'p1', 'sap-co'), c(1, 'p1', 'sap-co'), c(2, 'p1', 'xong'), c(4, 'p2', 'sap-co')];
const nhomChuong: NutNhom = { type: 'group', label: '2. T2', collapsed: true, entries: [{ type: 'link', label: 'a', href: '/x/', isCurrent: false }] };
const goc: Nut[] = [{ type: 'group', label: 'AI Engineer', collapsed: false, entries: [{ type: 'group', label: 'Phần 1', collapsed: false, entries: [nhomChuong] }] }];

describe('dungCay', () => {
	it('chèn Sắp có theo thứ tự so, giữ nhóm chương thật', () => {
		const [n] = dungCay(goc, nhanh, phan, chuong);
		const p1 = n.entries[0] as NutNhom;
		expect(p1.entries.map((e) => e.label)).toEqual(['1. T1', '2. T2', '3. T3']);
		expect(p1.entries.map((e) => e.type)).toEqual(['sap-co', 'group', 'sap-co']);
		expect(p1.entries[1]).toBe(nhomChuong);
	});
	it('Phần chỉ gồm chương Sắp có vẫn hiện', () => {
		const [n] = dungCay(goc, nhanh, phan, chuong);
		const p2 = n.entries[1] as NutNhom;
		expect(p2.entries).toEqual([{ type: 'sap-co', label: '4. T4' }]);
	});
	it('ném lỗi khi chương xong không có nhóm trong Starlight', () => {
		expect(() => dungCay([], nhanh, phan, chuong)).toThrow(/Chương 2 "T2" đã xuất bản/);
	});
});
