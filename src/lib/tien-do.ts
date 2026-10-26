export interface TienDo { daDoc: Record<string, string>; ngayHoc: string[] }
export const KHOA_STORAGE = 'air-tien-do-v1';

export function taoTrong(): TienDo {
	return { daDoc: {}, ngayHoc: [] };
}

export function ngayDiaPhuong(d: Date): string {
	const p = (n: number) => String(n).padStart(2, '0');
	return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

export function ghiLuotDoc(td: TienDo, slugTrang: string, ngay: string): TienDo {
	const ngayHoc = td.ngayHoc.includes(ngay) ? [...td.ngayHoc] : [...td.ngayHoc, ngay].sort();
	return { daDoc: { ...td.daDoc, [slugTrang]: ngay }, ngayHoc };
}

// Ngày kế trước, tính theo lịch (UTC để không dính giờ mùa hè).
function truocMotNgay(ngay: string): string {
	const [y, m, d] = ngay.split('-').map(Number);
	return new Date(Date.UTC(y, m - 1, d - 1)).toISOString().slice(0, 10);
}

export function chuoiNgay(td: TienDo, homNay: string): number {
	const co = new Set(td.ngayHoc);
	let cur = co.has(homNay) ? homNay : truocMotNgay(homNay);
	let n = 0;
	while (co.has(cur)) {
		n++;
		cur = truocMotNgay(cur);
	}
	return n;
}

export function phanTram(td: TienDo, cacSlugTrangDaXuatBan: string[]): number {
	if (cacSlugTrangDaXuatBan.length === 0) return 0;
	const doc = cacSlugTrangDaXuatBan.filter((s) => s in td.daDoc).length;
	return Math.floor((doc * 100) / cacSlugTrangDaXuatBan.length);
}

export function docTuStorage(s: Pick<Storage, 'getItem'> | undefined): TienDo {
	try {
		const raw = s?.getItem(KHOA_STORAGE);
		if (!raw) return taoTrong();
		const o = JSON.parse(raw);
		if (!o || typeof o.daDoc !== 'object' || o.daDoc === null || Array.isArray(o.daDoc) || !Array.isArray(o.ngayHoc)) return taoTrong();
		return { daDoc: o.daDoc, ngayHoc: o.ngayHoc.filter((x: unknown) => typeof x === 'string').sort() };
	} catch {
		return taoTrong();
	}
}

export function luuVaoStorage(s: Pick<Storage, 'setItem'> | undefined, td: TienDo): void {
	try {
		s?.setItem(KHOA_STORAGE, JSON.stringify(td));
	} catch {
		/* đầy bộ nhớ hoặc bị chặn: bỏ qua */
	}
}
