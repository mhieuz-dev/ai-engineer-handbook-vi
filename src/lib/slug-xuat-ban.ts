import { getCollection } from 'astro:content';
import { chuongDaXuatBan } from '../data/chuong';

/** Id các trang thuộc chương đã xuất bản (dùng cho sidebar tiến độ và nút Đã đọc). */
export async function slugTrangDaXuatBan(): Promise<string[]> {
	const tienTo = chuongDaXuatBan().map((c) => `${c.slug}/`);
	return (await getCollection('docs'))
		.map((e) => e.id)
		.filter((id) => tienTo.some((t) => id.startsWith(t)))
		.sort();
}
