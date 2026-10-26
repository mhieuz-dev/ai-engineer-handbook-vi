import type { Chuong, Nhanh, Phan } from '../data/chuong';

export interface NutLink { type: 'link'; label: string; href: string; isCurrent: boolean; attrs?: { class?: string } }
export interface NutNhom { type: 'group'; label: string; entries: Nut[]; collapsed: boolean; sapCo?: number }
export interface NutSapCo { type: 'sap-co'; label: string }
export type Nut = NutLink | NutNhom | NutSapCo;

const timNhom = (cha: Nut[], nhan: string) =>
	cha.find((e): e is NutNhom => e.type === 'group' && e.label === nhan);

/** Trộn cây sidebar của Starlight (chỉ chương xong) với danh mục: chèn chương "Sắp có" theo `so`. */
export function dungCay(goc: Nut[], nhanh: Nhanh[], phan: Phan[], chuong: Chuong[]): NutNhom[] {
	return nhanh.filter((n) => phan.some((p) => p.nhanh === n.id)).map((n) => {
		const nhomNhanh = timNhom(goc, n.ten);
		const phanCon = phan.filter((p) => p.nhanh === n.id).map((p): NutNhom => {
			const nhomPhan = timNhom(nhomNhanh?.entries ?? [], p.ten);
			const cuaPhan = chuong.filter((c) => c.phan === p.id);
			const entries = cuaPhan
				.sort((a, b) => a.so - b.so)
				.map((c): Nut => {
					const nhan = `${c.so}. ${c.ten}`;
					if (c.trangThai === 'sap-co') return { type: 'sap-co', label: nhan };
					const nhomChuong = timNhom(nhomPhan?.entries ?? [], nhan);
					if (!nhomChuong) {
						throw new Error(
							`Chương ${c.so} "${c.ten}" đã xuất bản nhưng không có nhóm "${nhan}" trong sidebar Starlight. Kiểm tra thư mục ${c.slug} có trang và nhãn khớp cauHinhSidebar().`,
						);
					}
					return nhomChuong;
				});
			const sapCo = cuaPhan.filter((c) => c.trangThai === 'sap-co').length;
			return { type: 'group', label: p.ten, entries, collapsed: sapCo === cuaPhan.length, sapCo };
		});
		return { type: 'group', label: n.ten, entries: phanCon, collapsed: false };
	});
}
