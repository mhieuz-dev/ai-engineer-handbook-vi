import { getCollection } from 'astro:content';
import { CHUONG, chuongDaXuatBan } from './chuong';
import type { Khu } from './khu';
import { taiBaiThuatToan } from '../lib/thuat-toan';
import { taiBaiToan } from '../lib/toan';
import { taiPreset } from '../lib/phong-van';

export type IconTen =
	| 'hoc'
	| 'luyen'
	| 'tra'
	| 'hoso'
	| 'route'
	| 'thi'
	| 'code'
	| 'math'
	| 'interview'
	| 'glossary'
	| 'notebook'
	| 'info'
	| 'home'
	| 'shield'
	| 'play';

export interface MucMenu {
	ten: string;
	href: string;
	mo: string;
	icon: IconTen;
}

export interface NhomMenu {
	id: Khu;
	ten: string;
	mo: string;
	items: MucMenu[];
}

/** Ba nhóm menu chính, kèm số liệu thật lấy từ dữ liệu site. */
export async function taiMenuKhu(): Promise<NhomMenu[]> {
	const daXong = chuongDaXuatBan().length;
	const soThuatToan = (await taiBaiThuatToan()).length;
	const soToan = (await taiBaiToan()).length;
	const soPhongVan = (await taiPreset()).length;
	const soThuatNgu = (await getCollection('thuatNgu')).length;
	const soNotebook = chuongDaXuatBan().filter((c) => c.notebook).length;

	return [
		{
			id: 'hoc',
			ten: 'Học',
			mo: 'Giáo trình từ Python đến mô hình ngôn ngữ lớn',
			items: [
				{ ten: 'Giáo trình AI Engineer', href: '/lo-trinh/', mo: `${daXong}/${CHUONG.length} chương`, icon: 'hoc' },
				{ ten: 'Bắt đầu từ Chương 0', href: '/ai-engineer/ch00-lo-trinh-va-colab/01-lo-trinh/', mo: 'Lộ trình và Colab', icon: 'play' },
				{ ten: 'Trang chủ', href: '/', mo: 'Chọn sách, xem học tiếp', icon: 'home' },
				{ ten: 'Robotics', href: '/lo-trinh/', mo: 'Sắp có', icon: 'route' },
			],
		},
		{
			id: 'luyen',
			ten: 'Luyện tập',
			mo: 'Thi thử, thuật toán, toán nền và phỏng vấn',
			items: [
				{ ten: 'Tất cả cách luyện', href: '/luyen-tap/', mo: 'Hub luyện tập', icon: 'luyen' },
				{ ten: 'Phòng thi thử', href: '/phong-thi/', mo: 'Theo chương hoặc chủ đề', icon: 'thi' },
				{ ten: 'Luyện thuật toán', href: '/thuat-toan/', mo: `${soThuatToan} bài + đồ án`, icon: 'code' },
				{ ten: 'Toán cho thuật toán', href: '/toan-thuat-toan/', mo: `${soToan} bài nền`, icon: 'math' },
				{ ten: 'Phỏng vấn thử', href: '/phong-van/', mo: `${soPhongVan} phong cách`, icon: 'interview' },
			],
		},
		{
			id: 'tra',
			ten: 'Tra cứu',
			mo: 'Từ điển, notebook và thông tin site',
			items: [
				{ ten: 'Thuật ngữ', href: '/thuat-ngu/', mo: `${soThuatNgu} khái niệm`, icon: 'glossary' },
				{ ten: 'Notebook', href: '/notebook/', mo: `${soNotebook} notebook Colab`, icon: 'notebook' },
				{ ten: 'Giới thiệu', href: '/gioi-thieu/', mo: 'Về site, tác giả, báo lỗi', icon: 'info' },
				{ ten: 'Quyền riêng tư', href: '/quyen-rieng-tu/', mo: 'Dữ liệu của bạn', icon: 'shield' },
			],
		},
	];
}
