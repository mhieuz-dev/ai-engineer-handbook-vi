import type { Chuong } from '../data/chuong';

export const REPO = 'https://github.com/mhieuz-dev/ai-engineer-handbook-vi';

/** Link xem notebook trên GitHub. */
export const githubNotebookUrl = (notebook: string) => `${REPO}/blob/main/notebooks/${notebook}`;
/** Link mở notebook trong Colab. */
export const colabUrl = (notebook: string) =>
	`https://colab.research.google.com/github/${REPO.replace('https://github.com/', '')}/blob/main/notebooks/${notebook}`;

export interface LuaChonTaiVe {
	nhan: string;
	/** nhãn ngắn cho cột phải */
	nhanNgan: string;
	href: string;
	/** 'in' = gọi window.print() trên trang đang đọc; 'lien-ket' = đi tới href */
	loai: 'in' | 'lien-ket';
	target?: '_blank';
}

/** Danh sách lựa chọn tải về của một chương, dùng chung cho menu và cột phải. */
export function luaChonTaiVe(chuong: Chuong): LuaChonTaiVe[] {
	const ds: LuaChonTaiVe[] = [
		{ nhan: '📄 Trang này (PDF)', nhanNgan: '📄 PDF trang này', href: '#', loai: 'in' },
		{ nhan: '📚 Cả chương (PDF)', nhanNgan: '📚 PDF cả chương', href: `/in/${chuong.slug}/?in=1`, loai: 'lien-ket' },
	];
	if (chuong.notebook) {
		ds.push({ nhan: '📓 Notebook', nhanNgan: '📓 Notebook', href: githubNotebookUrl(chuong.notebook), loai: 'lien-ket', target: '_blank' });
	}
	return ds;
}
