import { readdirSync } from 'node:fs';
import { join } from 'node:path';
import { NHANH, PHAN, CHUONG, chuongDaXuatBan, type Chuong, type Nhanh } from '../../data/chuong';

export interface CuonSach {
	id: Nhanh['id'];
	ten: string;
	phuDe: string;
	/** Một câu giới thiệu hiện trong bảng thông tin khi chọn sách. */
	moTa: string;
	/** null khi nhánh chưa có danh mục chương. */
	tongChuong: number | null;
	daViet: number;
	/** Trang đầu đã viết; null khi sách sắp có. */
	href: string | null;
	sapCo: boolean;
	mauBia: string;
	mauChu: string;
	/** Ảnh bìa vẽ tay trong public/ (sinh bằng `scripts/bia/ve-bia.mjs`). Không có thì bìa được vẽ bằng canvas. */
	anhBia?: string;
	/** Bản WebP 360x540 của bìa cho kệ phẳng (nhẹ hơn SVG nhiều lần, điện thoại không phải tải SVG). */
	anhBiaNho?: string;
}

const GIAO_DIEN: Record<Nhanh['id'], Pick<CuonSach, 'phuDe' | 'moTa' | 'mauBia' | 'mauChu' | 'anhBia' | 'anhBiaNho'>> = {
	'ai-engineer': { phuDe: 'Từ Python đến mô hình ngôn ngữ lớn', moTa: 'Từ Python cơ bản đến Machine Learning, Deep Learning và mô hình ngôn ngữ lớn, hiểu tận gốc từng thuật toán.', mauBia: '#0E2233', mauChu: '#FBF8F1', anhBia: '/hinh/bia/ai-engineer.svg', anhBiaNho: '/hinh/bia/ai-engineer.webp' },
	robotics: { phuDe: 'Nhánh thứ hai, đang được soạn', moTa: 'Toán robot, điều khiển, phần cứng, ROS 2 và sim-to-real. Nhánh này đang được soạn.', mauBia: '#DCDFE2', mauChu: '#1F2A33', anhBia: '/hinh/bia/robotics.svg', anhBiaNho: '/hinh/bia/robotics.webp' },
};

/**
 * Trang đầu của chương, cùng quy tắc với `trangDauCuaChuong` (trang có tên nhỏ nhất theo thứ tự chữ),
 * nhưng đọc thẳng thư mục bài để chạy được ngoài Astro (unit test). Chỉ gọi lúc build.
 */
function trangDau(c: Chuong): string | null {
	const ten = readdirSync(join(process.cwd(), 'src/content/docs', c.slug))
		.filter((f) => /\.mdx?$/.test(f))
		.sort()[0];
	return ten ? `/${c.slug}/${ten.replace(/\.mdx?$/, '')}/` : null;
}

export function dsCuonSach(): CuonSach[] {
	return NHANH.map((n) => {
		const phan = new Set(PHAN.filter((p) => p.nhanh === n.id).map((p) => p.id));
		const chuong = CHUONG.filter((c) => phan.has(c.phan));
		const daViet = chuongDaXuatBan()
			.filter((c) => phan.has(c.phan))
			.sort((a, b) => a.so - b.so);
		return {
			id: n.id,
			ten: n.ten,
			tongChuong: chuong.length || null,
			daViet: daViet.length,
			href: daViet[0] ? trangDau(daViet[0]) : null,
			sapCo: daViet.length === 0,
			...GIAO_DIEN[n.id],
		};
	});
}
