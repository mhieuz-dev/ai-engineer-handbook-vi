export type Khu = 'hoc' | 'luyen' | 'tra' | 'hoso';

export const KHU: Record<Khu, { ten: string; mau: string; moTa: string }> = {
	hoc: { ten: 'Học', mau: 'var(--khu-hoc)', moTa: 'Giáo trình và lộ trình' },
	luyen: { ten: 'Luyện tập', mau: 'var(--khu-luyen)', moTa: 'Thi, thuật toán, toán, phỏng vấn' },
	tra: { ten: 'Tra cứu', mau: 'var(--khu-tra)', moTa: 'Thuật ngữ, notebook, giới thiệu' },
	hoso: { ten: 'Hồ sơ', mau: 'var(--khu-hoso)', moTa: 'Tiến độ và kết quả của bạn' },
};

/** Khu của một đường dẫn, dùng cho menu, nhãn đầu trang và màu nhấn. */
export function khuCuaDuongDan(path: string): Khu {
	const p = path.split('?')[0].split('#')[0];
	if (p === '/' || p.startsWith('/ai-engineer') || p.startsWith('/lo-trinh')) return 'hoc';
	if (p.startsWith('/ho-so')) return 'hoso';
	if (p.startsWith('/thuat-ngu') || p.startsWith('/notebook') || p.startsWith('/gioi-thieu') || p.startsWith('/quyen-rieng-tu')) return 'tra';
	if (
		p.startsWith('/luyen-tap') ||
		p.startsWith('/phong-thi') ||
		p.startsWith('/thuat-toan') ||
		p.startsWith('/toan-thuat-toan') ||
		p.startsWith('/phong-van')
	)
		return 'luyen';
	return 'hoc';
}
