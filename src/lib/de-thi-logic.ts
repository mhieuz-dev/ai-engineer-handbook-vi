/** Logic phòng thi: chọn câu, tính điểm, bản đồ kiến thức, lưu kết quả. Thuần, dễ test. */

export interface KhaiNiem {
	id: string;
	ten: string;
	trang: string;
}

export interface NhiemVu {
	loai: 'code' | 'tu-luan';
	de: string;
	diem: number;
	kiem_tra?: string;
	rubric?: { y: string; diem: number }[];
}

export interface CauHoi {
	loai: 'trac-nghiem' | 'tu-luan' | 'code' | 'case';
	id: string;
	khai_niem?: string[];
	muc?: 'de' | 'vua' | 'kho';
	diem?: number;
	de: string;
	lua_chon?: string[];
	dap_an?: number;
	giai_thich?: string;
	rubric?: { y: string; diem: number }[];
	tra_loi_mau?: string;
	khung?: string;
	kiem_tra?: string;
	loi_giai?: string;
	boi_canh?: string;
	du_lieu?: string[];
	bay?: string[];
	nhiem_vu?: NhiemVu[];
	dap_an_mau?: string;
}

export interface DeThi {
	chuong: number;
	ten: string;
	khai_niem: KhaiNiem[];
	cau_hoi: CauHoi[];
}

export interface CauThi {
	khoa: string;
	chuong: number;
	tenChuong: string;
	cau: CauHoi;
}

export type KieuDe = 'nhanh' | 'chuong' | 'lon';
export type MucDo = 'de' | 'vua' | 'kho' | 'tron';

export interface TuyChon {
	phamVi: number[];
	kieu: KieuDe;
	muc: MucDo;
	daGap: string[];
	seed: number;
}

export interface TraLoiNhiemVu {
	dat?: boolean;
	diem?: number;
	chu?: string;
	daCham?: boolean;
}

export interface TraLoi {
	chon?: number;
	chu?: string;
	dat?: boolean;
	/** Điểm tự luận 0..10. */
	diem?: number;
	nhanXet?: string;
	nhiemVu?: TraLoiNhiemVu[];
}

export interface CauDaTraLoi {
	cauThi: CauThi;
	traLoi: TraLoi;
}

const TRONG_SO: Record<CauHoi['loai'], number> = { 'trac-nghiem': 1, 'tu-luan': 4, code: 3, case: 10 };

export function trongSo(c: CauHoi): number {
	return TRONG_SO[c.loai];
}

function rng(seed: number): () => number {
	let a = seed >>> 0;
	return () => {
		a = (a + 0x6d2b79f5) >>> 0;
		let t = a;
		t = Math.imul(t ^ (t >>> 15), t | 1);
		t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
}

function xao<T>(ds: T[], r: () => number): T[] {
	const a = [...ds];
	for (let i = a.length - 1; i > 0; i--) {
		const j = Math.floor(r() * (i + 1));
		[a[i], a[j]] = [a[j], a[i]];
	}
	return a;
}

const SO_LUONG: Record<KieuDe, [CauHoi['loai'], number][]> = {
	nhanh: [
		['trac-nghiem', 10],
		['tu-luan', 2],
	],
	chuong: [
		['trac-nghiem', 10],
		['tu-luan', 2],
		['code', 1],
		['case', 1],
	],
	lon: [
		['trac-nghiem', 10],
		['case', 2],
	],
};

export function chonCauHoi(de: DeThi[], o: TuyChon): CauThi[] {
	const r = rng(o.seed);
	const trongPhamVi = de.filter((d) => o.phamVi.includes(d.chuong));
	const tatCa = de;
	const daGap = new Set(o.daGap);
	const kho = (ds: DeThi[]) =>
		ds.flatMap((d) =>
			d.cau_hoi
				.filter((c) => o.muc === 'tron' || !c.muc || c.muc === o.muc)
				.map((c) => ({ khoa: `ch${d.chuong}-${c.id}`, chuong: d.chuong, tenChuong: d.ten, cau: c })),
		);
	const sapXep = (ds: CauThi[]) =>
		xao(ds, r).sort((a, b) => Number(daGap.has(a.khoa)) - Number(daGap.has(b.khoa)));

	const kq: CauThi[] = [];
	for (const [loai, so] of SO_LUONG[o.kieu]) {
		let ung = sapXep(kho(trongPhamVi).filter((c) => c.cau.loai === loai));
		if (ung.length < so) {
			const daCo = new Set(ung.map((c) => c.khoa));
			ung = [...ung, ...sapXep(kho(tatCa).filter((c) => c.cau.loai === loai && !daCo.has(c.khoa)))];
		}
		kq.push(...ung.slice(0, so));
	}
	return kq;
}

export function phanTramCau(c: CauHoi, t: TraLoi): number {
	if (c.loai === 'trac-nghiem') return t.chon === c.dap_an ? 1 : 0;
	if (c.loai === 'code') return t.dat ? 1 : 0;
	if (c.loai === 'tu-luan') return Math.max(0, Math.min(10, t.diem ?? 0)) / 10;
	const nv = c.nhiem_vu ?? [];
	const tong = nv.reduce((s, x) => s + x.diem, 0);
	if (!tong) return 0;
	const dat = nv.reduce((s, x, i) => {
		const tl = t.nhiemVu?.[i];
		if (!tl) return s;
		const pt = x.loai === 'code' ? (tl.dat ? 1 : 0) : Math.max(0, Math.min(10, tl.diem ?? 0)) / 10;
		return s + x.diem * pt;
	}, 0);
	return dat / tong;
}

export interface BanDoMuc {
	id: string;
	ten: string;
	trang: string;
	dat: number;
	tong: number;
	phanTram: number;
	muc: 'vung' | 'can-cung-co' | 'chua-nam';
}

export interface KetQua {
	diem: number;
	banDo: BanDoMuc[];
	manh: BanDoMuc[];
	yeu: BanDoMuc[];
}

export function tongHop(ds: CauDaTraLoi[], de: DeThi[]): KetQua {
	const khaiNiem = new Map<string, KhaiNiem>();
	for (const d of de) for (const k of d.khai_niem) khaiNiem.set(k.id, k);

	let tu = 0;
	let mau = 0;
	const diemTheo = new Map<string, { dat: number; tong: number }>();
	for (const { cauThi, traLoi } of ds) {
		const w = trongSo(cauThi.cau);
		const pt = phanTramCau(cauThi.cau, traLoi);
		tu += w * pt;
		mau += w;
		const ids = cauThi.cau.khai_niem ?? [];
		if (!ids.length) continue;
		for (const id of ids) {
			const cu = diemTheo.get(id) ?? { dat: 0, tong: 0 };
			cu.dat += (w * pt) / ids.length;
			cu.tong += w / ids.length;
			diemTheo.set(id, cu);
		}
	}

	const banDo: BanDoMuc[] = [...diemTheo.entries()]
		.map(([id, v]) => {
			const kn = khaiNiem.get(id);
			const phanTram = v.tong ? Math.round((v.dat / v.tong) * 100) : 0;
			return {
				id,
				ten: kn?.ten ?? id,
				trang: kn?.trang ?? '',
				dat: v.dat,
				tong: v.tong,
				phanTram,
				muc: (phanTram >= 80 ? 'vung' : phanTram >= 50 ? 'can-cung-co' : 'chua-nam') as BanDoMuc['muc'],
			};
		})
		.sort((a, b) => b.phanTram - a.phanTram);

	const manh = banDo.filter((x) => x.muc === 'vung').slice(0, 3);
	const yeu = [...banDo].reverse().filter((x) => x.muc !== 'vung').slice(0, 3);
	return { diem: mau ? Math.round((tu / mau) * 100) / 10 : 0, banDo, manh, yeu };
}

export interface KetQuaDaLuu {
	id: string;
	ngay: string;
	kieu: KieuDe;
	phamVi: number[];
	diem: number;
	banDo: BanDoMuc[];
	soCau: number;
}

export const KHOA_KET_QUA = 'air-bai-thi-v1';
export const KHOA_DA_GAP = 'air-da-gap-v1';

export function docDaGap(): string[] {
	try {
		const o = JSON.parse(localStorage.getItem(KHOA_DA_GAP) ?? '[]');
		return Array.isArray(o) ? o.filter((x) => typeof x === 'string') : [];
	} catch {
		return [];
	}
}

export function themDaGap(keys: string[]): void {
	const cu = new Set(docDaGap());
	for (const k of keys) cu.add(k);
	try {
		localStorage.setItem(KHOA_DA_GAP, JSON.stringify([...cu]));
	} catch {
		/* bỏ qua */
	}
}

export function docKetQua(): KetQuaDaLuu[] {
	try {
		const o = JSON.parse(localStorage.getItem(KHOA_KET_QUA) ?? '[]');
		return Array.isArray(o) ? (o as KetQuaDaLuu[]) : [];
	} catch {
		return [];
	}
}

export function luuKetQua(k: KetQuaDaLuu): void {
	const ds = docKetQua();
	ds.unshift(k);
	try {
		localStorage.setItem(KHOA_KET_QUA, JSON.stringify(ds.slice(0, 50)));
	} catch {
		/* bỏ qua */
	}
	window.dispatchEvent(new CustomEvent('du-lieu-doi'));
}
