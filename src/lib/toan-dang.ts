/** Dữ liệu thuần cho client (không đụng astro:content). */

export const MODULE_TOAN: Record<string, string> = {
	'do-phuc-tap': 'Độ phức tạp và đệ quy',
	'chung-minh': 'Chứng minh đúng',
	'xac-suat': 'Xác suất trong thuật toán',
	'dai-so': 'Đại số tuyến tính cho ML',
	'toi-uu': 'Tối ưu và hàm lồi',
	'do-an': 'Đồ án toán',
};

export const THU_TU_MODULE = Object.keys(MODULE_TOAN);

export interface BaiToan {
	so: number;
	ten: string;
	module: string;
	loai: 'code' | 'chung-minh';
	muc: 'de' | 'vua' | 'kho';
	de: string;
	goi_y: string[];
	khung?: string;
	test_vi_du?: string;
	test_an?: string;
	loi_giai: string;
	chung_minh?: string;
	phuc_tap?: string;
	rubric?: { y: string; diem: number }[];
	lien_quan: { ten: string; trang: string }[];
}
