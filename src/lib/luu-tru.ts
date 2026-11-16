/** Lớp lưu trữ chung: chưa đăng nhập thì localStorage, đã đăng nhập thì đồng bộ Firestore. */
import { docNguoiDung, ghiNguoiDung } from './firebase';

export const KHOA_LUU = ['air-tien-do-v1', 'air-bai-thi-v1', 'air-thuat-toan-v1', 'air-toan-v1', 'air-phong-van-v1'] as const;

export type DuLieu = Record<string, unknown>;

export function docTatCa(s: Storage | undefined = typeof localStorage === 'undefined' ? undefined : localStorage): DuLieu {
	const kq: DuLieu = {};
	for (const k of KHOA_LUU) {
		try {
			const raw = s?.getItem(k);
			if (raw) kq[k] = JSON.parse(raw);
		} catch {
			/* bỏ qua khóa hỏng */
		}
	}
	return kq;
}

export function ghiTatCa(d: DuLieu, s: Storage | undefined = typeof localStorage === 'undefined' ? undefined : localStorage): void {
	for (const k of KHOA_LUU) {
		if (!(k in d)) continue;
		try {
			s?.setItem(k, JSON.stringify(d[k]));
		} catch {
			/* đầy bộ nhớ: bỏ qua */
		}
	}
}

function laDoiTuong(x: unknown): x is Record<string, unknown> {
	return !!x && typeof x === 'object' && !Array.isArray(x);
}

/** Gộp danh sách kết quả: giữ mọi lần làm, trùng id thì lấy bản mới hơn (bên phải). */
export function tronMang(a: unknown[], b: unknown[]): unknown[] {
	const thay = new Map<string, unknown>();
	for (const x of [...a, ...b]) {
		const id = laDoiTuong(x) && 'id' in x ? String((x as Record<string, unknown>).id) : JSON.stringify(x);
		thay.set(id, x);
	}
	return [...thay.values()];
}

/** Gộp tiến độ đọc: hợp các trang đã đọc và các ngày học. */
export function tronTienDo(a: unknown, b: unknown): Record<string, unknown> {
	const x = laDoiTuong(a) ? a : {};
	const y = laDoiTuong(b) ? b : {};
	const daDoc = { ...(laDoiTuong(x.daDoc) ? x.daDoc : {}), ...(laDoiTuong(y.daDoc) ? y.daDoc : {}) };
	const ngay = [...new Set([...(Array.isArray(x.ngayHoc) ? x.ngayHoc : []), ...(Array.isArray(y.ngayHoc) ? y.ngayHoc : [])])]
		.filter((z): z is string => typeof z === 'string')
		.sort();
	return { daDoc, ngayHoc: ngay };
}

export function tronDuLieu(local: DuLieu, xa: DuLieu): DuLieu {
	const kq: DuLieu = { ...xa };
	for (const [k, v] of Object.entries(local)) {
		const cu = kq[k];
		if (k === 'air-tien-do-v1') kq[k] = tronTienDo(cu, v);
		else if (Array.isArray(v)) kq[k] = tronMang(Array.isArray(cu) ? cu : [], v);
		else if (laDoiTuong(v) && laDoiTuong(cu)) kq[k] = { ...cu, ...v };
		else if (cu === undefined) kq[k] = v;
	}
	return kq;
}

const phat = () => window.dispatchEvent(new CustomEvent('tien-do-doi'));

/** Mở trang khi đã có phiên: lấy dữ liệu tài khoản; tài khoản trống thì đẩy dữ liệu đang có lên. */
export async function taiKhiMoTrang(uid: string, hoSo?: { ten?: string; anh?: string }): Promise<void> {
	const xa = await docNguoiDung(uid);
	const local = docTatCa();
	if (xa) {
		ghiTatCa(xa);
		phat();
	} else if (Object.keys(local).length) {
		await ghiNguoiDung(uid, local, hoSo);
	}
}

/**
 * Vừa đăng nhập: nếu hai bên đều có dữ liệu thì hỏi trước khi gộp.
 * `hoiGop` trả true = gộp dữ liệu trình duyệt vào tài khoản; false = chỉ dùng dữ liệu tài khoản.
 */
export async function dongBoKhiDangNhap(
	uid: string,
	hoiGop: () => Promise<boolean>,
	hoSo?: { ten?: string; anh?: string },
): Promise<'gop' | 'tai-khoan' | 'trinh-duyet'> {
	const local = docTatCa();
	const xa = await docNguoiDung(uid);
	const coLocal = Object.keys(local).length > 0;
	const coXa = xa !== null && Object.keys(xa).length > 0;
	let ketQua: DuLieu;
	let cach: 'gop' | 'tai-khoan' | 'trinh-duyet';
	if (coLocal && coXa) {
		if (await hoiGop()) {
			ketQua = tronDuLieu(local, xa!);
			cach = 'gop';
		} else {
			ketQua = xa!;
			cach = 'tai-khoan';
		}
	} else if (coXa) {
		ketQua = xa!;
		cach = 'tai-khoan';
	} else {
		ketQua = local;
		cach = 'trinh-duyet';
	}
	ghiTatCa(ketQua);
	await ghiNguoiDung(uid, ketQua, hoSo);
	phat();
	return cach;
}

/** Ghi lên Firestore khi dữ liệu đổi; gộp nhiều lần đổi trong 1,5 giây thành một lần ghi. */
export function batDongBo(uid: string, hoSo?: { ten?: string; anh?: string }): () => void {
	let hen: number | undefined;
	let dangGhi = false;
	let choGhi = false;
	const ghi = async () => {
		if (dangGhi) {
			choGhi = true;
			return;
		}
		dangGhi = true;
		try {
			await ghiNguoiDung(uid, docTatCa(), hoSo);
		} catch {
			/* mất mạng: lần đổi sau sẽ thử lại */
		}
		dangGhi = false;
		if (choGhi) {
			choGhi = false;
			void ghi();
		}
	};
	const henGhi = () => {
		window.clearTimeout(hen);
		hen = window.setTimeout(ghi, 1500);
	};
	window.addEventListener('tien-do-doi', henGhi);
	window.addEventListener('du-lieu-doi', henGhi);
	window.addEventListener('storage', henGhi);
	return () => {
		window.clearTimeout(hen);
		window.removeEventListener('tien-do-doi', henGhi);
		window.removeEventListener('du-lieu-doi', henGhi);
		window.removeEventListener('storage', henGhi);
	};
}

export function xoaTatCaCucBo(): void {
	for (const k of KHOA_LUU) {
		try {
			localStorage.removeItem(k);
		} catch {
			/* bỏ qua */
		}
	}
	phat();
}
