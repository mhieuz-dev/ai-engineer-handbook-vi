import { readdirSync } from 'node:fs';
import { join } from 'node:path';
import { NHANH, PHAN, CHUONG, chuongDaXuatBan, type Chuong, type Nhanh } from '../../data/chuong';

export interface CuonSach {
	id: Nhanh['id'];
	ten: string;
	phuDe: string;
	/** null khi nhánh chưa có danh mục chương. */
	tongChuong: number | null;
	daViet: number;
	/** Trang đầu đã viết; null khi sách sắp có. */
	href: string | null;
	sapCo: boolean;
	mauBia: string;
	mauChu: string;
	/** Ảnh bìa trong public/ (vd `/hinh/bia/ai-engineer.webp`). Không có thì bìa được vẽ bằng canvas. */
	anhBia?: string;
}

const GIAO_DIEN: Record<Nhanh['id'], Pick<CuonSach, 'phuDe' | 'mauBia' | 'mauChu' | 'anhBia'>> = {
	'ai-engineer': { phuDe: 'Từ Python đến mô hình ngôn ngữ lớn', mauBia: '#0E2233', mauChu: '#FBF8F1', anhBia: undefined },
	robotics: { phuDe: 'Nhánh thứ hai, đang được soạn', mauBia: '#DCDFE2', mauChu: '#1F2A33', anhBia: undefined },
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
