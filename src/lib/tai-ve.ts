import type { Chuong } from '../data/chuong';

export const REPO = 'https://github.com/mhieuz-dev/ai-engineer-handbook-vi';

export interface LuaChonTaiVe {
	nhan: string;
	href: string;
	/** 'in' = gọi window.print() trên trang đang đọc; 'lien-ket' = đi tới href */
	loai: 'in' | 'lien-ket';
	target?: '_blank';
}

/** Danh sách lựa chọn tải về của một chương, dùng chung cho menu và cột phải. */
export function luaChonTaiVe(chuong: Chuong): LuaChonTaiVe[] {
	const ds: LuaChonTaiVe[] = [
		{ nhan: '📄 Trang này (PDF)', href: '#', loai: 'in' },
		{ nhan: '📚 Cả chương (PDF)', href: `/in/${chuong.slug}/?in=1`, loai: 'lien-ket' },
	];
	if (chuong.notebook) {
		ds.push({ nhan: '📓 Notebook', href: `${REPO}/blob/main/notebooks/${chuong.notebook}`, loai: 'lien-ket', target: '_blank' });
	}
	return ds;
}
