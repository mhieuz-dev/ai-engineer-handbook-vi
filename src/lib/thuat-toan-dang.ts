/** Dữ liệu thuần (không đụng astro:content) để client import an toàn. */

export const DANG: Record<string, string> = {
	'mang-bang-bam': 'Mảng và bảng băm',
	'hai-con-tro': 'Hai con trỏ',
	'cua-so-truot': 'Cửa sổ trượt',
	'ngan-xep': 'Ngăn xếp',
	'tim-kiem-nhi-phan': 'Tìm kiếm nhị phân',
	'danh-sach-lien-ket': 'Danh sách liên kết',
	cay: 'Cây',
	'do-thi': 'Đồ thị BFS/DFS',
	heap: 'Heap',
	'quy-hoach-dong': 'Quy hoạch động',
	'quay-lui': 'Quay lui',
	'tham-lam': 'Tham lam / khoảng',
};

export const THU_TU_DANG = Object.keys(DANG);

export interface BaiThuatToan {
	so: number;
	ten: string;
	dang: string;
	muc: 'de' | 'vua' | 'kho';
	de: string;
	vi_du: { vao: string; ra: string }[];
	rang_buoc: string[];
	khung: string;
	test_vi_du: string;
	test_an: string;
	loi_giai: string;
	phuc_tap: string;
	goi_y: string[];
	tuong_tu: { ten: string; link: string };
}
