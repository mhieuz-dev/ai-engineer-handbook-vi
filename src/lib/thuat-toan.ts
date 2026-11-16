import { getCollection } from 'astro:content';
import type { BaiThuatToan } from './thuat-toan-dang';

export { DANG, THU_TU_DANG } from './thuat-toan-dang';
export type { BaiThuatToan } from './thuat-toan-dang';

export async function taiBaiThuatToan(): Promise<BaiThuatToan[]> {
	const ds = await getCollection('thuatToan');
	return ds.map((e) => e.data as unknown as BaiThuatToan).sort((a, b) => a.so - b.so);
}
