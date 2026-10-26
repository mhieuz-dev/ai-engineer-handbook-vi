import { CHUONG, chuongDaXuatBan } from '../data/chuong';

const MAU_TERM = /<Term\s+id\s*=\s*["']([^"']+)["']/g;

/** Các id trong `<Term id="...">`, theo thứ tự xuất hiện, không trùng. */
export function trichIdThuatNgu(mdx: string): string[] {
	const ids = new Set<string>();
	for (const m of mdx.matchAll(MAU_TERM)) ids.add(m[1]);
	return [...ids];
}

/** id thuật ngữ -> các trang dùng nó (theo thứ tự đầu vào). Bỏ trang `kiem-thu/`. */
export function dungLinkNguoc(
	trang: { id: string; body: string; title: string }[],
): Map<string, { id: string; title: string }[]> {
	const map = new Map<string, { id: string; title: string }[]>();
	for (const t of trang) {
		if (t.id.startsWith('kiem-thu/')) continue;
		for (const id of trichIdThuatNgu(t.body)) {
			const ds = map.get(id) ?? [];
			ds.push({ id: t.id, title: t.title });
			map.set(id, ds);
		}
	}
	return map;
}

/** Nhãn và đường dẫn "Học kỹ ở Chương N →". Chương chưa xuất bản thì trỏ /lo-trinh/. */
export function linkHocKy(hocKy: string, docIds: string[]): { so: number; href: string } | undefined {
	const c = CHUONG.find((x) => x.slug === hocKy);
	if (!c) return undefined;
	const daXuatBan = chuongDaXuatBan().some((x) => x.slug === hocKy);
	const trangDau = daXuatBan ? docIds.filter((id) => id.startsWith(`${hocKy}/`)).sort()[0] : undefined;
	return { so: c.so, href: trangDau ? `/${trangDau}/` : '/lo-trinh/' };
}
