import { getCollection } from 'astro:content';
import { chuongDaXuatBan, type Chuong } from '../data/chuong';

/** Đường dẫn trang đầu tiên của một chương (theo thứ tự tên file), vd `/ai-engineer/ch10-.../01-truc-giac/`. */
export async function trangDauCuaChuong(c: Chuong): Promise<string | undefined> {
	const id = (await getCollection('docs')).map((e) => e.id).filter((i) => i.startsWith(`${c.slug}/`)).sort()[0];
	return id ? `/${id}/` : undefined;
}

/** Trang đầu của chương đã xuất bản có số nhỏ nhất. */
export async function trangBatDauHoc(): Promise<string | undefined> {
	const c = [...chuongDaXuatBan()].sort((a, b) => a.so - b.so)[0];
	return c ? trangDauCuaChuong(c) : undefined;
}
