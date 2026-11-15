import { describe, it, expect } from 'vitest';
import { chonCauHoi, phanTramCau, tongHop, type CauHoi, type DeThi } from '../../src/lib/de-thi-logic';

function deGia(chuong: number): DeThi {
	const tn: CauHoi[] = Array.from({ length: 12 }, (_, i) => ({
		loai: 'trac-nghiem',
		id: `tn${i}`,
		khai_niem: ['k1'],
		muc: i < 6 ? 'de' : 'kho',
		diem: 1,
		de: `câu ${i}`,
		lua_chon: ['a', 'b'],
		dap_an: 0,
		giai_thich: '',
	}));
	const tl: CauHoi[] = Array.from({ length: 3 }, (_, i) => ({
		loai: 'tu-luan',
		id: `tl${i}`,
		khai_niem: ['k2'],
		muc: 'vua',
		diem: 10,
		de: 'tự luận',
		rubric: [{ y: 'ý', diem: 10 }],
		tra_loi_mau: '',
	}));
	const code: CauHoi = { loai: 'code', id: 'c1', khai_niem: ['k1'], muc: 'vua', diem: 3, de: 'code', khung: '', kiem_tra: '', loi_giai: '' };
	const cs: CauHoi = {
		loai: 'case',
		id: 'case1',
		khai_niem: ['k1', 'k2'],
		muc: 'kho',
		diem: 10,
		de: '',
		boi_canh: 'bối cảnh',
		nhiem_vu: [{ loai: 'code', de: 'a', diem: 10, kiem_tra: '' }],
		dap_an_mau: '',
	};
	return { chuong, ten: `Ch${chuong}`, khai_niem: [{ id: 'k1', ten: 'K1', trang: '/a' }, { id: 'k2', ten: 'K2', trang: '/b' }], cau_hoi: [...tn, ...tl, code, cs] };
}

describe('chọn câu', () => {
	it('đề chương lấy đủ 10 TN + 2 TL + 1 code + 1 case', () => {
		const kq = chonCauHoi([deGia(0)], { phamVi: [0], kieu: 'chuong', muc: 'tron', daGap: [], seed: 1 });
		expect(kq.filter((c) => c.cau.loai === 'trac-nghiem')).toHaveLength(10);
		expect(kq.filter((c) => c.cau.loai === 'tu-luan')).toHaveLength(2);
		expect(kq.filter((c) => c.cau.loai === 'code')).toHaveLength(1);
		expect(kq.filter((c) => c.cau.loai === 'case')).toHaveLength(1);
	});
	it('đề nhanh không có code và case', () => {
		const kq = chonCauHoi([deGia(0)], { phamVi: [0], kieu: 'nhanh', muc: 'tron', daGap: [], seed: 2 });
		expect(kq).toHaveLength(12);
		expect(kq.some((c) => c.cau.loai === 'code' || c.cau.loai === 'case')).toBe(false);
	});
	it('ưu tiên câu chưa gặp', () => {
		const daGap = Array.from({ length: 12 }, (_, i) => `ch0-tn${i}`);
		const kq = chonCauHoi([deGia(0)], { phamVi: [0], kieu: 'nhanh', muc: 'tron', daGap, seed: 3 });
		const tn = kq.filter((c) => c.cau.loai === 'trac-nghiem');
		// Không còn câu TN chưa gặp: vẫn trả đủ nhưng tất cả đã gặp.
		expect(tn).toHaveLength(10);
		expect(tn.every((c) => daGap.includes(c.khoa))).toBe(true);
	});
	it('mức dễ vẫn lấp từ chương khác nếu thiếu', () => {
		const a = deGia(0);
		const b = deGia(1);
		const kq = chonCauHoi([a, b], { phamVi: [0], kieu: 'nhanh', muc: 'de', daGap: [], seed: 4 });
		expect(kq.filter((c) => c.cau.loai === 'trac-nghiem')).toHaveLength(10);
		expect(new Set(kq.map((c) => c.chuong))).toEqual(new Set([0, 1]));
	});
});

describe('phần trăm từng câu', () => {
	const tn: CauHoi = { loai: 'trac-nghiem', id: 'x', de: '', lua_chon: ['a', 'b'], dap_an: 1, giai_thich: '' };
	it('trắc nghiệm đúng/sai', () => {
		expect(phanTramCau(tn, { chon: 1 })).toBe(1);
		expect(phanTramCau(tn, { chon: 0 })).toBe(0);
		expect(phanTramCau(tn, {})).toBe(0);
	});
	it('tự luận quy về 0..1', () => {
		expect(phanTramCau({ loai: 'tu-luan', id: 't', de: '', rubric: [] }, { diem: 7.5 })).toBe(0.75);
		expect(phanTramCau({ loai: 'tu-luan', id: 't', de: '', rubric: [] }, { diem: 12 })).toBe(1);
	});
	it('code đạt/không đạt', () => {
		const c: CauHoi = { loai: 'code', id: 'c', de: '', khung: '', kiem_tra: '', loi_giai: '' };
		expect(phanTramCau(c, { dat: true })).toBe(1);
		expect(phanTramCau(c, { dat: false })).toBe(0);
	});
	it('case chia theo điểm từng nhiệm vụ', () => {
		const c: CauHoi = {
			loai: 'case',
			id: 'cs',
			de: '',
			boi_canh: '',
			dap_an_mau: '',
			nhiem_vu: [
				{ loai: 'code', de: '', diem: 5, kiem_tra: '' },
				{ loai: 'tu-luan', de: '', diem: 5, rubric: [] },
			],
		};
		expect(phanTramCau(c, { nhiemVu: [{ dat: true }, { diem: 5 }] })).toBe(0.75);
	});
});

describe('tổng hợp điểm và bản đồ', () => {
	it('tính đúng thang 10 theo trọng số', () => {
		const d = deGia(0);
		const [tn, tl, code, cs] = [d.cau_hoi[0], d.cau_hoi[12], d.cau_hoi[15], d.cau_hoi[16]];
		const ds = [
			{ cauThi: { khoa: 'a', chuong: 0, tenChuong: 'Ch0', cau: tn }, traLoi: { chon: 0 } },
			{ cauThi: { khoa: 'b', chuong: 0, tenChuong: 'Ch0', cau: tl }, traLoi: { diem: 5, daCham: true } },
			{ cauThi: { khoa: 'c', chuong: 0, tenChuong: 'Ch0', cau: code }, traLoi: { dat: true } },
			{
				cauThi: { khoa: 'd', chuong: 0, tenChuong: 'Ch0', cau: cs },
				traLoi: { nhiemVu: [{ dat: true }] },
			},
		];
		const kq = tongHop(ds, [d]);
		// 1 + 4*0.5 + 3 + 10 = 16 trên 18 -> 8.9
		expect(kq.diem).toBeCloseTo(8.9, 1);
		expect(kq.banDo.length).toBeGreaterThan(0);
		expect(kq.banDo.every((x) => x.phanTram >= 0 && x.phanTram <= 100)).toBe(true);
	});
});
