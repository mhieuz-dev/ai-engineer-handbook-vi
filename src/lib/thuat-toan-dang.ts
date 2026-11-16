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
	'do-an': 'Đồ án tốt nghiệp',
};

export const THU_TU_DANG = Object.keys(DANG);

/** Lộ trình gợi ý từ dễ đến khó; bài 41 là đồ án tổng hợp, luôn cuối. */
export const LO_TRINH = [
	1, 2, 11, 14, 17, 18, 6, 7, 9, 21, 22, 24, 25, 35,
	3, 4, 5, 8, 10, 13, 15, 16, 19, 20, 23, 26, 27, 28, 29, 30, 32, 33, 36, 37, 38, 39, 40,
	12, 31, 34, 41,
];

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
	vi_sao_dung?: string;
	do_phuc_tap_chat?: string;
	goi_y: string[];
	tuong_tu: { ten: string; link: string };
}
